---
title: "NC2 on Google Cloud, as code: the console builds the cluster, Pulumi and the v4 API do the rest"
date: 2026-09-23
time: 07:00
by: Alex Alvord
slug: nc2-gcp-plan-pulumi-v4-api-only
section: nutanix
summary: "Corrected and rewritten. The first version of this post said Nutanix Cloud Clusters does not support Google Cloud. That was wrong: NC2 on Google Cloud is generally available, running the full Nutanix stack on Google Compute Engine bare metal instances in your own project and VPC. This is the third walkthrough in the series, on the same terms as the AWS and Azure posts: Pulumi for the landing zone, the NC2 console for the cluster, and the Prism Central v4 API for everything above that line."
---

> **Correction, 2026-09-23.** The version of this post published at 07:00 opened by saying Nutanix Cloud Clusters "does not list Google Cloud as a supported platform," and built an architecture plan around working around that absence with Sole-Tenant Nodes and a hand-driven Foundation install. ~~That premise was wrong.~~ NC2 on Google Cloud is generally available. It runs on Google Compute Engine bare metal instances, it is provisioned by the same NC2 console as AWS and Azure, and Sole-Tenant Nodes have nothing to do with it. The whole post below is rewritten against the shipping product. What survives from the first version is the last section, the v4-API-only discipline, which was the only part that did not depend on the bad premise. Sources for every claim are listed at the end.

Two posts this week walked NC2 on AWS and NC2 on Azure exactly as the public deployment guides describe them. Google Cloud gets the same walk, because it is the same product: the NC2 console provisions and manages the cluster lifecycle, Prism Central runs day two, and the Nutanix software stack on the nodes is the stack you already run on-premises. The two constraints handed to the lab for this one are Pulumi as the infrastructure-as-code tool instead of Bicep or OpenTofu, and, once Prism Central answers, only the v4 API touches it.

## The map

```text
 ┌─ NC2 console (SaaS, my.nutanix.com) ────────────────────────────────────────────────┐
 │  multicloud control plane: obtains bare-metal instances, sets the IAM roles it      │
 │  needs, writes VPC firewall rules, monitors hardware, replaces failed nodes         │
 └────────────────────────────────────────┬─────────────────────────────────────────────┘
                                          │ Compute Engine API, via two service accounts
                                          ▼
 ┌─ your Google Cloud project · your VPC ───────────────────────────────────────────────┐
 │  cluster (management) subnet:                                                        │
 │    GCE bare-metal nodes (C4 or Z3, -metal) ── AHV ── CVM ── AOS on local Titanium SSD │
 │    Prism Central /29 inside it   ◀── you talk to this, :9440                          │
 │    NAT range (secondary range)  ─┐                                                    │
 │    no-NAT subnet                ─┴── Flow Virtual Networking transit, mandatory here  │
 │  Cloud Router + Cloud NAT ── egress, including the cluster's link to the NC2 console  │
 └────────────────────────────────────────┬─────────────────────────────────────────────┘
                                          │ v4 APIs
                                          ▼
 ┌─ laptop ─ Pulumi (Nutanix provider, bridged from the Terraform provider) ─ Prism ────┐
 │  Central v4 REST ── Flow VPCs, subnets, images, VMs: the same resources the AWS and  │
 │  Azure posts built with OpenTofu, same v4 surface, different tool                    │
 └──────────────────────────────────────────────────────────────────────────────────────┘
```

The shape is the AWS and Azure shape. What differs on Google Cloud is the substrate underneath and one hard requirement in the middle, and those are the two sections worth your time.

## Step 1: the substrate is GCE bare metal, not a VM and not Bare Metal Solution

AHV runs directly on Compute Engine bare metal instances. These are ordinary GCE instances with `-metal` in the machine type: they appear in the Google Cloud console like any other instance, they live in your project and your VPC, and they are a different product from Google Bare Metal Solution, which is the older colocated offering and is not what NC2 uses. There is no nested virtualization involved and no Sole-Tenant Node group to build. Workload storage comes from the locally attached Titanium SSD on the node, which the CVM claims for the AOS storage layer, and each node also gets a Hyperdisk volume that AHV itself boots from.

The qualified machine types at GA:

| Machine type | vCPUs | Memory | Local Titanium SSD | Family |
|---|---|---|---|---|
| `z3-highmem-192-highlssd-metal` | 192 | 1,536 GB | 72,000 GiB | Z3, storage optimized |
| `c4-standard-288-lssd-metal` | 288 | 1,080 GB | 18,000 GiB | C4, general purpose |
| `c4-highmem-288-lssd-metal` | 288 | 2,232 GB | 18,000 GiB | C4, general purpose |

One note on that table, because it cost me a re-check. Google's own GA announcement blog lists the memory for the two C4 rows the other way round, 1,080 GB against `c4-highmem` and 2,232 GB against `c4-standard`. The Compute Engine machine-type documentation has standard at 1,080 and highmem at 2,232, which is also the only reading where the names mean what they say. The docs win. If you are sizing from the blog post, you are sizing backwards.

Nodes are placed across Availability Domains inside a Google Cloud zone, which maps onto Nutanix rack awareness, so replica placement survives a physical failure at both RF2 and RF3. Size n+1 for RF2 and n+2 for RF3, the same as anywhere else. If a node dies, NC2 provisions a replacement from Google Cloud and rebuilds resilience without you filing a hardware ticket.

## Step 2: the landing zone, in Pulumi

You can let the NC2 console create the VPC and subnets for you at deployment. This post does not, because the point of the series is that the network is code you own. Deploying into an existing VPC means the NAT range and the no-NAT subnet have to exist before the console asks for them, so they are in the program below.

What the cluster VPC needs: a management subnet wide enough for the bare-metal nodes, Prism Central and the NAT range; a /29 inside it reserved for the Prism Central VMs and VIP; a secondary range used by Flow Virtual Networking to hand out SNAT addresses and floating IPs; a no-NAT range for the Flow transit VPC; and Cloud NAT for egress, which is also how the cluster keeps its required link to the NC2 console.

```python
# __main__.py (Pulumi, Python)
import pulumi
import pulumi_gcp as gcp

region, zone = "us-west1", "us-west1-a"

cluster_net = gcp.compute.Network("nc2-cluster-vpc", auto_create_subnetworks=False)

# Management subnet: nodes, Prism Central (/29 inside this range), and the FVN NAT range
# as a secondary range on the same subnet.
mgmt = gcp.compute.Subnetwork("nc2-mgmt-subnet",
    network=cluster_net.id, region=region, ip_cidr_range="10.20.0.0/22",
    private_ip_google_access=True,
    secondary_ip_ranges=[{
        "range_name": "fvn-nat-range",
        "ip_cidr_range": "10.21.0.0/24",
    }])

# Flow Virtual Networking transit, no-NAT side.
no_nat = gcp.compute.Subnetwork("nc2-no-nat-subnet",
    network=cluster_net.id, region=region, ip_cidr_range="10.22.0.0/24")

router = gcp.compute.Router("nc2-router", network=cluster_net.id, region=region)
nat = gcp.compute.RouterNat("nc2-nat", router=router.name, region=region,
    nat_ip_allocate_option="AUTO_ONLY",
    source_subnetwork_ip_ranges_to_nat="ALL_SUBNETWORKS_ALL_IP_RANGES")

# Two service accounts: one the NC2 console assumes to orchestrate the build,
# one the bare-metal instances run as. Roles are bound separately; see the
# deployment guide for the exact permission sets, which change between releases.
sa_nc2 = gcp.serviceaccount.Account("nc2-console-sa",
    account_id="nc2-console", display_name="NC2 console orchestration")
sa_node = gcp.serviceaccount.Account("nc2-node-sa",
    account_id="nc2-node", display_name="NC2 bare-metal node identity")

pulumi.export("cluster_vpc", cluster_net.name)
pulumi.export("mgmt_subnet", mgmt.self_link)
pulumi.export("no_nat_subnet", no_nat.self_link)
```

Do not use `192.168.5.0/24`, `10.100.0.0/16`, `10.200.0.0/16`, `10.200.0.0/22` or `100.64.1.0/24` for any of these ranges. Those are reserved for AHV-to-CVM traffic, the VTEP subnet and CSMP. This is the kind of constraint that does not fail at `pulumi up`, it fails an hour into a cluster build, which is the expensive place to find it.

Three APIs have to be enabled on the project before any of this is useful: Compute Engine, IAM, and Service Usage or Quotas for the console's capacity checks. Check your quota for `-metal` instances in the target region too. Bare-metal quota is not granted by default and it is the single most common reason a first deployment stalls.

## Step 3: the cluster, from the NC2 console

This is the step the first version of this post got most wrong, so it is worth being plain about what actually happens. You do not run Foundation. You do not image anything. In the NC2 console you add your Google Cloud account to an organization, point a new cluster at the project, region, VPC and management subnet built above, give it the NAT and no-NAT ranges, choose a machine type and a node count, and the console does the rest: it obtains the bare-metal instances, installs the stack, forms the cluster, and deploys Prism Central onto it unless another Prism Central in the region is already available to adopt it. The advertised figure is a full cluster in about a couple of hours.

Two things that are easy to skip past. The cluster must keep its connectivity to the NC2 console for normal operation, so the Cloud NAT path above is not optional plumbing, it is a dependency. And Prism Central is not per-cluster by default: the first cluster in a region stands one up, later clusters can adopt it or run their own.

**UNKNOWN, and I am not going to guess at it:** whether the NC2 v2 API has a create-cluster endpoint for Google Cloud the way it does for AWS and Azure. The Azure post used `POST /clusters/azure` to take the mouse out of the loop entirely. The nutanix.dev v2 reference renders its endpoint list client-side and its worked example is the AWS one, so I could not confirm a Google Cloud equivalent from the public documentation without an account against it. If it exists, this step collapses into one more API call and the console never has to be opened. Treat the console path above as the documented one and check the v2 reference yourself before assuming either way.

## Step 4: Flow Virtual Networking is mandatory here

On AWS and Azure, Flow Virtual Networking is a choice. On Google Cloud it is a requirement: NC2 does not support VLAN-type networking there at all. Every user VM lives on a Flow overlay subnet inside a Flow VPC, with Geneve encapsulation between hosts, and Prism Central is the control plane for all of it. That has one practical consequence worth designing around early: the network your VMs see is not the Google Cloud network, it is the overlay, and reaching a native Google Cloud service such as BigQuery or GKE from a VM goes out through the transit VPC using the NAT range, or over Private Google Access, Private Service Access or Private Service Connect from the cluster VPC.

For anyone coming from the AWS post, this is the one place where the muscle memory does not transfer.

## Step 5: Pulumi against the v4 API

From the moment Prism Central answers on 9440, this post converges on exactly what the AWS and Azure posts already practice: every Flow VPC, subnet, image and VM is a v4 resource, managed as code, with no console clicks recorded as the real state.

Nutanix ships an official Terraform and OpenTofu provider (`nutanix/nutanix`, v2.x), which is the one both prior posts used against the v4 API. Pulumi's Terraform bridge turns it into a native Pulumi SDK without Nutanix having to publish a first-party Pulumi package:

```bash
pulumi package add terraform-provider nutanix/nutanix
```

```python
# nc2_gcp_resources.py (Pulumi, once the bridged provider is generated)
import pulumi
import pulumi_nutanix as ntnx

provider = ntnx.Provider("pc", endpoint="10.20.0.10", port=9440,
    username=nutanix_username, password=nutanix_password, insecure=False)

overlay_vpc = ntnx.VpcV2("nc2-gcp-overlay",
    name="overlay-vpc-gcp", opts=pulumi.ResourceOptions(provider=provider))

overlay_subnet = ntnx.SubnetV2("nc2-gcp-overlay-subnet",
    vpc_reference=overlay_vpc.ext_id,
    ip_config={"ipv4": {"ip_subnet": {"ip": "192.168.100.0", "prefix_length": 24}}},
    opts=pulumi.ResourceOptions(provider=provider))
```

The `V2` suffixes are the provider's own naming for its v4-backed resources, as distinct from the older v1 and v2 console-era ones. That naming has moved between provider releases, so check it against the provider's current documentation rather than against this page. I have run the bridge mechanism as documented by Pulumi; I have not run this exact program end to end against a live Google Cloud cluster, and I am not going to write it as though I had.

## What is verified here, and what is not

- **Verified against vendor documentation:** GA status and the 17-region starting footprint, GCE bare metal as the substrate, the three qualified machine types and their specifications, the NC2 console as the provisioning control plane, the two service accounts, the mandatory Flow Virtual Networking, the network layout including the Prism Central /29 and the NAT and no-NAT ranges, node placement across Availability Domains, license portability and Marketplace availability.
- **Corroborative only, confirm before you build:** the reserved CIDR list, which comes from a community landing-zone repository rather than from the deployment guide's own text. It matches what those ranges are used for, but check the guide.
- **UNKNOWN:** whether an NC2 v2 API create-cluster endpoint exists for Google Cloud, and the exact current IAM permission sets for the two service accounts, which change between releases and belong in the guide, not in a blog post.
- **Region and instance availability move.** Seventeen regions at GA is more by next quarter, by Nutanix's own statement. Check the portal's region page and Compute Engine's bare-metal regional availability rather than trusting any list written on a Wednesday.

Sources: the Nutanix GA announcement for NC2 on Google Cloud; Google Cloud's GA announcement; Google Cloud's own NC2 on Google Cloud solution document; Compute Engine bare metal instance and general-purpose machine family documentation; the Nutanix Cloud Clusters on Google Cloud Deployment and User Guide on the Nutanix portal; the NC2 v2 API reference on nutanix.dev; Pulumi's Terraform bridge documentation.

Personal blog. I work at Nutanix; the opinions above are my own, this is not a Nutanix roadmap announcement, and nothing here is Nutanix confidential. Everything checkable is checked against public documentation, the one thing I could not check is marked UNKNOWN, and the thing I got wrong this morning is struck through at the top rather than quietly deleted.
