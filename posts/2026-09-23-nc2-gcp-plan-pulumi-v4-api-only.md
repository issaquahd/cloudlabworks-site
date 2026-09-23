---
title: "NC2 on Google Cloud, as code: Pulumi for the landing zone, the NC2 v2 API for the cluster, the v4 API for everything above"
date: 2026-09-23
time: 07:00
by: Alex Alvord
slug: nc2-gcp-plan-pulumi-v4-api-only
section: nutanix
summary: "Corrected twice, and now written from the Nutanix portal instead of from launch blogs. NC2 on Google Cloud is generally available on Google Compute Engine bare metal, six supported instance types across twenty-three regions, and the NC2 v2 API has a POST /clusters/gcp so the console comes out of the loop exactly as it did in the Azure post. Pulumi builds the landing zone, the v2 API builds the cluster, and the Prism Central v4 API owns everything above that line."
---

> **Corrections, 2026-09-23.** This post has been wrong twice today and both are worth stating.
>
> **First**, the 07:00 version opened by claiming Nutanix Cloud Clusters "does not list Google Cloud as a supported platform," and built a plan around routing past that absence with Sole-Tenant Nodes and a hand-driven Foundation install. ~~That premise was wrong.~~ NC2 on Google Cloud is generally available and runs on GCE bare metal.
>
> **Second**, the correction I published an hour later was rewritten from the Nutanix and Google launch blogs rather than from the documentation. It got the shape right and the details wrong: ~~three supported instance types~~ (there are six), ~~seventeen regions~~ (the portal lists twenty-three), ~~a /29 for Prism Central~~ (it is a /28), ~~10.200.0.0/16 among the reserved ranges~~ (it is 10.200.32.0/24), and it left the NC2 v2 API question open as UNKNOWN when the reference answers it plainly.
>
> This version is written from the NC2 on Google Cloud Deployment and User Guide on the Nutanix portal (pages last updated 2026-08-25), the Nutanix Cloud Bible's Google Cloud chapter (PC and AOS 7.3.1.1), the NC2 v2 API reference, and Compute Engine's machine-type documentation. Where this page and the guide disagree on your version, the guide wins.

Two posts this week walked NC2 on AWS and NC2 on Azure exactly as the public deployment guides describe them. Google Cloud is the third, and it lands closer to the Azure post than the AWS one: everything the NC2 console does here, the NC2 v2 API also does, including creating the cluster. So this is the same walk with the mouse taken away. Pulumi builds the Google Cloud side instead of Bicep, one v2 call builds the cluster, and from the moment Prism Central answers, only the v4 API touches it.

## The map

```text
 ┌─ your Google Cloud project (Pulumi) ─────────────────────────────────────────────────┐
 │  APIs + org policy: Compute Engine API, IP forwarding allowed, trusted image         │
 │  projects not blocked, VPC Service Controls not in the way, vCPU and LSSD quota      │
 │  cluster VPC, MTU >= 2000:                                                           │
 │    management subnet  /24 minimum  (nodes; a /28 for Prism Central is carved from it)│
 │    FVN NAT subnet     /27 minimum                                                    │
 │    FVN no-NAT subnet  /27 minimum                                                    │
 │    Cloud Router + Cloud NAT (BYO gateway: dynamic port allocation, not static)       │
 │  two service accounts: one for the NC2 console, one for the cluster nodes            │
 └────────────────────────────────────────┬─────────────────────────────────────────────┘
                                          │ vpc / subnet names, cloud account id
                                          ▼
 ┌─ NC2 v2 API (cloud.nutanix.com/api/v2), JWT from a My Nutanix key ───────────────────┐
 │  POST /clusters/gcp   cluster + Prism Central, one task; poll /tasks/{id}            │
 └────────────────────────────────────────┬─────────────────────────────────────────────┘
                                          │
                                          ▼
 ┌─ Google Cloud · region ──────────────────────────────────────────────────────────────┐
 │  GCE bare-metal nodes, 3 to 28 ── AHV ── CVM ── AOS                                  │
 │    Z3 / C4 metal: AOS on local Titanium SSD                                          │
 │    C3 metal:      no local storage, AOS on Hyperdisk Balanced                        │
 │  Prism Central in its /28   ◀── you talk to this, :9440                              │
 │  Flow Virtual Networking overlay, mandatory, and no Flow Gateway VMs unlike Azure    │
 └────────────────────────────────────────┬─────────────────────────────────────────────┘
                                          │ v4 APIs
                                          ▼
 ┌─ laptop ─ Pulumi (Nutanix provider, bridged from the Terraform provider) ─ Prism ────┐
 │  Central v4 REST ── Flow VPCs, subnets, images, VMs                                  │
 └──────────────────────────────────────────────────────────────────────────────────────┘
```

## Step 1: the substrate, and the choice the other two clouds do not make you make

AHV runs directly on Google Compute Engine bare metal instances: ordinary GCE instances with `-metal` in the machine type, in your own project and VPC, appearing in the Google Cloud console like any other instance. They are explicitly distinct from Google Bare Metal Solution, which is not supported with NC2. There is no nested virtualization and no Sole-Tenant Node group anywhere in this.

Six instance types are supported, and they split into two storage architectures. That split is the first real design decision, and it has no equivalent on AWS or Azure.

**Local SSD instances.** AOS storage comes from the node's local Titanium SSD, passed to the CVM the way local devices are on any Nutanix cluster.

| Instance type | vCPUs | Memory | Local NVMe | Processor |
|---|---|---|---|---|
| `z3-highmem-192-highlssd-metal` | 192 | 1,536 GB | 12 x 6 TB, 72,000 GB | Sapphire Rapids 8481C |
| `c4-standard-288-lssd-metal` | 288 | 1,080 GB | 6 x 3 TB, 18,000 GB | Granite Rapids 6985P-C |
| `c4-highmem-288-lssd-metal` | 288 | 2,232 GB | 6 x 3 TB, 18,000 GB | Granite Rapids 6985P-C |

**Hyperdisk Balanced instances.** No local storage at all. C3 metal nodes take configurable remote NVMe, 15 to 120 TB per host, 30,000 IOPS and 1,400 MB/s per host, four data disks.

| Instance type | vCPUs | Memory |
|---|---|---|
| `c3-standard-192-metal` | 192 | 768 GB |
| `c3-highcpu-192-metal` | 192 | 512 GB |
| `c3-highmem-192-metal` | 192 | 1,536 GB |

The C3 path buys you capacity that is decoupled from the node, and it comes with rules worth knowing before you pick it: you cannot change a Hyperdisk volume's capacity or performance from the Google Cloud console, you cannot add or remove disks on an existing node, growing an existing cluster means adding a node, a single volume failure replaces the whole node rather than the disk, and every C3 node in a cluster shares one storage profile.

Boot volumes differ too. Z3 and C4 use a 100 GB Hyperdisk Balanced volume for AHV and 150 GB of local disk for the CVM. C3 uses 100 GB Hyperdisk Balanced for AHV and another 200 GB Hyperdisk Balanced for the CVM.

One note on the memory column, because it cost me a re-check and then cost me a published error. Google's GA announcement blog lists the memory for the two C4 rows the other way round. Compute Engine's machine-type documentation and the Nutanix portal both have standard at 1,080 and highmem at 2,232. Two vendor sources against one blog, and it is also the only reading where the names mean what they say.

**Regions.** Twenty-three, and availability is per instance type, not per region. Only `us-central1`, `europe-west4` and `asia-southeast1` carry all six. Several regions carry Z3 alone, and `us-west1` carries only the C3 family. Check the portal's region table against the instance type you actually want rather than assuming a region is simply "supported."

**Placement.** Nutanix uses a partition placement policy with seven partitions, striping hosts across them so the partitions behave like racks on-premises. That gives you one full rack failure, or two in a 2N/2D configuration, without losing availability.

## Step 2: the landing zone, in Pulumi

You can let the NC2 console create the VPC and subnets at deployment. This series does not, because the point is that the network is code you own. The documented minimums are a /24 cluster subnet, with the Prism Central /28 carved out of it, and /27 for each of the two Flow Virtual Networking subnets.

Three requirements sit outside the resource graph and break deployments quietly if you miss them: the VPC needs an MTU of at least 2,000 bytes, IP forwarding must not be blocked by the `Restrict VM IP Forwarding` organization policy, and `constraints/compute.trustedImageProjects` must not block the `nc2-mcm-img-mgmt-prod` project, which is where the AHV, CVM and Prism Central images come from. VPC Service Controls must not be restricting the services either.

```python
# __main__.py (Pulumi, Python)
import pulumi
import pulumi_gcp as gcp

region, zone = "us-central1", "us-central1-a"   # all six instance types available here

cluster_net = gcp.compute.Network("nc2-cluster-vpc",
    auto_create_subnetworks=False,
    mtu=8896)   # documented minimum is 2000; take the jumbo option while you are here

mgmt = gcp.compute.Subnetwork("nc2-mgmt-subnet",
    network=cluster_net.id, region=region,
    ip_cidr_range="10.20.0.0/22",   # /24 is the documented minimum; PC's /28 comes out of this
    private_ip_google_access=True)

fvn_nat = gcp.compute.Subnetwork("nc2-fvn-nat-subnet",
    network=cluster_net.id, region=region, ip_cidr_range="10.21.0.0/24")   # /27 minimum

fvn_no_nat = gcp.compute.Subnetwork("nc2-fvn-no-nat-subnet",
    network=cluster_net.id, region=region, ip_cidr_range="10.22.0.0/24")   # /27 minimum

router = gcp.compute.Router("nc2-router", network=cluster_net.id, region=region)

# Bring-your-own Cloud NAT must use dynamic port allocation. The gateway NC2 creates for
# itself already does; a static-allocation gateway you hand it is a documented failure.
nat = gcp.compute.RouterNat("nc2-nat", router=router.name, region=region,
    nat_ip_allocate_option="AUTO_ONLY",
    source_subnetwork_ip_ranges_to_nat="ALL_SUBNETWORKS_ALL_IP_RANGES",
    enable_dynamic_port_allocation=True,
    min_ports_per_vm=32, max_ports_per_vm=4096)

# Two service accounts: the NC2 console uses one (and needs a key for it), the
# bare-metal nodes run as the other. Bind the documented custom roles separately.
sa_nc2 = gcp.serviceaccount.Account("nc2-console-sa",
    account_id="nc2-console", display_name="NC2 console orchestration")
sa_node = gcp.serviceaccount.Account("nc2-node-sa",
    account_id="nc2-node", display_name="NC2 bare-metal node identity")

pulumi.export("vpc", cluster_net.name)
pulumi.export("mgmt_subnet", mgmt.name)
pulumi.export("no_nat_subnet", fvn_no_nat.name)
```

Five ranges are reserved for AHV-to-CVM traffic, the VTEP subnet and CSMP, and must not appear anywhere in the above: `192.168.5.0/24`, `10.100.0.0/16`, `10.200.32.0/24`, `10.200.0.0/22` and `100.64.1.0/24`. Using one does not fail at `pulumi up`. It fails partway into a cluster build, which is the expensive place to find it.

You also need outbound internet from the cluster VPC, because the cluster's link to the NC2 console is not optional plumbing, it is a dependency, and DNS that can resolve public names. Nutanix recommends two servers from different providers.

## Step 3: the cluster, in one v2 API call

This is the part the earlier versions of this post got wrong from both directions: first by claiming no NC2 service existed on Google Cloud, then by saying the console was the documented path and marking the API question UNKNOWN. The NC2 v2 API reference has a `POST /clusters/gcp`, "Create Google Cloud cluster," and it takes the VPC and subnet names Pulumi just exported. So Google Cloud lands where Azure did: the console never has to be clicked.

```bash
curl --request POST \
  --url https://cloud.nutanix.com/api/v2/clusters/gcp \
  --header 'Authorization: Bearer '"$JWT" \
  --header 'Content-Type: application/json' \
  --data '{
    "name": "nc2-gcp-lab",
    "organization_id": "'"$ORG_ID"'",
    "cloud_account_id": "'"$CLOUD_ACCOUNT_ID"'",
    "region": "us-central1",
    "aos_version": "7.3",
    "license": "nci",
    "software_tier": "pro",
    "use_case": "general",
    "cluster_fault_tolerance": { "factor": "1N/1D" },
    "capacity": [
      { "instance_type": "z3-highmem-192-highlssd-metal", "nodes_count": 3 }
    ],
    "network": {
      "mode": "existing",
      "availability_zone": "us-central1-a",
      "vpc": "nc2-cluster-vpc",
      "management_subnet": "nc2-mgmt-subnet",
      "dns_servers": ["8.8.8.8", "1.0.0.1"],
      "fvn_config": {
        "nat_ip_ranges": [{ "name": "nc2-fvn-nat-subnet" }],
        "no_nat": { "name": "nc2-fvn-no-nat-subnet" }
      }
    },
    "prism_central": { "mode": "new", "vm_size": "small" }
  }'
```

Like every long-running v2 operation, this returns a task. Poll `/tasks/{id}` until it reaches a terminal state, the same loop the Azure post used. `license` takes `nci` or `aos`, where `aos` needs the legacy portfolio feature enabled, and `software_tier` takes `pro` or `ultimate`.

Node count is 3 to 28. Single-node clusters are not recommended in production and two-node clusters are not supported at all, so three is the floor rather than a suggestion.

## Step 4: Flow Virtual Networking, mandatory, and lighter than Azure

Flow Virtual Networking is required on Google Cloud. There is no VLAN-type networking option. Every user VM sits on an overlay subnet inside a Flow VPC, Geneve carries traffic between hosts, and Prism Central is the control plane. You create the virtual networks, subnets, DHCP, NAT, routing and security policy in Prism Central, in any address range you like including RFC1918, independent of the Google Cloud topology underneath.

The good news relative to the Azure post: NC2 on Google Cloud does not require Flow Gateway VMs. Azure needs them, Google Cloud does not, which removes a VNet, a pair of VMs and the BGP plumbing that went with them.

The constraint to design around: the network your VMs see is not the Google Cloud network. Reaching BigQuery, GKE or the internet goes through the overlay's NAT path, with floating IPs for inbound, or through Private Google Access, Private Service Access or Private Service Connect from the cluster VPC. Do not create Google Cloud entities inside the Flow external NAT subnet.

## Step 5: Pulumi against the v4 API

From the moment Prism Central answers on 9440, this converges on what the AWS and Azure posts already practice: every Flow VPC, subnet, image and VM is a v4 resource under code, with no console clicks recorded as the real state.

Nutanix ships an official Terraform and OpenTofu provider (`nutanix/nutanix`, v2.x), the one both prior posts used. Pulumi's Terraform bridge turns it into a native Pulumi SDK:

```bash
pulumi package add terraform-provider nutanix/nutanix
```

```python
# nc2_gcp_resources.py (Pulumi, once the bridged provider is generated)
import pulumi
import pulumi_nutanix as ntnx

provider = ntnx.Provider("pc", endpoint=prism_central_ip, port=9440,
    username=nutanix_username, password=nutanix_password, insecure=False)

overlay_vpc = ntnx.VpcV2("nc2-gcp-overlay",
    name="overlay-vpc-gcp", opts=pulumi.ResourceOptions(provider=provider))

overlay_subnet = ntnx.SubnetV2("nc2-gcp-overlay-subnet",
    vpc_reference=overlay_vpc.ext_id,
    ip_config={"ipv4": {"ip_subnet": {"ip": "192.168.100.0", "prefix_length": 24}}},
    opts=pulumi.ResourceOptions(provider=provider))
```

The `V2` suffixes are the provider's naming for v4-backed resources, as distinct from the older console-era ones, and that naming has moved between provider releases. Check it against the provider's current docs, not against this page. I have run the bridge as Pulumi documents it; I have not run this exact program end to end against a live Google Cloud cluster, and I will not write it as though I had.

## Limits worth knowing before you design around them

These are documented constraints, not opinions, and several of them differ from AWS and Azure:

- **Hibernate and resume are not supported** on Google Cloud. If your cost model for AWS assumed parking a cluster overnight, it does not port.
- **Three to twenty-eight nodes.** No two-node clusters.
- **No IPv6**, and no Prism Central backup or restore to Google Cloud Storage.
- **No cross-registration**: an on-premises Prism Element cannot register to an NC2 Prism Central, or the reverse.
- **No SPDK**, no renaming the CVM, and no reconfiguring Prism Central VM IP addresses once deployed.

## What is sourced from where

Everything above is from the Nutanix portal's NC2 on Google Cloud Deployment and User Guide (Planning for Deployment, Supported Bare-metal Instances, Supported Regions, Requirements, Limitations; pages dated 2026-08-25), the Nutanix Cloud Bible's Google Cloud chapter at PC and AOS 7.3.1.1 for the placement policy and the Flow Gateway comparison, the NC2 v2 API reference on nutanix.dev for the `POST /clusters/gcp` schema, and Compute Engine's machine-type documentation for the instance specifications. Region and instance availability move; re-read the region table rather than trusting a list written on a Wednesday.

Personal blog. I work at Nutanix; the opinions above are my own, this is not a Nutanix roadmap announcement, and nothing here is Nutanix confidential. This page has carried two corrections today, both struck through above rather than deleted, because a post that hides its own edit history is worth less than one that shows it.
