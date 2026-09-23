---
title: NC2 on Google Cloud
slug: nc2-on-google-cloud
product: Nutanix Cloud Clusters (NC2), Google Cloud
status: verified
verified: 2026-09-23
updated: 2026-09-23
summary: Six bare-metal instance types in two storage architectures, twenty-three regions with availability per instance type, the subnet sizes, the node limits and the reserved ranges. Read from the hosted deployment guide dated August 25, 2026.
---

## Instances

Six instance types, in two families that differ in where AOS keeps its data.

**Local SSD (Table 7 in the guide).** AOS runs on the node's own NVMe.

| Instance | Processor | Cores / vCPUs | Memory | Local storage | Network |
|---|---|---|---|---|---|
| `z3-highmem-192-highlssd-metal` | Intel Sapphire Rapids 8481C, 2.2 GHz, 3.0 GHz turbo | 96 / 192 | 1,536 GB DDR5 | 12 x 6 TB NVMe, 72,000 GB | up to 200 Gbps, Tier 1 |
| `c4-standard-288-lssd-metal` | Intel Granite Rapids 6985P-C, 3.0 GHz, 3.9 GHz turbo | 144 / 288 | 1,080 GB DDR5 | 6 x 3 TB, 18,000 GB | up to 200 Gbps, Tier 1 |
| `c4-highmem-288-lssd-metal` | Intel Granite Rapids 6985P-C, 3.0 GHz, 3.9 GHz turbo | 144 / 288 | 2,232 GB DDR5 | 6 x 3 TB, 18,000 GB | up to 200 Gbps, Tier 1 |

**Hyperdisk Balanced (Table 8).** No local storage. Capacity is remote and decoupled from the node. Added to the guide on July 27, 2026.

| Instance | Processor | Cores / vCPUs | Memory | Remote storage per host | IOPS / throughput per host |
|---|---|---|---|---|---|
| `c3-standard-192-metal` | Intel 4th Gen Xeon (Sapphire Rapids), 2.8 GHz | 96 / 192 | 768 GB | 15 to 120 TB | 30,000 / 1,400 MB/s |
| `c3-highcpu-192-metal` | same | 96 / 192 | 512 GB | 15 to 120 TB | 30,000 / 1,400 MB/s |
| `c3-highmem-192-metal` | same | 96 / 192 | 1,536 GB | 15 to 120 TB | 30,000 / 1,400 MB/s |

Each C3 node carries four data disks and two boot disks (one AHV, one CVM). Three constraints come with Hyperdisk: never change a volume's capacity or performance from the Google Cloud console; disks cannot be added to or removed from an existing node, so more capacity means another node; and a single failed volume is handled by replacing the whole node.

The vCPU count is the cloud provider's billing and quota figure, not a scheduling limit.

## Regions

Twenty-three regions (Table 9), and availability is per instance type. Three regions carry all six types: `asia-southeast1`, `europe-west4` and `us-central1`. Pick the region for the instance, not the other way round.

| Region | z3-highmem | c4-standard | c4-highmem | c3-standard | c3-highcpu | c3-highmem |
|---|---|---|---|---|---|---|
| asia-east1 | Yes | No | No | Yes | No | No |
| asia-northeast1 | Yes | No | No | No | No | No |
| asia-south1 | Yes | No | No | Yes | No | No |
| asia-southeast1 | Yes | Yes | Yes | Yes | Yes | Yes |
| australia-southeast2 | Yes | No | No | No | No | No |
| europe-north2 | No | No | No | Yes | No | No |
| europe-southwest1 | No | No | Yes | No | No | No |
| europe-west1 | Yes | No | No | Yes | Yes | Yes |
| europe-west2 | Yes | No | No | No | No | No |
| europe-west3 | Yes | No | No | Yes | No | No |
| europe-west4 | Yes | Yes | Yes | Yes | Yes | Yes |
| europe-west8 | Yes | No | No | No | No | No |
| me-central1 | Yes | No | No | Yes | No | Yes |
| me-central2 | No | No | Yes | No | No | No |
| northamerica-northeast2 | Yes | No | No | No | No | No |
| southamerica-east1 | Yes | No | No | No | No | No |
| us-central1 | Yes | Yes | Yes | Yes | Yes | Yes |
| us-east1 | Yes | No | No | Yes | Yes | Yes |
| us-east4 | Yes | No | Yes | Yes | Yes | Yes |
| us-east5 | Yes | No | No | Yes | Yes | Yes |
| us-south1 | No | No | Yes | No | No | No |
| us-west1 | No | No | No | Yes | Yes | Yes |
| us-west2 | Yes | No | No | No | No | No |

The guide's change log shows how fast this table moves: `asia-northeast1` was added July 2, 2026, the C3 family July 27, 2026, and `asia-south1` August 14, 2026. Re-read the table rather than trusting this copy.

## Cluster limits

- Three nodes minimum, twenty-eight maximum. Creating a cluster outside that range is listed as unsupported.
- Node type and redundancy factor are fixed at creation.
- Capacity changes go through the NC2 console, never the Google Cloud console.

## Networking

Subnet sizes, from the planning chapter:

| Subnet | Minimum |
|---|---|
| Cluster (management) subnet | /24, with a /28 for Prism Central carved out of it |
| Flow Virtual Networking NAT subnet | /27 |
| Flow Virtual Networking no-NAT subnet | /27 |

Ranges the cluster reserves for itself, which the VPC must not use: `192.168.5.0/24`, `10.100.0.0/16`, `10.200.32.0/24`, `10.200.0.0/22` and `100.64.1.0/24`.

## Automation

Cluster lifecycle is the NC2 console API, `POST /clusters/gcp` on `https://cloud.nutanix.com/api/v2`, which returns a task to poll. Everything after Prism Central answers is the v4 API; see [One API for the estate](/nutanix/kb/one-api-for-the-estate). The full walk with Pulumi for the landing zone is in the post [NC2 on Google Cloud, as code](/nutanix/nc2-gcp-plan-pulumi-v4-api-only).

## Sources

- [Nutanix Cloud Clusters on Google Cloud Deployment and User Guide](https://download.nutanix.com/documentation/hosted/Nutanix-Cloud-Clusters-Google-Cloud.pdf), hosted PDF dated August 25, 2026 on its cover. Tables 7, 8 and 9, the planning chapter's subnet and reserved-range lists, and the limitations list. Read 2026-09-23. The same guide is browsable on [portal.nutanix.com](https://portal.nutanix.com/) under Cloud Clusters (NC2).
- [NC2 API reference](https://www.nutanix.dev/api_reference/apis/nc2.html) for the cluster create call. Read 2026-09-23.
