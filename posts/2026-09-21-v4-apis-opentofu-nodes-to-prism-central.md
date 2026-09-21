---
title: Nutanix v4 APIs and OpenTofu — from imaged nodes to Prism Central, as code
date: 2026-09-21
time: 09:00
by: Alex Alvord
slug: v4-apis-opentofu-nodes-to-prism-central
section: nutanix
draft: true
summary: The v4 APIs gave the Nutanix OpenTofu/Terraform provider a real day-zero story. One walkthrough, six steps, ASCII at every step — cluster, Prism Central (the multicluster manager), registration, a second cluster, network, and the first VM — with nothing typed into a console after Foundation.
---

Until the v4 APIs, "Nutanix as code" started on day one, not day zero. You could build VMs, subnets and categories from Terraform all day, but the multicluster manager — Prism Central — was a wizard you clicked through, and a new cluster still meant Foundation, then a browser. Version 2 of the Nutanix provider is built on the v4 APIs and closes that gap: Prism Central deploys from a resource, clusters register from a resource, a second cluster forms from unconfigured nodes from a resource. This is the whole path, once, with a picture at every step.

Everything below is from the public provider docs and examples ([github.com/nutanix/terraform-provider-nutanix](https://github.com/nutanix/terraform-provider-nutanix)), run with OpenTofu. Substitute Terraform if that's your shop; the HCL is identical.

## The map

```text
 laptop ─── tofu ───┐
                    │  step 2 (only)           steps 3–6
                    ▼                             ▼
          ┌──────────────────┐        ┌──────────────────────┐
          │ Prism Element    │  ───▶  │ Prism Central        │
          │ cluster VIP:9440 │ deploy │ the multicluster mgr │
          │ (Foundation-made)│        │ :9440                │
          └──────────────────┘        └──────────┬───────────┘
                                                 │ manages
                              ┌──────────────────┼──────────────────┐
                              ▼                  ▼                  ▼
                        ┌──────────┐      ┌────────────┐     ┌───────────┐
                        │ cluster1 │      │ cluster2   │     │ subnets,  │
                        │ (step 3) │      │ (step 4)   │     │ VMs (5–6) │
                        └──────────┘      └────────────┘     └───────────┘
```

Two endpoints, one code base. The Prism Central deploy is the only call that goes to Prism Element; everything after it goes to Prism Central. The provider handles that with two aliases.

## What v4 changed, in one paragraph

The v4 APIs are namespaced (`clustermgmt`, `vmm`, `networking`, `prism`, and so on), every object has an `ext_id` instead of a UUID-in-a-metadata-block, writes are guarded by ETags so a stale plan can't clobber a newer change, and long operations return a task you can follow. The provider's `_v2` resources map one-to-one onto those namespaces. The legacy `v0.8`/`v1`/`v2`-API resources still work but are on notice — the provider's docs say the deprecation lands in the Q4 CY2026 release — so new code should be `_v2` only.

## Step 0 — toolchain

```text
 ┌─ laptop ──────────────────────────────────────────────┐
 │  tofu 1.x                                             │
 │  provider  nutanix/nutanix  2.4.2   (v4 API based)    │
 │  env  NUTANIX_USERNAME  NUTANIX_PASSWORD              │
 │  files  versions.tf  providers.tf  vars.tf  *.tf      │
 └───────────────────────────────────────────────────────┘
```

The provider is on the OpenTofu registry (it pulls the release binary from GitHub), so `tofu init` needs no mirror configuration.

```hcl
# versions.tf
terraform {
  required_version = ">= 1.6"
  required_providers {
    nutanix = {
      source  = "nutanix/nutanix"
      version = "2.4.2"
    }
  }
}
```

```hcl
# providers.tf — two endpoints, same credentials pattern
provider "nutanix" {
  alias        = "pe"
  endpoint     = var.pe_vip        # cluster virtual IP, Prism Element
  port         = 9440
  insecure     = var.lab           # true only in a lab with self-signed certs
  wait_timeout = 10
}

provider "nutanix" {
  alias        = "pc"
  endpoint     = var.pc_ip         # the Prism Central you are about to create
  port         = 9440
  insecure     = var.lab
  wait_timeout = 10
}
```

Username and password are not in the files. The provider reads `NUTANIX_USERNAME` and `NUTANIX_PASSWORD` from the environment; put them there from your vault. Version 2.4.2 also accepts an API key instead of a password — better for a pipeline runner — but the walkthrough uses the local admin because that is what a fresh cluster has.

```text
 $ export NUTANIX_USERNAME=admin
 $ export NUTANIX_PASSWORD=$(vault read ...)      # never in a .tf, never in state
 $ tofu init
   Initializing provider plugins...
   - Installing nutanix/nutanix v2.4.2...
   OpenTofu has been successfully initialized!
```

Compatibility matters here: provider 2.4.2 is matched to AOS 7.5 and Prism Central 7.5 or later. Older AOS, older provider; the matrix is on the provider's index page.

## Step 1 — Foundation, the one thing that is not code

```text
 ┌─────────┐ ┌─────────┐ ┌─────────┐          ┌─────────────────────┐
 │ node A  │ │ node B  │ │ node C  │  ─────▶  │ cluster1  (AOS 7.5) │
 │ bare    │ │ bare    │ │ bare    │Foundation│ CVM IPs, VIP, admin │
 └─────────┘ └─────────┘ └─────────┘          └─────────────────────┘
```

Foundation images the hypervisor and CVMs and forms the first cluster. It is an ISO, a network, and a coffee. It has an API too (the provider ships legacy Foundation and Foundation Central resources), but keep it out of this state file: it runs once per rack, from a different network position, with different credentials. Everything from here on is `tofu apply`.

Two things Foundation leaves behind that matter: the cluster VIP (your `var.pe_vip`) and the default admin password, which must be changed before a registration call will succeed — the provider's own cluster example does this with a `local-exec` running `ncli user reset-password`. Do it once, by hand or by that provisioner, and never bake the result into a file.

## Step 2 — deploy Prism Central, from Prism Element

This is the step that used to be a wizard. `nutanix_pc_deploy_v2` is an action resource: it runs once, takes a long time, and update/delete are no-ops (destroy and re-apply to run it again). It is called on the cluster, so it uses the `pe` alias.

```text
        ┌──────────────────┐   POST /prism/v4 … deploy   ┌──────────────────┐
 tofu ─▶│ Prism Element    │ ─────────────────────────▶  │ Prism Central VM │
        │ cluster1 VIP     │   task … (60–120 min)       │ STARTER, 1 node  │
        └──────────────────┘ ◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │ pc_ip on vlan-mgmt│
                                  ext_id, task done       └──────────────────┘
```

```hcl
# pc.tf
data "nutanix_subnets_v2" "mgmt" {
  provider = nutanix.pe
  filter   = "name eq '${var.mgmt_subnet_name}'"
}

resource "nutanix_pc_deploy_v2" "pc" {
  provider = nutanix.pe

  timeouts {
    create = "120m"        # the docs are explicit: raise this, the default is not enough
  }

  config {
    build_info {
      version = var.pc_version   # the build string as the cluster lists it, e.g. "pc.2024.3" in the docs
    }
    size = "STARTER"             # STARTER | SMALL | LARGE | EXTRALARGE
    name = "pc-lab"
  }

  network {
    external_networks {
      network_ext_id = data.nutanix_subnets_v2.mgmt.subnets[0].ext_id
      default_gateway { ipv4 { value = var.mgmt_gateway } }
      subnet_mask     { ipv4 { value = var.mgmt_mask } }
      ip_ranges {
        begin { ipv4 { value = var.pc_ip } }
        end   { ipv4 { value = var.pc_ip } }   # one IP: a single-node PC
      }
    }
    name_servers { ipv4 { value = var.dns1 } }
    name_servers { ipv4 { value = var.dns2 } }
    ntp_servers  { fqdn { value = "0.pool.ntp.org" } }
    ntp_servers  { fqdn { value = "1.pool.ntp.org" } }
  }

  # should_enable_high_availability = true   # scale-out (3 VMs); give ip_ranges three addresses
}
```

`tofu apply -target=nutanix_pc_deploy_v2.pc` and go do something else. When it returns, Prism Central answers at `var.pc_ip` and the `pc` alias is live.

## Step 3 — register the cluster with Prism Central

A cluster that is not registered is invisible to the `pc` alias, and the v4 cluster APIs (add node, categories, profiles) need the registration. `nutanix_pc_registration_v2` runs on Prism Central and reaches out to the cluster.

```text
        ┌──────────────────┐   register(cluster1 VIP, admin)   ┌────────────┐
 tofu ─▶│ Prism Central    │ ───────────────────────────────▶  │ cluster1   │
        │ pc_ext_id        │ ◀ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │ registered │
        └──────────────────┘                                   └────────────┘
```

```hcl
# register.tf
data "nutanix_clusters_v2" "pc_self" {
  provider   = nutanix.pc
  filter     = "config/clusterFunction/any(t:t eq Clustermgmt.Config.ClusterFunctionRef'PRISM_CENTRAL')"
  depends_on = [nutanix_pc_deploy_v2.pc]
}

locals {
  pc_ext_id = data.nutanix_clusters_v2.pc_self.cluster_entities[0].ext_id
}

resource "nutanix_pc_registration_v2" "cluster1" {
  provider  = nutanix.pc
  pc_ext_id = local.pc_ext_id

  remote_cluster {
    aos_remote_cluster_spec {
      remote_cluster {
        address { ipv4 { value = var.pe_vip } }
        credentials {
          authentication {
            username = var.pe_username
            password = var.pe_password   # marked sensitive; lives in the environment
          }
        }
      }
    }
  }
}
```

That filter string is OData against the v4 `clustermgmt` namespace — the same filters work on the raw API, which is the point of v4: what the provider does, `curl` can do.

## Step 4 — a second cluster, from unconfigured nodes, without Foundation

This is the part v4 made possible from code. Nodes that Foundation imaged but did not cluster show up as unconfigured; Prism Central can discover them and form a cluster from them.

```text
 ┌─────────┐ ┌─────────┐ ┌─────────┐   discover     ┌──────────────────┐
 │ node D  │ │ node E  │ │ node F  │ ◀───────────── │ Prism Central    │
 │ imaged, │ │ imaged, │ │ imaged, │   create ───▶  │ cluster2 formed  │
 │unclustrd│ │unclustrd│ │unclustrd│   register ──▶ │ and registered   │
 └─────────┘ └─────────┘ └─────────┘                └──────────────────┘
```

```hcl
# cluster2.tf
# a data source: it asks Prism Central what it can see, and fails the plan if a node is missing
data "nutanix_clusters_discover_unconfigured_nodes_v2" "c2" {
  provider     = nutanix.pc
  ext_id       = local.pc_ext_id
  address_type = "IPV4"
  dynamic "ip_filter_list" {
    for_each = var.cluster2_cvm_ips
    content { ipv4 { value = ip_filter_list.value } }
  }
}

resource "nutanix_cluster_v2" "c2" {
  provider   = nutanix.pc
  name       = "cluster2"
  depends_on = [data.nutanix_clusters_discover_unconfigured_nodes_v2.c2]

  nodes {
    dynamic "node_list" {
      for_each = var.cluster2_cvm_ips
      content { controller_vm_ip { ipv4 { value = node_list.value } } }
    }
  }
  config {
    cluster_function  = ["AOS"]
    redundancy_factor = 2
    cluster_arch      = "X86_64"
    fault_tolerance_state { domain_awareness_level = "NODE" }
  }
  network {
    external_address          { ipv4 { value = var.cluster2_vip } }
    external_data_services_ip { ipv4 { value = var.cluster2_dsip } }
    ntp_server_ip_list { fqdn { value = "0.pool.ntp.org" } }
  }
}

resource "nutanix_pc_registration_v2" "cluster2" {
  provider  = nutanix.pc
  pc_ext_id = local.pc_ext_id
  remote_cluster {
    aos_remote_cluster_spec {
      remote_cluster {
        address { ipv4 { value = var.cluster2_vip } }
        credentials { authentication { username = var.pe_username, password = var.pe_password } }
      }
    }
  }
  depends_on = [nutanix_cluster_v2.c2]
}
```

Same password caveat as step 1: a freshly formed cluster has the default admin password until something changes it, and registration needs the changed one. The provider example uses a `local-exec` between create and register; a pipeline should do the same or have Foundation set it.

## Step 5 — network

```text
 Prism Central
   └── cluster1
        └── vlan-112  192.168.112.0/24   gw .1   pool .20–.200   (VLAN, external)
```

```hcl
# network.tf
data "nutanix_clusters_v2" "c1" {
  provider   = nutanix.pc
  filter     = "name eq '${var.cluster1_name}'"
  depends_on = [nutanix_pc_registration_v2.cluster1]
}

resource "nutanix_subnet_v2" "vlan112" {
  provider          = nutanix.pc
  name              = "vlan-112"
  cluster_reference = data.nutanix_clusters_v2.c1.cluster_entities[0].ext_id
  subnet_type       = "VLAN"
  network_id        = 112
  is_external       = true
  ip_config {
    ipv4 {
      ip_subnet {
        ip { value = "192.168.112.0" }
        prefix_length = 24
      }
      default_gateway_ip { value = "192.168.112.1" }
      pool_list {
        start_ip { value = "192.168.112.20" }
        end_ip   { value = "192.168.112.200" }
      }
    }
  }
}
```

## Step 6 — the first VM, and categories so day two has handles

```text
 ┌─ vm-web-01 ───────────────────────────┐
 │ 2 vCPU · 4 GiB · disk 40 GiB (SCSI 0) │   categories: environment=lab
 │ nic → vlan-112 (pool)                 │               owner=platform
 │ boot: UEFI  disk → network            │
 └───────────────────────────────────────┘
```

```hcl
# vm.tf
resource "nutanix_category_v2" "env_lab" {
  provider = nutanix.pc
  key      = "environment"
  value    = "lab"
}

data "nutanix_storage_containers_v2" "c1_default" {
  provider = nutanix.pc
  filter   = "clusterExtId eq '${data.nutanix_clusters_v2.c1.cluster_entities[0].ext_id}'"
}

resource "nutanix_virtual_machine_v2" "web01" {
  provider             = nutanix.pc
  name                 = "vm-web-01"
  num_sockets          = 2
  num_cores_per_socket = 1
  memory_size_bytes    = 4 * 1024 * 1024 * 1024

  cluster { ext_id = data.nutanix_clusters_v2.c1.cluster_entities[0].ext_id }

  categories { ext_id = nutanix_category_v2.env_lab.id }

  disks {
    disk_address { bus_type = "SCSI", index = 0 }
    backing_info {
      vm_disk {
        disk_size_bytes = 40 * 1024 * 1024 * 1024
        storage_container { ext_id = data.nutanix_storage_containers_v2.c1_default.storage_containers[0].ext_id }
      }
    }
  }

  nics {
    nic_network_info {
      virtual_ethernet_nic_network_info {
        nic_type = "NORMAL_NIC"
        subnet { ext_id = nutanix_subnet_v2.vlan112.id }
      }
    }
  }

  boot_config {
    uefi_boot { boot_order = ["DISK", "NETWORK"] }
  }

  power_state = "ON"
}
```

## The whole run

```text
 $ tofu apply
   nutanix_pc_deploy_v2.pc                          creating...  [1h47m elapsed]  ✔
   nutanix_pc_registration_v2.cluster1              creating...  [2m10s]          ✔
   nutanix_cluster_v2.c2                            creating...  [31m]            ✔
   nutanix_pc_registration_v2.cluster2              creating...  [2m]             ✔
   nutanix_category_v2.env_lab                      creating...  [1s]             ✔
   nutanix_subnet_v2.vlan112                        creating...  [4s]             ✔
   nutanix_virtual_machine_v2.web01                 creating...  [18s]            ✔

   Apply complete! Resources: 7 added, 0 changed, 0 destroyed.

 $ tofu plan
   No changes. Your infrastructure matches the configuration.
```

That last line is the deliverable. Not the VM — the fact that a second `plan` is empty, which means the multicluster manager, both clusters, the network and the workload are now described by files in git and reconcilable against reality. Change a VLAN in the file, `plan` shows the diff, `apply` makes it so, and the ETag on every v4 write means a colleague's click in the UI five minutes ago turns into a plan diff instead of a silent overwrite.

## What to watch

- **Two endpoints, one state.** Step 2 uses the `pe` alias; everything else uses `pc`. Keep that boundary in the file names and you will never wonder which credential a resource used.
- **Action resources don't reconcile.** `pc_deploy_v2` runs once; a change to it is a destroy-and-recreate of the resource record, not of Prism Central. Read the resource's note before you edit it in place.
- **Passwords.** The default admin password blocks registration; the provider's own examples reset it with `ncli` from a provisioner. Decide where that happens — Foundation, a provisioner, or a person — before the pipeline runs unattended.
- **Version pinning is real.** Provider 2.4.2 ↔ AOS 7.5 / PC 7.5. The matrix is on the provider's index page; mismatches fail late, inside a 120-minute apply.
- **Sensitive values.** `pe_password`, `pc` credentials and user keys are marked sensitive by the provider as of 2.4.2, but state still holds them. Encrypt the state backend as you would any other.

Source for every resource above: the provider's `website/docs/r/*_v2.html.markdown` and `examples/*_v2/main.tf` on GitHub. If a block here disagrees with those on your version, the docs win — file names change faster than blog posts.
