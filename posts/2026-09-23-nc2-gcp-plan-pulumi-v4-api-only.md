---
title: "NC2 on Google Cloud: a plan — Pulumi, and the v4 API only"
date: 2026-09-23
time: 07:00
by: Alex Alvord
slug: nc2-gcp-plan-pulumi-v4-api-only
section: nutanix
summary: Not a walkthrough of a shipping feature — Nutanix Cloud Clusters does not list Google Cloud as a supported platform today, only AWS and Azure. This is the lab's own architecture plan for the closest honest equivalent on GCP, built from Sole-Tenant Nodes instead of a managed NC2 service, orchestrated end to end in Pulumi, and touching nothing but the Prism Central v4 API once Prism Central exists. Marked plainly where it is proposal instead of documented fact.
---

Two posts this week walked NC2 on AWS and NC2 on Azure exactly as the public deployment guides describe them: an NC2 console (or its v2 API) that builds the cluster and Prism Central for you, then the v4 API and OpenTofu for everything above that line. Google Cloud does not get that walk, because Nutanix Cloud Clusters does not list GCP as a supported cloud today — the public deployment guides cover AWS and Azure only. **UNKNOWN: whether GCP support exists on any internal roadmap.** Anything below that reads like a fact about Nutanix's product is instead a stated architecture proposal, and is written that way on purpose.

So this is a different kind of post: a plan, not a report. The question it answers is narrower and more useful than "does Nutanix support GCP" — it's "what would it take to run something NC2-shaped on GCP anyway, with two constraints the lab was asked for: Pulumi as the IaC tool instead of Bicep or OpenTofu, and once Prism Central is up, only the v4 API touches it — no NC2 v2 API, because there is no NC2 service on GCP to call."

## The honest map

```text
 ┌─ what NC2 gives you for free on AWS/Azure ───────────────────────────────────────────┐
 │  a managed control plane that: onboards the cloud account, racks bare-metal capacity, │
 │  installs AOS, stands up Prism Central, wires overlay networking — one API/console   │
 └────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │  this layer does not exist for GCP
                                          ▼
 ┌─ what this plan has to build instead, on GCP ─────────────────────────────────────────┐
 │  1. Pulumi: project, VPC, subnets, Cloud NAT, firewall rules, service accounts        │
 │  2. Pulumi: Sole-Tenant Node group (nested virtualization) — the AHV substrate        │
 │  3. Foundation (imaged, not console-driven): AOS onto the sole-tenant instances        │
 │  4. Prism Central: a VM, deployed the same way Foundation Central deploys it on-prem  │
 │  5. From here on: v4 API only — no NC2 v2 API exists to reach for                     │
 └────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
 ┌─ laptop ─ Pulumi (Nutanix provider, bridged from the Terraform provider) ─ Prism      │
 │  Central v4 REST ─ VPCs, subnets, images, VMs — the same resources the AWS/Azure      │
 │  posts built with OpenTofu, now under Pulumi, against the same v4 surface             │
 └──────────────────────────────────────────────────────────────────────────────────────┘
```

The gap between "what NC2 does for you" and "what this plan does by hand" is the whole first half of the post. Steps 1 and 2 are ordinary GCP infrastructure, well documented. Step 3 is the part every NC2-on-AWS/Azure reader never sees, because the console did it: Foundation, imaging AOS onto bare capacity. That is real, well-documented Nutanix practice on-prem and it is the piece this plan borrows unmodified — it does not become easier or harder for being on GCP, it just becomes something you drive yourself instead of a click.

## Step 1: the substrate — Sole-Tenant Nodes, not general-purpose VMs

AHV needs nested virtualization: real hardware-assisted virtualization exposed to the guest, which ordinary GCE instances don't give a workload running as a guest hypervisor. GCP's answer is **Sole-Tenant Nodes**: physical servers reserved to one project, with `minNodeCpus`/node templates, and nested virtualization enabled on the VMs placed on them. This is the GCP feature that plays the role EC2 bare metal plays for NC2 on AWS and Azure Bare Metal plays there — a dedicated, non-shared piece of hardware AHV can run on top of, not a shared hypervisor slice.

```text
 gcloud compute node-templates create nc2-node-template \
   --node-type=n2-node-80-640 --region=us-central1
 gcloud compute node-groups create nc2-node-group \
   --node-template=nc2-node-template --target-size=3 --zone=us-central1-a
```

**UNKNOWN, and the first thing to verify before spending a dollar on this:** whether Nutanix's own licensing and hardware-compatibility list treats a GCP Sole-Tenant Node's virtualized-nested-on-real-silicon shape as a supported AHV target at all. On AWS and Azure, Nutanix qualifies the exact instance/host types NC2 uses; nothing here says a Sole-Tenant Node passes that bar. This plan proceeds on the architecture question only — whether the pieces fit together — not on a licensing green light, which is a real conversation with Nutanix, not a technical one this post can answer.

## Step 2: the landing zone, in Pulumi

Same shape as the Bicep landing zone in the Azure post — a VPC per NC2 concern, Cloud NAT for egress, custom routes — written as a Pulumi program instead of a template language, because that's the ask.

```python
# __main__.py (Pulumi, Python)
import pulumi
import pulumi_gcp as gcp

project, region = "nc2-lab-gcp", "us-central1"

cluster_net = gcp.compute.Network("nc2-cluster-vpc", auto_create_subnetworks=False)
cluster_subnet = gcp.compute.Subnetwork("nc2-cluster-subnet",
    network=cluster_net.id, ip_cidr_range="10.20.0.0/24", region=region)

pc_net = gcp.compute.Network("nc2-pc-vpc", auto_create_subnetworks=False)
pc_subnet = gcp.compute.Subnetwork("nc2-pc-subnet",
    network=pc_net.id, ip_cidr_range="10.30.0.0/26", region=region)

nat_router = gcp.compute.Router("nc2-nat-router", network=cluster_net.id, region=region)
nc2_nat = gcp.compute.RouterNat("nc2-nat", router=nat_router.name, region=region,
    nat_ip_allocate_option="AUTO_ONLY",
    source_subnetwork_ip_ranges_to_nat="ALL_SUBNETWORKS_ALL_IP_RANGES")

node_template = gcp.compute.NodeTemplate("nc2-node-template",
    region=region, node_type="n2-node-80-640")
node_group = gcp.compute.NodeGroup("nc2-node-group",
    zone=f"{region}-a", size=3, node_template=node_template.id)

pulumi.export("cluster_subnet", cluster_subnet.self_link)
pulumi.export("pc_subnet", pc_subnet.self_link)
pulumi.export("node_group", node_group.name)
```

Two VPCs for the same reason the Azure post had two VNets: the cluster nodes and Prism Central are different concerns even though nothing here forces a delegated-subnet split the way Azure's `Microsoft.BareMetal` delegation does. Peering (or Shared VPC, GCP's usual answer for "these need to talk") is the next resource in the same program; left out of the snippet because the exact shape depends on whether Prism Central needs to be reachable from a jump host, a VPN, or Cloud Interconnect back to the lab, a decision this plan leaves open on purpose rather than guessing.

## Step 3: Foundation — the part NC2 usually hides

On AWS and Azure, "install AOS onto the bare capacity" is inside the black box the console drives. Here it's the same Foundation flow used for any bare-metal AOS install: image the sole-tenant instances with the AOS installer, configure the CVMs, form the cluster. This is publicly documented Nutanix practice, unchanged by being on GCP — the work is getting Foundation's imaging path to reach GCP instances at all (PXE/ISO-based imaging assumes IPMI-like out-of-band access that a Sole-Tenant Node does not provide the same way a physical rack does). **UNKNOWN and flagged, not guessed at:** the exact mechanism for getting Foundation's image onto a Sole-Tenant Node instance without IPMI access is the single largest open question in this plan, bigger than anything in steps 1, 2 or 4. A custom GCE image built from the AOS installer, booted directly, is the likely shape; it is not verified here.

## Step 4: Prism Central, then the API-only line

Once a cluster exists, Prism Central deploys the way it deploys anywhere: an OVA/qcow2-equivalent image, sized `small`/`large`, given the cluster's virtual IP. From the moment Prism Central answers on 9440, this plan's second constraint takes over: **only the v4 API, nothing else.** No NC2 v2 API (there's no NC2 service on GCP to have one), no console clicks recorded as the "real" state — every VPC, subnet, image and VM from here on is a v4 resource, managed the same disciplined way the AWS and Azure posts already are, just via Pulumi instead of OpenTofu.

## Step 5: Pulumi against the v4 API — the part that already exists today

This is the one piece of the plan resting on solid, checkable ground rather than a guess: Nutanix ships an official Terraform/OpenTofu provider (`nutanix/nutanix`, v2.x, the same one both prior posts used against the v4 API). Pulumi's Terraform bridge (`pulumi package gen-sdk <provider>` / the `pulumi-terraform-provider` "any Terraform provider" bridge) turns any existing Terraform provider into a native Pulumi SDK without Nutanix having to publish a first-party Pulumi package. **Verify the exact bridging command and the generated package's fidelity against the current Pulumi docs before running this for real** — the bridge mechanism is real and documented by Pulumi, but this post has not run it end to end against the Nutanix provider, so the specifics (attribute mapping edge cases, provider config shape) are unverified, not assumed correct.

```bash
# generate a local Pulumi SDK from the Nutanix Terraform provider (Python target, this plan's language)
pulumi package add terraform-provider nutanix/nutanix
```

```python
# nc2_gcp_resources.py (Pulumi, once the bridged Nutanix provider is available)
import pulumi_nutanix as ntnx

provider = ntnx.Provider("pc", endpoint="10.30.0.5", port=9440,
    username=nutanix_username, password=nutanix_password, insecure=False)

overlay_vpc = ntnx.VpcV2("nc2-gcp-overlay",
    name="overlay-vpc-gcp", opts=pulumi.ResourceOptions(provider=provider))

overlay_subnet = ntnx.SubnetV2("nc2-gcp-overlay-subnet",
    vpc_reference=overlay_vpc.ext_id, ip_config={"ipv4": {"ip_subnet": {"ip": "192.168.100.0", "prefix_length": 24}}},
    opts=pulumi.ResourceOptions(provider=provider))
```

Same discipline as the AWS and Azure posts: field and resource names above follow the provider's own v4 resource naming (`VpcV2`, `SubnetV2` and similar suffixes are how the provider distinguishes v4-backed resources from the older v1/v2 NC2-console-era ones) as of this writing — check them against the provider's current docs before the first real run, not against this page.

## What this plan gets right and where it's honest about not knowing

- **Right, and reusable today:** the v4-API-only discipline itself. Whatever solves steps 1–4, the moment Prism Central exists, this plan and the shipped AWS/Azure posts converge onto the identical practice — Pulumi or OpenTofu, doesn't matter, against the same v4 surface, same ETag-based safety against a colleague's console click.
- **Right, and standard GCP practice:** Sole-Tenant Nodes as the nested-virtualization substrate. That part of the plan is not a guess; it's the documented GCP feature built for exactly this class of problem (running a guest hypervisor on GCP).
- **UNKNOWN, stated plainly:** Nutanix licensing/HCL support for this hardware shape; the Foundation-without-IPMI imaging path; and whether any of this maps to an actual Nutanix roadmap item for GCP. None of the three are answered by an architecture diagram, and this post doesn't pretend they are.

Personal blog. I work at Nutanix; the opinions and the plan above are my own, this is not a Nutanix roadmap announcement, and nothing here is Nutanix confidential — everything checkable is checked against public docs (the Nutanix Terraform/OpenTofu provider, GCP Sole-Tenant Node docs, Pulumi's Terraform bridge), and everything not checkable is marked `UNKNOWN` instead of asserted.
