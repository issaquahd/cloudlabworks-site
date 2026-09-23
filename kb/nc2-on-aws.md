---
title: NC2 on AWS
slug: nc2-on-aws
product: Nutanix Cloud Clusters (NC2), AWS
status: verified
verified: 2026-09-23
updated: 2026-09-23
summary: The supported EC2 bare-metal instance table, the tenancy models, the mixing rules for heterogeneous clusters, the node cap and the Prism Central subnet. Read from the hosted deployment guide dated September 9, 2026.
---

## Instances

Table 12 in the guide lists these EC2 bare-metal types. Rows marked with two asterisks in the guide need AOS 7.5.1.x or later.

| Instance | Physical cores / vCPUs | Memory | Local NVMe |
|---|---|---|---|
| `i7ie.metal-24xl` | 48 / 96 | 768 GB | 60 TB |
| `i7ie.metal-48xl` | 96 / 192 | 1,536 GB | 120 TB |
| `i7i.metal-24xl` | 48 / 96 | 768 GB | 22.5 TB |
| `i7i.metal-48xl` | 96 / 192 | 1,536 GB | 45 TB |
| `i4i.metal` | 64 / 128 | 1,024 GB | 30 TB |
| `m6id.metal` | 64 / 128 | 512 GB | 7.6 TB |
| `m5d.metal` | 48 / 96 | 384 GB | 3.6 TB |
| `i3.metal` (existing clusters only) | 36 / 72 | 512 GB | 15.2 TB |
| `i3en.metal` | 48 / 96 | 768 GB | 60 TB |
| `z1d.metal` | 24 / 48 | 384 GB | 1.8 TB |
| `g4dn.metal` | 48 / 96 | 384 GB, plus 128 GiB GPU memory | 1.8 TB |
| `m8id.metal-48xl` (AOS 7.5.1.x+) | 96 / 192 | 768 GB | 11.4 TB |
| `m8id.metal-96xl` (AOS 7.5.1.x+) | 192 / 384 | 1.5 TB | 22.8 TB |
| `r8id.metal-48xl` (AOS 7.5.1.x+) | 96 / 192 | 1.5 TB | 11.4 TB |
| `r8id.metal-96xl` (AOS 7.5.1.x+) | 192 / 384 | 3 TB | 22.8 TB |
| `c6id.metal` (AOS 7.5.1.x+) | 64 / 128 | 256 GB | 7.6 TB |
| `r6id.metal` (AOS 7.5.1.x+) | 64 / 128 | 1,024 GB | 7.6 TB |
| `c8id.metal-48xl` (AOS 7.5.1.x+) | 96 / 192 | 384 GB | 11.4 TB |
| `c8id.metal-96xl` (AOS 7.5.1.x+) | 192 / 384 | 768 GB | 22.8 TB |
| `r6idn.metal` (AOS 7.5.1.x+) | 64 / 128 | 1,024 GB | 7.6 TB |
| `x2idn.metal` (AOS 7.5.1.x+) | 64 / 128 | 2,048 GB | 3.8 TB |
| `x2iedn.metal` (AOS 7.5.1.x+) | 64 / 128 | 4,096 GB | 3.8 TB |
| `m6idn.metal` (AOS 7.5.1.x+) | 64 / 128 | 512 GB | 7.6 TB |

`i3.metal` is a legacy type as of the September 8, 2026 change: it cannot create a new cluster, hibernate one, or be added during expansion, including to clusters that already contain it. Existing `i3.metal` nodes can stay, be removed, or be migrated to a supported type.

The vCPU count is AWS's billing and quota figure, not a scheduling limit.

## Mixing instance types

- A cluster may mix at most three instance types, subject to bare-metal availability in the region. The guide's Creating a Heterogeneous Cluster section lists the allowed combinations.
- `g4dn.metal` clusters are homogeneous only.
- NC2 needs three or more partitions in the region for a given type; some types are absent from some regions for that reason.

## Tenancy

Two EC2 tenancy models. Default tenancy lets a bare-metal instance land on a different physical host after a power cycle and spreads instances across partitions with placement groups; it is also the model that allows Windows Server License Included instances. Dedicated Host pins each instance to a physical host NC2 allocates, and it stays there across power cycles.

## Regions

Table 13 in the guide is a matrix of region by instance type, and it runs to several pages because availability differs per type. Read the row for the instance you want; a region count on its own is misleading here.

## Cluster limits and networking

- Twenty-eight nodes maximum per cluster.
- Prism Central subnet: /28, and /28 is what the console selects by default.

## Automation

Cluster lifecycle is the NC2 console API on `https://cloud.nutanix.com/api/v2` (`POST /clusters/aws`, then poll the task). Everything after Prism Central answers is the v4 API; see [One API for the estate](/nutanix/kb/one-api-for-the-estate). The Terraform walk is in the post [NC2 on AWS, as code](/nutanix/nc2-aws-as-code-nc2-console-to-first-vm).

## Sources

- [Nutanix Cloud Clusters on AWS Deployment and User Guide](https://download.nutanix.com/documentation/hosted/Nutanix-Clusters-AWS.pdf), hosted PDF dated September 9, 2026 on its cover. Supported Regions and Bare-metal Instances (Tables 12 and 13), the change log entries for September 8, 2026 and July 3, 2026, the tenancy section, the limitations list. Read 2026-09-23. Also on [portal.nutanix.com](https://portal.nutanix.com/) under Cloud Clusters (NC2).
- [NC2 API reference](https://www.nutanix.dev/api_reference/apis/nc2.html): the documented 3-node AWS create example and task polling. Read 2026-09-23.
