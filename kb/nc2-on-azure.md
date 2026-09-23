---
title: NC2 on Azure
slug: nc2-on-azure
product: Nutanix Cloud Clusters (NC2), Azure
status: verified
verified: 2026-09-23
updated: 2026-09-23
summary: Three bare-metal SKUs, twenty regions with availability per SKU and the footnotes that matter, the node cap, the reserved ranges and the VNet and subnet sizes. Read from the hosted deployment guide dated August 25, 2026.
---

## Instances

Azure offers three SKUs (Table 16).

| Specification | AN36 | AN36P | AN64 |
|---|---|---|---|
| Processor | Intel 6140, 36 cores, 2.3 GHz | Intel 6240, 36 cores, 2.6 GHz | Intel Xeon 4th generation, 64 cores, 2.8 GHz |
| vCPUs | 72 | 72 | 128 |
| RAM | 576 GB | 768 GB | 1 TB |
| Storage | 18.56 TB (8 x 1.92 TB SATA SSD, 2 x 1.6 TB NVMe) | 20.7 TB (2 x 750 GB Optane, 6 x 3.2 TB NVMe) | 38.4 TB (5 x 7.68 TB NVMe) |
| Network between nodes | 25 Gbps | 25 Gbps | 25 Gbps |

The vCPU count is Azure's billing and quota figure, not a scheduling limit.

## Regions

Twenty regions (Table 17). AN36 is in two of them; AN64 is the newer SKU and the one still being added region by region through 2025 and 2026 per the guide's change log.

| Region | AN36 | AN36P | AN64 |
|---|---|---|---|
| Australia East | No | Yes | No |
| Canada Central | No | No | Yes |
| Canada East | No | No | Yes |
| Central India (Pune) | No | Yes | No |
| East US (Virginia) | Yes | No | No |
| East US 2 (Virginia) | No | Yes | Yes, two zones only |
| Germany West Central | No | No | Yes, one zone only |
| Japan East (Tokyo) | No | Yes | No |
| North Central US (Illinois) | No | Yes | Yes, one zone only |
| North Europe | No | No | Yes, add the region to the cloud account first |
| Qatar Central | No | Yes | Yes; RF3 (2N/2D) not supported in this region |
| Southeast Asia | No | Yes | No |
| South Central US | No | No | Yes, add the region to the cloud account first |
| South India | No | Yes | No |
| UAE North | No | Yes | Yes; RF3 not supported in one zone with AN64 |
| UK South | No | Yes | Yes, two zones only, AOS 6.10.1+ or 7.0.1+ |
| West Europe | No | Yes | No |
| West US 2 (Washington) | Yes | No | No |
| West US 3 | No | No | Yes, add the region to the cloud account first |

The zone-limited entries are exact in the guide's footnotes: AN64 in East US 2 is `useast2-az02` and `useast2-az03`; in UK South `uksouth-az01` and `uksouth-az02`; in Germany West Central `germanywc-az02`; in North Central US `usnorth-az02`.

## Cluster limits

- Twenty-eight nodes maximum with AOS 6.6 or later and Prism Central pc.2022.9 or later. Older releases cap at thirteen.
- Two-node clusters are not supported. Single-node clusters are not recommended for production.
- Each subnet in the resource group needs its own CIDR; subnets are not shared between clusters, and only private IPv4 ranges are allowed.

## Networking

Ranges the cluster reserves: `192.168.5.0/24` for CVM-to-hypervisor traffic on every node, so the cluster VNet must not use it; and for the Prism Central VNet, none of `10.100.0.0/16`, `10.200.0.0/24`, `192.168.5.0/24` or `10.200.0.0/22`. Clusters created before August 2, 2024 must also avoid `192.168.0.0/16`.

VNet and subnet sizes from the planning table (recommended on the left, minimum on the right):

| Component | Recommended | Minimum |
|---|---|---|
| Prism Central VNet | /23 | /23 or /24 |
| Flow Gateway subnet (external) | /24 | /24 to /26 |
| Flow Gateway subnet (internal) | /28 | /28 |
| BGP Gateway subnet | /28 | /28 |
| Internal Load Balancer subnet | /28 | not applicable |
| Hub VNet | /27 | /24 to /27 |
| Route Server subnet | /27 | /27, an Azure minimum |

## Automation

Cluster lifecycle is the NC2 console API on `https://cloud.nutanix.com/api/v2` (`POST /clusters/azure`, then poll the task). Everything after Prism Central answers is the v4 API; see [One API for the estate](/nutanix/kb/one-api-for-the-estate). The Bicep walk is in the post [NC2 on Azure, as code](/nutanix/nc2-azure-as-code-bicep-to-first-cluster).

## Sources

- [Nutanix Cloud Clusters on Azure Deployment and User Guide](https://download.nutanix.com/documentation/hosted/Nutanix-Cloud-Clusters-Azure.pdf), hosted PDF dated August 25, 2026 on its cover. Tables 16 and 17 with footnotes, the Limitations section, the VNet and subnet planning table. Read 2026-09-23. Also on [portal.nutanix.com](https://portal.nutanix.com/) under Cloud Clusters (NC2).
- [NC2 API reference](https://www.nutanix.dev/api_reference/apis/nc2.html). Read 2026-09-23.
