---
title: One API for the estate: Prism Central v4
slug: one-api-for-the-estate
product: Prism Central, v4 API
status: verified
verified: 2026-09-23
updated: 2026-09-23
summary: Every cluster in a Nutanix estate, on-prem AHV and NC2 on AWS, Azure and Google Cloud, registers to Prism Central and is driven through the same v4 API namespaces. One version, one URL shape, one set of SDKs. What sits outside that line, and why.
---

## The rule

Pick v4 and use it for the entire estate. Prism Central serves the v4 API for every cluster registered to it, whether the nodes are in a rack in Duvall or on bare metal in us-central1. The URL shape never changes:

```text
https://{prism-central}:9440/api/{namespace}/{version}/{resource}
```

Two things follow from that. Automation written once against v4 runs unchanged against every cloud, because the cloud never appears in the call. And the version pin is a single decision, made once per namespace, not once per cluster.

Nutanix.dev states the position plainly: v4 APIs and SDKs are generally available and v4 is the recommended version for production. Prism Element v2.0 and Prism Central v3 remain published as current GA references, but they are the past.

## The namespaces

The API reference on developers.nutanix.com lists twenty v4 namespaces (read from the site's namespace selector on 2026-09-23):

| Namespace | URL path segment (where the user guide shows it) |
|---|---|
| AIOps | `aiops` |
| Cluster Management | `clustermgmt` |
| Data Policies | |
| Data Protection | |
| Files | |
| Identity and Access Management | |
| Licensing | |
| Life Cycle Management | |
| Flow Management | |
| Monitoring | `monitoring` |
| Multi Domain Management | |
| Networking | |
| Object Storage Management | |
| NCM Operation Base Platform | |
| Prism | |
| Security | |
| Storage | |
| SP Central Tenant Management | |
| Virtual Machine Management | `vmm` |
| Volumes | `volumes` |

Each namespace carries its own version list. Cluster Management, read on the same day, offers v4.0, v4.1, v4.2 and v4.3 plus the earlier alpha and beta tags. The Nutanix API User Guide's own examples use `vmm/v4.1`, `clustermgmt/v4.1`, `volumes/v4.1` and `monitoring/v4.3`. Which minor a given Prism Central serves depends on its release, so the pin is: one v4 minor per namespace, chosen from what the oldest Prism Central in the estate supports, and raised deliberately.

## The URL, worked

Listing VMs whose name starts with `pc`, excluded, on any cluster in the estate:

```text
GET https://{prism-central}:9440/api/vmm/v4.1/ahv/config/vms?$filter=not startswith(name, 'pc')
```

The query grammar is OData and it is the same in every namespace: `$filter` with `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `and`, `or`, `not`, `in`, `contains`, `startswith`, `endswith`; `$select` to trim the projection; `$expand` to pull related entities; `$page` and `$limit` for paging; `$apply` with `groupby` and `aggregate` where the namespace supports it. Three more from the user guide:

```text
GET /api/clustermgmt/v4.1/config/storage-containers?$select=name,containerExtId,replicationFactor
GET /api/volumes/v4.1/config/volume-groups?$expand=metadata,cluster
GET /api/monitoring/v4.3/serviceability/alerts?$apply=groupby((severity), aggregate(title with count as alertCount))
```

## Rate limits, by Prism Central size

From the Nutanix API User Guide. The limit is per Prism Central, so an estate-wide job that fans out across many clusters is still bounded by the one Prism Central it talks to.

| Prism Central size | Memory | vCPU | Disk | Requests per second |
|---|---|---|---|---|
| X-Small | 18 GB | 4 | 100 GB | 30 |
| Small | 26 GB | 6 | 500 GB | 40 |
| Large | 44 GB | 10 | 2,500 GB | 60 |
| Extra Large | 60 GB | 14 | 2,500 GB | 80 |

## SDKs and infrastructure as code

Nutanix.dev lists v4 SDKs for Python, Java, Go and JavaScript. The Nutanix Terraform provider exposes v4-backed resources with a `_v2` suffix, and Pulumi reaches the same provider through its Terraform bridge. The `V2` in the resource names is the provider's naming, not the API version underneath, which is v4. Check the suffix against the provider's current documentation before relying on it; it has moved between releases.

## What is not v4, and is not pretending to be

The NC2 console API at `https://cloud.nutanix.com/api/v2` creates, hibernates, resumes and terminates cloud clusters and hands back tasks to poll. Nutanix.dev's API reference index lists it as its own product API, and there is no v4 edition of it as of 2026-09-23. That is the one call in an NC2 build that is not v4: the call that makes the cluster exist. Once Prism Central answers on port 9440, everything above that line is v4.

The same index lists other product APIs with their own versioning: Nutanix Database Service, NCM Self-Service, NCM Cost Governance, NCM Security Central, Move, Foundation, Foundation Central and Nutanix Enterprise AI. They are separate products with separate references; none of them changes the estate rule for Prism Central.

## Sources

- [Nutanix.dev API Reference index](https://www.nutanix.dev/api-reference/): v4 GA announcement, product API list, NC2 API entry. Read 2026-09-23.
- [developers.nutanix.com API Reference](https://developers.nutanix.com/api-reference): namespace and version selectors. Read 2026-09-23.
- [Nutanix API User Guide](https://www.nutanix.dev/nutanix-api-user-guide/): URL shape, OData grammar, rate limit table, v2.0 and v3 reference links. Read 2026-09-23.
- [NC2 API reference](https://www.nutanix.dev/api_reference/apis/nc2.html): cluster create, hibernate, resume, terminate and task polling on the v2 base URL. Read 2026-09-23.
