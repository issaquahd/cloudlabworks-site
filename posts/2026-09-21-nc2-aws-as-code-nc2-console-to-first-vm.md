---
title: NC2 on AWS, as code: the NC2 console to the first VM with the v4 APIs and OpenTofu
date: 2026-09-21
time: 07:00
by: Alex Alvord
slug: nc2-aws-as-code-nc2-console-to-first-vm
section: nutanix
draft: true
summary: Nutanix Cloud Clusters on AWS has no Prism Element to log into: with Flow Virtual Networking you are Prism Central–bound from the first minute. One walkthrough, ASCII at every step: onboarding the AWS account in the NC2 console, the URLs and ports to allowlist, the cluster and Prism Central in one create, then OpenTofu on the v4 APIs for VPCs, subnets, floating IPs and the first VM.
---

The first time I stood up NC2 on AWS, I went looking for Prism Element. Habit. Fifteen years of clusters will do that to you. It wasn't there, and that was the whole lesson: with Flow Virtual Networking you are Prism Central-bound from the first minute. The NC2 console builds the cluster *and* Prism Central in one create, and everything after that (VPCs, subnets, images, VMs) is a Prism Central v4 API call. Which is exactly what the version 2 OpenTofu/Terraform provider speaks.

So the build has two halves. The first is the NC2 console: a UI where you onboard a cloud account, pick a region and instance type, and press Create. It replaces the manual AWS and Nutanix setup that used to eat a day. The second half is code, and it's the fun half. Here is the whole path, once, with a picture at every step, because that is what I wished someone had drawn for me. Everything below comes from the public NC2 on AWS Deployment and User Guide and the provider's docs and `examples/nc2` samples on GitHub, run with OpenTofu. If Terraform is your shop, swap the binary; the HCL is identical.

## The map

```text
 ┌─ NC2 console (cloud.nutanix.com) ─────────────────────────────────────┐
 │  1. org ─▶ 2. AWS cloud account (CloudFormation) ─▶ 3. Create Cluster │
 │                                                    + Prism Central    │
 └───────────────────────────────┬───────────────────────────────────────┘
                                 │ orchestrates, over TCP/443
                                 ▼
 ┌─ AWS account · region · AZ ───────────────────────────────────────────┐
 │  VPC                                                                  │
 │   ├─ management subnet (private)  ── bare-metal nodes  ── cluster     │
 │   ├─ Prism Central subnet  /28    ── PC VM(s)  ◀── you talk to this   │
 │   └─ Flow Virtual Networking /24  ── transit-vpc, external subnets    │
 └───────────────────────────────┬───────────────────────────────────────┘
                                 │ v4 APIs, :9440
                                 ▼
 ┌─ laptop ─ tofu ─ one provider, one endpoint: Prism Central ───────────┐
 │  4. VPC + overlay subnets  5. default route  6. image + VM + FIP      │
 └───────────────────────────────────────────────────────────────────────┘
```

No Prism Element in the picture. It's there (the CVMs are running) but nothing you do touches it, and that took me a minute to trust.

## Step 1: before the NC2 console: the AWS side

```text
 AWS account
   ├─ IAM user with IAMFullAccess + AWSCloudFormationFullAccess   (to run the stack, once)
   ├─ vCPU quota for the bare-metal type, n+1 nodes               (Service Quotas console)
   └─ region enabled                                              (some are opt-in)
```

Three things, none of them Nutanix. The IAM permissions are only for running a CloudFormation stack that creates NC2's roles; NC2 itself never uses them, which is the first question your security team will ask, so have the answer ready. The quota is counted in vCPUs at 2 per physical core and must cover one more node than you deploy, because a node replacement runs n+1 for a while.

## Step 2: onboard the cloud account in the NC2 console

This is the step that used to be a runbook, and I have written that runbook more than once. The NC2 console generates a CloudFormation template scoped to the features you tick, you create the stack in your AWS account, and it verifies the roles it can now assume.

```text
 NC2 console                                 AWS console
 ┌───────────────────────────┐              ┌──────────────────────────────┐
 │ Organizations ▸ <org>     │              │ CloudFormation ▸ Quick create│
 │  Cloud Accounts ▸ Add     │  template    │  stack: Nutanix-Clusters-    │
 │   provider: amazon        │ ──URL──────▶ │   High-Nc2-Cloud-Stack-Prod  │
 │   account id: 123456789012│              │  ☑ may create IAM resources  │
 │   features: ☑ FVN ☑ …     │              │  Create ─▶ CREATE_COMPLETE   │
 │  [Verify credentials] ◀───│──────────────│  roles: …Nc2-Cluster-Role,   │
 │  regions: us-west-2       │              │         …Nc2-Orchestrator-   │
 │  [Add Account]  ─▶ R      │              │         Role-Prod            │
 └───────────────────────────┘              └──────────────────────────────┘
```

Click path, from the guide: sign in at cloud.nutanix.com → Organizations → your org → Cloud Accounts → Add Cloud Account → provider `amazon`, a name, the 12-digit account ID without hyphens → select features → Generate CloudFormation Template → Open AWS Console → Quick create stack, acknowledge IAM, Create → wait for `CREATE_COMPLETE` → back in the NC2 console, Verify credentials → choose regions → Add Account. Status `R` means ready.

Two things worth knowing. The template is per-feature: turn on Flow Virtual Networking, Cluster Protect or dedicated hosts later and you re-run the stack so the roles gain the permissions. And the stack is the one part of this half that *is* code, the template URL the NC2 console hands you can be applied from `aws cloudformation create-stack` or an OpenTofu `aws_cloudformation_stack` resource, which is how you keep the roles in git.

## Step 3: what the cluster must reach: the allowlist

The NC2 console has its own set of endpoints, and a cluster that can't reach them never finishes forming. From the guide's Ports and Endpoints page, outbound from the management subnet, all TCP/443:

```text
 management subnet ──▶ gateway-external-api.cloud.nutanix.com/*   NC2 orchestration (this is the NC2 console)
                  ──▶ downloads.cloud.nutanix.com/clusters/*      NC2 RPMs
                  ──▶ portal.nutanix.com/*                        service portal
                  ──▶ licensing-api.nutanix.com                   licensing
                  ──▶ download.nutanix.com/*                      LCM upgrades
                  ──▶ insights.nutanix.com/*                      Pulse
                  ──▶ 169.254.169.123                             AWS Time Sync
                  ──▶ ec2.<region>.amazonaws.com/*                EC2 metadata (e.g. ec2.us-west-2.amazonaws.com)
```

Nutanix publishes names, not IPs: the destinations sit behind DNS failover, so an IP allowlist rots. I have watched a cluster sit at "Creating" for an hour over exactly this. If the management subnet has no route out (no NAT gateway, or an egress firewall), this table is the first thing to check, and the guide is explicit that it is not exhaustive: Prism Central and the microservices platform have their own port lists.

Inbound, the user-management security group opens 22, 80, 9440, 8443 and the DR/NGT/Files ports by default; 9440 is the one you will use from the laptop.

## Step 4: Create Cluster, with Prism Central inside it

One wizard, and Prism Central comes out the other side. Still feels like cheating. The parts that matter are on the Network and Prism Central tabs.

```text
 Create Cluster
 ├─ General    name · organization · cloud account · region + AZ · license tier · AOS version
 ├─ Capacity   host type · number of hosts (3 – 28) · redundancy · EBS (optional)
 ├─ Network    ○ create a new VPC (CIDR)  ● use existing VPC + management subnet
 │             ☑ Enable Flow Virtual Networking on this cluster   ◀── decide now; can't add later
 │             access policy: management services / UVMs (security groups)
 ├─ Prism Central   (appears only with FVN ticked)
 │             ● deploy a new Prism Central on this cluster
 │               size Small | Large | X-large · PC version · PC subnet /28 · FVN subnet /24 · NTP
 │             ○ register to an existing Prism Central (same account + AZ, scale-out, healthy)
 └─ Summary    quota check ─▶ Create ─▶ Creating … Running   (~30 min)
```

The constraints, from the guide: at least three nodes; the VPC's primary CIDR, never 192.168.5.0/24 (CVM-to-hypervisor traffic lives there); the Prism Central subnet must not overlap the management subnet; the Flow subnet must be at least a /24 and overlap neither. Flow Virtual Networking can only be enabled at create time. And the first credential on the new Prism Central is the documented default, change it before anything else, and never write the replacement into a file.

When the status turns Running you have a cluster, a Prism Central, a `transit-vpc`, and an `overlay-external-subnet-nat` (plus a no-NAT one if you chose that path); all built by the NC2 console, none of it by hand. That Prism Central address is the only endpoint the rest of this post talks to.

## Step 5: toolchain, one endpoint

```text
 ┌─ laptop ──────────────────────────────────────────────────┐
 │  tofu 1.x                                                 │
 │  provider  nutanix/nutanix  2.4.2   (v4 API based)        │
 │  endpoint  Prism Central  :9440    (the whole list)       │
 │  env  NUTANIX_USERNAME  NUTANIX_PASSWORD                  │
 └───────────────────────────────────────────────────────────┘
```

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

# providers.tf: one provider, pointed at Prism Central. No PE alias; there is nothing to point it at.
provider "nutanix" {
  endpoint     = var.pc_endpoint     # Prism Central IP or FQDN from the NC2 console
  port         = 9440
  insecure     = var.lab             # only until a real certificate is on PC
  wait_timeout = 10
}
```

The provider is on the OpenTofu registry (it pulls the release binary from GitHub), so `tofu init` needs nothing extra. Username and password come from `NUTANIX_USERNAME` / `NUTANIX_PASSWORD` in the environment; 2.4.2 also takes an API key, which is the better fit for a pipeline. The provider's own NC2 samples were tested on NC2 with pc.2024.3.1.1 / AOS 10.0.1; the 2.4.x line targets PC 7.5, match the provider to the PC version the NC2 console deployed.

```text
 $ export NUTANIX_USERNAME=admin NUTANIX_PASSWORD=$(vault read …)
 $ tofu init
   - Installing nutanix/nutanix v2.4.2...
   OpenTofu has been successfully initialized!
```

## Step 6: a Flow VPC with NAT egress

The NC2 console built the transit VPC and the external NAT subnet. Your VPC hangs off that subnet; your overlay subnets hang off your VPC. The AWS-side `.2` resolver is the DNS to hand out; the provider sample derives it from the Prism Central address.

```text
 transit-vpc (NC2-built)
   └─ overlay-external-subnet-nat (NC2-built)  ◀── external subnet for:
        └─ vpc-app  (yours)
             ├─ app-web  192.168.10.0/24  gw .1  pool .10–.200  dns 10.x.0.2
             └─ app-db   192.168.20.0/24  gw .1  pool .10–.200
             └─ route  0.0.0.0/0 ─▶ overlay-external-subnet-nat
```

```hcl
# network.tf
data "nutanix_subnets_v2" "ext_nat" {
  filter = "name eq 'overlay-external-subnet-nat'"
}

resource "nutanix_vpc_v2" "app" {
  name        = "vpc-app"
  description = "application VPC, NAT egress via the NC2 transit VPC"
  external_subnets {
    subnet_reference = data.nutanix_subnets_v2.ext_nat.subnets[0].ext_id
  }
}

locals {
  # AWS resolver is the VPC's .2; derived from the PC address the same way the provider's NC2 sample does it
  dns_server = replace(var.pc_endpoint, "/^([0-9]+\\.[0-9]+)\\.[0-9]+\\.[0-9]+$/", "$1.0.2")
  subnets = {
    "app-web" = "192.168.10"
    "app-db"  = "192.168.20"
  }
}

resource "nutanix_subnet_v2" "app" {
  for_each      = local.subnets
  name          = each.key
  subnet_type   = "OVERLAY"
  vpc_reference = nutanix_vpc_v2.app.id
  ip_config {
    ipv4 {
      ip_subnet {
        ip { value = "${each.value}.0" }
        prefix_length = 24
      }
      default_gateway_ip { value = "${each.value}.1" }
      pool_list {
        start_ip { value = "${each.value}.10" }
        end_ip   { value = "${each.value}.200" }
      }
      dhcp_server_address { value = "${each.value}.2" }
    }
  }
  dhcp_options {
    domain_name_servers { ipv4 { value = local.dns_server } }
  }
}

# Default route out through the external NAT subnet. The VPC's route table is created with the VPC; look it up.
data "nutanix_route_tables_v2" "app" {
  filter     = "vpcReference eq '${nutanix_vpc_v2.app.id}'"
  depends_on = [nutanix_subnet_v2.app]
}

resource "nutanix_routes_v2" "app_default" {
  name               = "vpc-app-default"
  vpc_reference      = nutanix_vpc_v2.app.id
  route_table_ext_id = data.nutanix_route_tables_v2.app.route_tables[0].ext_id
  route_type         = "STATIC"
  destination {
    ipv4 {
      ip { value = "0.0.0.0" }
      prefix_length = 0
    }
  }
  next_hop {
    next_hop_type      = "EXTERNAL_SUBNET"
    next_hop_reference = data.nutanix_subnets_v2.ext_nat.subnets[0].ext_id
  }
}
```

The route table lookup after the subnets is deliberate: the provider's sample waits for the VPC and subnets before reading the table, because it is created asynchronously with the VPC. If `route_tables[0]` comes back empty on a fast apply, that is why.

## Step 7: an image, a VM, a floating IP

```text
 ┌─ web-01 ──────────────────────────────────────────────────┐
 │ 2 vCPU · 4 GiB · disk 40 GiB from Ubuntu cloud image      │   category  environment=lab
 │ nic ─▶ app-web (pool)          cloud-init: user + ssh key │
 │ floating IP from the AWS VPC range ─▶ this NIC            │
 └───────────────────────────────────────────────────────────┘
```

```hcl
# vm.tf
resource "nutanix_images_v2" "ubuntu" {
  name        = "ubuntu-24.04-cloud"
  description = "Ubuntu 24.04 cloud image, from the public repository"
  type        = "DISK_IMAGE"
  source {
    url_source {
      url = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
    }
  }
}

resource "nutanix_category_v2" "env_lab" {
  key   = "environment"
  value = "lab"
}

data "nutanix_clusters_v2" "nc2" {
  filter = "config/clusterFunction/any(t:t eq Clustermgmt.Config.ClusterFunctionRef'AOS')"
}

resource "nutanix_virtual_machine_v2" "web01" {
  name                 = "web-01"
  num_sockets          = 2
  num_cores_per_socket = 1
  memory_size_bytes    = 4 * pow(1024, 3)

  cluster    { ext_id = data.nutanix_clusters_v2.nc2.cluster_entities[0].ext_id }
  categories { ext_id = nutanix_category_v2.env_lab.id }

  disks {
    disk_address { bus_type = "SCSI", index = 0 }
    backing_info {
      vm_disk {
        data_source {
          reference {
            image_reference { image_ext_id = nutanix_images_v2.ubuntu.id }
          }
        }
        disk_size_bytes = 40 * pow(1024, 3)
      }
    }
  }

  nics {
    nic_network_info {
      virtual_ethernet_nic_network_info {
        nic_type = "NORMAL_NIC"
        subnet { ext_id = nutanix_subnet_v2.app["app-web"].id }
      }
    }
  }

  # cloud-init runs on first boot only; changing this block replaces the VM (the provider says so; plan for it)
  guest_customization {
    config {
      cloud_init {
        cloud_init_script {
          user_data {
            value = base64encode(templatefile("${path.module}/templates/web.yaml", { ssh_key = var.ssh_public_key }))
          }
        }
      }
    }
  }

  boot_config {
    uefi_boot { boot_order = ["DISK", "NETWORK"] }
  }
  power_state = "ON"
}

# A floating IP from the AWS VPC range, attached to the VM's NIC (the provider's NC2 sample pattern)
resource "nutanix_floating_ip_v2" "web01" {
  name                      = "fip-web-01"
  external_subnet_reference = data.nutanix_subnets_v2.ext_nat.subnets[0].ext_id
  association {
    vm_nic_association {
      vm_nic_reference = nutanix_virtual_machine_v2.web01.nics[0].ext_id
    }
  }
}
```

## The whole run

```text
 $ tofu apply
   nutanix_images_v2.ubuntu                creating...  [image download]   ✔
   nutanix_category_v2.env_lab             creating...                     ✔
   nutanix_vpc_v2.app                      creating...                     ✔
   nutanix_subnet_v2.app["app-web"]        creating...                     ✔
   nutanix_subnet_v2.app["app-db"]         creating...                     ✔
   nutanix_routes_v2.app_default           creating...                     ✔
   nutanix_virtual_machine_v2.web01        creating...                     ✔
   nutanix_floating_ip_v2.web01            creating...                     ✔

   Apply complete! Resources: 8 added, 0 changed, 0 destroyed.

 $ tofu plan
   No changes. Your infrastructure matches the configuration.
```

That empty second plan is the deliverable, and it is the part I show customers first. The NC2 console owns the cluster and Prism Central; git owns everything above them; and because every v4 write carries an ETag, a colleague's click in Prism Central shows up as a plan diff instead of a silent overwrite.

## What to watch

- **Two owners, one line between them.** Keep it sharp. The NC2 console owns the cluster, Prism Central, the transit VPC and the external subnets. Code owns your VPCs, subnets, routes, images and VMs. Don't manage the NC2-built objects from state; look them up with data sources, as above.
- **Flow Virtual Networking is a create-time decision.** No FVN, no Prism Central tab, no overlay VPCs, and no adding it later.
- **The allowlist is names.** `gateway-external-api.cloud.nutanix.com` is the NC2 console's door into your cluster; without it the cluster never reports Running.
- **Default credentials.** The new Prism Central's first password is the documented default. Change it before the provider ever sees it; keep it in the environment or a vault, never in `.tf` or state you don't encrypt.
- **Version pinning.** Match provider 2.x to the Prism Central version the NC2 console deployed; the matrix is on the provider's index page. Mismatches fail late.
- **The NC2 console has an API too.** API keys with NC2 scope (Admin creates and deletes clusters) and a five-minute JWT signed with the key; the guide's API Key Management page has the script. That is the path to putting step 4 itself in a pipeline; a topic for another post.

Sources: NC2 on AWS Deployment and User Guide (portal.nutanix.com: Deployment Workflow, Adding an AWS Cloud Account, Creating a Cluster, Ports and Endpoints Requirements, API Key Management), and the Nutanix Terraform provider docs and `examples/nc2` on GitHub. Where a block here disagrees with those on your version, they win.
