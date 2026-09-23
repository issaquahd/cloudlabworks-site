---
title: "NC2 on Google Cloud, day one: from Prism Central to a running VM with nothing but the v4 API"
date: 2026-09-23
time: 16:30
by: Alex Alvord
slug: nc2-gcp-day-one-pure-v4-api
section: nutanix
draft: true
summary: "The follow-up to the Pulumi post. The cluster exists and Prism Central answers on 9440; from here on every call is the Prism Central v4 API, pinned to one version, with no console, no Terraform provider and no cloud SDK. Cluster, VPC, subnet, image, VM, power on, task poll: seven calls, and the same seven on AWS, Azure or a rack."
---

Everything here is read from the v4.1 OpenAPI specifications published by Nutanix at developers.nutanix.com (namespace files `networking`, `vmm`, `clustermgmt` and `prism`, each at spec version 4.1.1), the Nutanix API User Guide on nutanix.dev, and the NC2 on Google Cloud Deployment and User Guide dated August 25, 2026. Read on 2026-09-23. Where this page and the specification disagree on your version, the specification wins. Endpoints, minimum Prism Central versions and body shapes are quoted from the specifications; I have not run this exact sequence against a live Google Cloud cluster, and I will not write it as though I had.

[The previous post](/nutanix/nc2-gcp-plan-pulumi-v4-api-only) built the Google Cloud landing zone with Pulumi and created the cluster with one call to the NC2 console API. That call is the last time anything cloud-specific appears. This post starts where that one stopped: Prism Central is up, it answers on port 9440, and the question is how far you can get with only the v4 API. The answer is all the way to a VM with a public-facing floating IP, and the sequence is identical to the one you would run against NC2 on AWS, NC2 on Azure, or the cluster in the rack, because the API never sees the cloud.

## The map

```text
 NC2 console API (v2)  ─── POST /clusters/gcp ──▶ cluster exists, Prism Central answers on 9440
                                                          │
  ┌── everything below this line is https://{pc}:9440/api/{namespace}/v4.1/ ──────────────────┐
  │                                                                                            │
  │  1  GET  clustermgmt/v4.1/config/clusters            which cluster, its extId               │
  │  2  POST networking/v4.1/config/vpcs                 the overlay VPC                        │
  │  3  POST networking/v4.1/config/subnets              an OVERLAY subnet inside it            │
  │  4  POST vmm/v4.1/content/images                     a disk image, pulled from a URL         │
  │  5  POST vmm/v4.1/ahv/config/vms                     the VM: NIC on the subnet, disk from 4  │
  │  6  POST vmm/v4.1/ahv/config/vms/{extId}/$actions/power-on                                   │
  │  7  POST networking/v4.1/config/floating-ips         a floating IP on the VM's NIC           │
  │                                                                                            │
  │  every POST returns 202 + a task; GET prism/v4.1/config/tasks/{extId} until SUCCEEDED       │
  └────────────────────────────────────────────────────────────────────────────────────────────┘
```

## The pin: v4.1, and why not v4.4

Each namespace publishes its own minor versions. On the day of writing, `networking` and `prism` go up to v4.4, `vmm` and `clustermgmt` to v4.3. This post pins every call to **v4.1**, for one reason that the specification states per operation: the minimum Prism Central for every call used here is **pc.2024.3**, and creating a VM or a subnet also states a minimum Prism Element of 6.8 and 7.0 respectively. NC2 on Google Cloud went generally available on AOS 7.5, so every NC2 cluster there clears those minimums. A newer minor buys features this walk does not need and raises the floor for no return. Pick the lowest minor whose floor your oldest Prism Central clears, write it once, and raise it on purpose.

Three conventions apply to every call below, all from the specification:

- **Authentication** is HTTP Basic or an API key in the `X-ntnx-api-key` header (the two security schemes every v4.1 spec declares).
- **`NTNX-Request-Id`** is a required header on every POST: a UUID you generate, so a retried request is idempotent instead of creating a second VPC.
- **Polymorphic fields carry a `$objectType` discriminator, and its value drops the minor version.** The schema is named `vmm.v4.1.ahv.config.VmDisk`; the value you send is `vmm.v4.ahv.config.VmDisk`. Every example in the published specifications follows that pattern, and it is the one place in this walk where copying a schema name verbatim produces a request the server rejects.
- **Actions on an existing resource need `If-Match`.** Power-on is one. The value is the ETag returned by the GET on that resource. Send the action without it and the server answers **428 Precondition Required**, which is the specification's wording, not mine.

## Step 1: which cluster

```bash
PC=https://prism-central.example:9440/api
AUTH="admin:${PC_PASSWORD}"

curl -sS -u "$AUTH" "$PC/clustermgmt/v4.1/config/clusters?\$select=extId,name" | jq '.data[]'
```

Cluster Management lists every cluster registered to this Prism Central, and the query grammar is OData: `$select` trims the projection, `$filter` narrows it, `$page` and `$limit` page it. The `extId` of the NC2 cluster is the only value the rest of the walk needs from this call. The same call on a Prism Central with an on-prem cluster and three NC2 clusters returns four rows, and nothing in any row says which cloud it lives in; that is the point.

## Step 2: the overlay VPC

```bash
curl -sS -u "$AUTH" -X POST "$PC/networking/v4.1/config/vpcs" \
  -H "Content-Type: application/json" -H "NTNX-Request-Id: $(uuidgen)" \
  -d '{
    "name": "overlay-vpc-gcp",
    "description": "Flow Virtual Networking overlay, day one",
    "vpcType": "REGULAR",
    "externalSubnets": [ { "subnetReference": "<extId of the NC2 external subnet>" } ]
  }'
```

`vpcType` is `REGULAR` or `TRANSIT` in the spec. On NC2 on Google Cloud, Flow Virtual Networking is mandatory and the console creates the transit VPC and the external subnets during cluster deployment, which is why this step attaches to an external subnet rather than creating one: a VPC can reference up to four. The response is `202 Accepted` with a task reference; the VPC's own `extId` comes back in the task's `entitiesAffected` once it succeeds, or from a `GET .../vpcs?$filter=name eq 'overlay-vpc-gcp'`.

## Step 3: an overlay subnet

```bash
curl -sS -u "$AUTH" -X POST "$PC/networking/v4.1/config/subnets" \
  -H "Content-Type: application/json" -H "NTNX-Request-Id: $(uuidgen)" \
  -d '{
    "name": "app-tier",
    "subnetType": "OVERLAY",
    "vpcReference": "<VPC extId from step 2>",
    "ipConfig": [ {
      "ipv4": {
        "ipSubnet":         { "ip": { "value": "192.168.100.0" }, "prefixLength": 24 },
        "defaultGatewayIp": { "value": "192.168.100.1" },
        "poolList": [ { "startIp": { "value": "192.168.100.10" }, "endIp": { "value": "192.168.100.200" } } ]
      }
    } ]
  }'
```

`subnetType` is `VLAN` or `OVERLAY`; overlay subnets take a `vpcReference` and no `clusterReference`, VLAN subnets the reverse. The `ipConfig` shape above is quoted from the spec's `IPv4Config`: an `ipSubnet` with `ip` and `prefixLength`, a `defaultGatewayIp`, an optional `dhcpServerAddress`, and a `poolList` of `startIp`/`endIp` pairs. Every address is an object with a `value`, never a bare string. Minimum Prism Central pc.2024.3, minimum Prism Element 7.0.

## Step 4: a disk image from a URL

```bash
curl -sS -u "$AUTH" -X POST "$PC/vmm/v4.1/content/images" \
  -H "Content-Type: application/json" -H "NTNX-Request-Id: $(uuidgen)" \
  -d '{
    "name": "ubuntu-24.04-cloudimg",
    "type": "DISK_IMAGE",
    "source": { "$objectType": "vmm.v4.content.UrlSource",
                "url": "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img" },
    "clusterLocationExtIds": [ "<cluster extId from step 1>" ]
  }'
```

`type` is `DISK_IMAGE` or `ISO_IMAGE`. `source` is one of `UrlSource`, `VmDiskSource` or `ObjectsLiteSource`; the `$objectType` discriminator names which. `clusterLocationExtIds` places the image on the NC2 cluster, which matters because Prism Central may hold clusters in three clouds and a rack, and an image is only useful where the VM will run. The cluster pulls the file itself, so the URL must be reachable from the cluster's Flow no-NAT or NAT path, which is a landing-zone fact from the previous post, not an API one.

## Step 5: the VM

```bash
curl -sS -u "$AUTH" -X POST "$PC/vmm/v4.1/ahv/config/vms" \
  -H "Content-Type: application/json" -H "NTNX-Request-Id: $(uuidgen)" \
  -d '{
    "name": "app-01",
    "numSockets": 2, "numCoresPerSocket": 1,
    "memorySizeBytes": 4294967296,
    "cluster": { "extId": "<cluster extId from step 1>" },
    "bootConfig": { "$objectType": "vmm.v4.ahv.config.UefiBoot" },
    "disks": [ {
      "diskAddress": { "busType": "SCSI", "index": 0 },
      "backingInfo": { "$objectType": "vmm.v4.ahv.config.VmDisk",
                       "diskSizeBytes": 42949672960,
                       "dataSource": { "reference": { "$objectType": "vmm.v4.ahv.config.ImageReference",
                                                      "imageExtId": "<image extId from step 4>" } } }
    } ],
    "nics": [ {
      "networkInfo": { "nicType": "NORMAL_NIC",
                       "subnet": { "extId": "<subnet extId from step 3>" } }
    } ]
  }'
```

Everything in that body is a named type in the `vmm` v4.1 spec: `bootConfig` is `LegacyBoot` or `UefiBoot`; a disk has a `diskAddress` (`busType` from `SCSI`, `IDE`, `PCI`, `SATA`, `SPAPR`, plus an `index`) and a `backingInfo` that is a `VmDisk` or a volume-group reference; a `VmDisk` can be sized and seeded from a `dataSource` whose reference is an `ImageReference`, a `VmDiskReference`, a volume disk or a recovery point; a NIC's `networkInfo` carries a `nicType` (`NORMAL_NIC`, `DIRECT_NIC`, `NETWORK_FUNCTION_NIC`, `SPAN_DESTINATION_NIC`) and a `subnet` reference. Minimum Prism Central pc.2024.3, minimum Prism Element 6.8. The VM is created powered off; `powerState` is read-only here and reports `ON`, `OFF`, `PAUSED` or `UNDETERMINED`.

## Step 6: power on, with the ETag

```bash
VM=<vm extId from step 5's task>
ETAG=$(curl -sS -u "$AUTH" -D - -o /dev/null "$PC/vmm/v4.1/ahv/config/vms/$VM" | awk 'tolower($1)=="etag:"{print $2}' | tr -d '\r')

curl -sS -u "$AUTH" -X POST "$PC/vmm/v4.1/ahv/config/vms/$VM/\$actions/power-on" \
  -H "NTNX-Request-Id: $(uuidgen)" -H "If-Match: $ETAG"
```

The GET returns the VM's current ETag; the action sends it back as `If-Match`. That is the specification's optimistic concurrency rule for every action and update on an existing resource, and it is the reason two automations cannot both change a VM they last read at different times. Skip the header and the answer is 428.

## Step 7: a floating IP on the NIC

```bash
curl -sS -u "$AUTH" -X POST "$PC/networking/v4.1/config/floating-ips" \
  -H "Content-Type: application/json" -H "NTNX-Request-Id: $(uuidgen)" \
  -d '{
    "name": "app-01-public",
    "association": { "$objectType": "networking.v4.config.VmNicAssociation",
                     "vmNicReference": "<NIC extId, from GET on the VM>" },
    "externalSubnetReference": "<extId of the NC2 external NAT subnet>"
  }'
```

A floating IP associates with a VM NIC, a private IP, or a load balancer session, and is allocated from an external subnet. On Google Cloud that external subnet is the Flow NAT range the previous post reserved as a `/27`; the address the VM gets is what the Cloud NAT path carries out. Nothing in the request names Google.

## The task loop that every step shares

```bash
poll() {  # $1 = task extId
  while :; do
    s=$(curl -sS -u "$AUTH" "$PC/prism/v4.1/config/tasks/$1" | jq -r .data.status)
    case $s in SUCCEEDED) return 0;; FAILED|CANCELED) return 1;; esac
    sleep 3
  done
}
```

Every POST above answers `202` with a task reference. The Prism namespace's task object carries `status` (`QUEUED`, `RUNNING`, `CANCELING`, `SUCCEEDED`, `FAILED`, `CANCELED`, `SUSPENDED`), `progressPercentage`, `entitiesAffected` with the `extId` of what was created, `subTasks`, and `errorMessages`. One poll function serves seven calls, and it serves the same seven on the other clouds.

## What this buys, in one sentence

The previous post needed three tools for three layers: Pulumi for Google Cloud, the NC2 console API for the cluster, and a bridged Terraform provider for the rest. From the moment Prism Central answers, the rest is one API at one version, reachable with `curl`, and the cloud is a value in a region field somewhere below it that these calls never read.

## Limits, so you design around the right ones

- **Rate limits are per Prism Central**, by its size, from the API User Guide: X-Small 30, Small 40, Large 60, Extra Large 80 requests per second. A fan-out across many clusters still lands on one Prism Central.
- **Hibernate and resume are not supported on Google Cloud**, so an automation that parks an AWS cluster overnight has no v4 equivalent here; that lives in the NC2 console API anyway, not v4.
- **No IPv6 on NC2 on Google Cloud.** The spec accepts an `ipv6` block on a subnet; the platform does not.
- **Three to twenty-eight nodes**, and node type and redundancy factor are fixed at creation, so `clustermgmt` cannot change them after the fact.

## What is sourced from where

Paths, minimum supported versions, request body types, enums and the `NTNX-Request-Id` and `If-Match` rules are from the v4.1 OpenAPI files Nutanix publishes for the `networking`, `vmm`, `clustermgmt` and `prism` namespaces (spec version 4.1.1, fetched from developers.nutanix.com on 2026-09-23), with the human-readable reference at developers.nutanix.com/api-reference. The security schemes, OData grammar and rate limit table are from the Nutanix API User Guide on nutanix.dev. Platform limits, the Flow subnet sizes and the GA release are from the NC2 on Google Cloud Deployment and User Guide dated August 25, 2026. The version lists per namespace move; re-read them rather than trusting a list written on a Wednesday. The same facts, kept current, live in the [Nutanix Knowledge Base](/nutanix/kb) on this site.
