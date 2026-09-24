---
title: "NC2 across AWS, Azure and Google Cloud: active/active/standby on the v4 API, with a native service beside each cluster"
date: 2026-09-24
time: 14:30
by: Alex Alvord
slug: nc2-active-active-standby-aws-azure-google-cloud
section: nutanix
summary: "The real point: a Nutanix UVM on NC2 sits in a plain VPC or VNet, so talking to a native cloud service next to it takes no Nutanix-specific plumbing at all — the v4 API sets up standard networking and gets out of the way. Proven with an active/active/standby pattern across AWS, Azure and Google Cloud (Prism Central's v4 dataprotection API for the failover, a data lake, a Function and a Looker instance for the native-service half) — and a straight look at where the two earlier build posts still lean on the console and the v2 API, and what full v4 buys back. ASCII at every step. Design pattern from the published v4 specs; not run end-to-end against three live clusters."
---

The point of this post is narrower than the diagram makes it look: **a Nutanix UVM is just a VM on a standard VPC or VNet subnet, so a native cloud service next to it is one networking hop away, not a Nutanix integration project.** The active/active/standby pattern below is the proof, because DR is the workload most likely to expose sloppy networking — if a data lake, a Function and a BI tool can keep working across a live failover without a single Nutanix-specific hook, the easy case (a UVM calling S3 on a Tuesday) was never in question.

The three build posts (AWS, Azure, Google Cloud) each stopped at one running VM. The question underneath all three was always the next one: put a workload on all three, keep two of them serving and one caught up and cold, and do the failover with the same v4 API that built the VM. Nutanix's cross-cluster building blocks are `dataprotection` protection policies and recovery plans, spoken over Prism Central's v4 API exactly like the `vmm` and `networking` calls in the earlier posts — and none of it needs the receiving side to be the same cloud, because the API never sees the cloud, only the cluster.

Worth being honest about where those earlier posts actually left their customers. The [AWS post](/nutanix/nc2-aws-as-code-nc2-console-to-first-vm) built the cluster and Prism Central through the **NC2 console** (a UI, not the v4 API) and only picked up v4 for what came after — VPCs, subnets, the VM. The [Azure post](/nutanix/nc2-azure-as-code-bicep-to-first-cluster) went further on automation (Bicep, no console click) but the organization, cloud account and cluster still came from the **NC2 v2 API**, with v4 arriving at the same point AWS's did. Neither customer has fully migrated: the lifecycle layer (org, account, cluster) is still v1/v2, and only the operational layer (network, compute, storage) is v4. Only the [Google Cloud day-one post](/nutanix/nc2-gcp-day-one-pure-v4-api) ran the whole sequence, cluster included, on v4 alone. This post's DR half — availability zones, protection policies, recovery plans — is v4-only on all three clouds regardless of how the cluster itself was born, because `dataprotection` has no v1/v2 predecessor to fall back to.

### Why the migration is worth finishing

- **One API family, every layer.** Today an AWS or Azure customer scripts the cluster in one API generation and the network/compute/storage in another — two auth flows, two response shapes, two things to version. Full v4 collapses that to one.
- **One task-polling model.** Every v4 mutation in this series — VM create, VPC create, protection policy, recovery plan — returns the same task envelope, polled the same way. v1/v2 console operations do not; they are UI state, not a resource you can poll from your own pipeline.
- **The native-service story gets easier, not harder.** Because v4 `networking` is what stands up the VPC/VNet a UVM lives in, the same IaC that creates the cluster's network can also create the S3 gateway endpoint, the Event Grid topic's private link, or the BigQuery-facing service connection — one pipeline, not a handoff from a console-driven network to a hand-built peering.
- **Idempotent and diffable — the part that actually changes how a team operates.** A v4 resource body is the full desired state, not a verb; `PUT` the same VM spec twice and the second call is a no-op, not a duplicate or an error. That is what lets a tool like OpenTofu compute a plan — additions, changes, destroys — *before* anything happens, against the live cluster, not against a changelog someone kept by hand. Console clicks and v2's imperative calls ("create this," "attach that") have no such plan step: there is no diff to review, only an audit log after the fact of what already happened. Three practical effects follow directly: drift detection (a manual console change shows up as a diff on the next `plan`, instead of silently rotting the IaC's picture of reality); safe re-runs (a failed apply, a flaky network call, a retried CI job — all idempotent, so re-running is the fix, not a new problem to reason about); and code review for infrastructure changes (a `plan` output is a diff, which means it can go through the same pull-request review as application code, instead of a screen-share of someone's console session). The AWS and Azure posts both hit this wall exactly at the console/v2 boundary: everything after cluster creation is diffable; the creation step itself is not, and has to be treated as a one-time, undiffable fact the rest of the pipeline works around.

### Why this matters most to a customer vacating an SDDC

The customer this pattern is actually for is not greenfield — it is the one mid-migration off a VMware SDDC, still running vSphere/NSX/vSAN on one side and standing NC2 up on the other, for as long as that takes. Three things about v4 matter disproportionately to exactly that customer:

- **The migration itself becomes a diffable plan, not a runbook.** A `plan` against v4 resources shows precisely what a wave of VMs moving off the SDDC will create, in advance, reviewable before a single workload actually cuts over — the same confidence a `terraform plan` gives an AWS migration, applied to the Nutanix side of a hybrid estate that used to have no plan step on either end.
- **Idempotency forgives a migration's inevitable false starts.** Migration waves get retried, paused, and re-run against partially-moved state more than almost any other IaC workload; a `PUT` that no-ops on an already-created VM is the difference between a safe re-run and a bespoke cleanup script every time a wave stalls.
- **One API for the destination end of the migration, matching the source end's own IaC.** A team already scripting the SDDC side with Terraform/vSphere providers is not learning a new operational model for the NC2 side — v4's declarative, pollable, diffable shape is the same shape, so the migration tooling on both ends of the move looks like one discipline instead of two.

This is also, not incidentally, where the DR pattern above stops being a nice-to-have: a customer vacating an SDDC rarely gets to cut over instastantly, so an SDDC-side workload and its NC2-side replacement often have to run **as** an active/active or active/standby pair for the migration window itself, before the SDDC is ever decommissioned — which is exactly the `dataprotection` shape this post already walked through, just with one leg still on-prem instead of a third cloud.

The second half of this post is the other direction: what the clouds are for, once NC2 is not doing it for you, and how little stands between a UVM and each one. A data lake (AWS), an event-driven function (Azure), a BI tool over a warehouse (Google Cloud) — three services with no Nutanix equivalent and no reason to fake one. They sit beside the cluster, reading and writing over VPC/VNet peering that the same v4 `networking` calls already provisioned, never inside the failover path, so a region failing over does not also fail over your BigQuery-backed dashboard — and never touched by anything Nutanix-specific, because there is nothing Nutanix-specific to touch.

Everything below is a design pattern built from the published v4 OpenAPI specifications (`dataprotection`, `networking`, `vmm`, `clustermgmt`, spec version 4.1.1) referenced in the three build posts and the NC2 Deployment and User Guides for each cloud, read 2026-09-24. I have not run this exact three-cloud sequence against three live clusters, and I am not writing it as though I had — where a guide and a block here disagree on your version, the guide wins.

## The map

```text
 ┌─ AWS · us-west-2 ── ACTIVE ─────────────┐     ┌─ Azure · westus2 ── ACTIVE ──────────────┐
 │  NC2 cluster + Prism Central A          │     │  NC2 cluster + Prism Central B            │
 │   └─ App/DB VMs, serving traffic        │     │   └─ App/DB VMs, serving traffic          │
 │  beside it, not in the failover path:   │     │  beside it, not in the failover path:     │
 │   S3 + Glue + Athena  (data lake)  ◀────┼─VPC─┤   Event Grid ─▶ Azure Function  (FaaS)    │
 └───────────────┬──────────────────────────┘     └───────────────┬────────────────────────────┘
                 │ dataprotection v4: protection policy            │
                 │ (sync/async), recovery points                   │
                 ▼                                                  ▼
          ┌──────────────────────────────────────────────────────────────┐
          │           PC-to-PC availability zone pairing (mutual)        │
          │           A ⇄ B replicate to each other; both replicate      │
          │           to the standby below                              │
          └───────────────────────────┬────────────────────────────────┘
                                      │ dataprotection v4: recovery plan
                                      │ (ordered VM boot, network mapping)
                                      ▼
                 ┌─ Google Cloud · us-west1 ── STANDBY ───────────────────┐
                 │  NC2 cluster + Prism Central C                        │
                 │   └─ Recovery points only; VMs registered, powered off │
                 │  beside it, reachable once promoted:                  │
                 │   BigQuery / Cloud SQL ─▶ Looker  (BI)                │
                 └─────────────────────────────────────────────────────────┘

 Failover:  recovery plan C executes ─▶ power on in dependency order ─▶
            re-IP or re-attach floating IP ─▶ traffic follows ─▶ A/B unregister
 Failback:  reverse protection policy direction, resync, repeat
```

## Step 1 — three clusters that already exist

Nothing here builds a cluster; that is the three earlier posts, one per cloud:

- [NC2 on AWS, as code](/nutanix/nc2-aws-as-code-nc2-console-to-first-vm) — NC2 console + OpenTofu on the v4 API.
- [NC2 on Azure, as code](/nutanix/nc2-azure-as-code-bicep-to-first-cluster) — Bicep landing zone + NC2 v2 API.
- [NC2 on Google Cloud, day one](/nutanix/nc2-gcp-day-one-pure-v4-api) — pure v4 API, no console.

The precondition for everything below: three Prism Central instances, each answering on `:9440`, each with at least one registered cluster and a VM image already in place.

## Step 2 — pair the Prism Centrals (availability zones)

Cross-cluster DR in Prism Central is built on "availability zone" pairing between Prism Centrals, not between clusters directly. Each pair is a one-time trust setup: PC A and PC B exchange certificates and register each other as a remote availability zone, then PC B and PC C do the same, then A and C. This is the only step that is not a v4 `dataprotection` call in the current spec generation — it is a Prism Central admin action (Settings → Availability Zones), done three times for a three-way mesh:

```text
   PC A (AWS) ───pair─── PC B (Azure)
       \                    /
        \__pair────pair___/
              PC C (GCP)
```

## Step 3 — protection policies, v4 `dataprotection`

A protection policy is what makes a VM's disks eligible for replication and states where recovery points land and how often. For the two active legs replicating into the standby, the policy is asynchronous (RPO measured in minutes, not synchronous mirroring — cross-cloud WAN latency rules out zero-RPO here):

```http
POST https://<PC-A-or-B>:9440/api/dataprotection/v4.1/config/protection-policies
{
  "name": "aws-to-gcp-standby",
  "replicationConfigs": [
    { "sourceLocationLabel": "PC-A-AWS",
      "targetLocationLabel": "PC-C-GCP",
      "schedule": { "recoveryPointObjectiveTimeSeconds": 900 } }
  ],
  "category": { "key": "app-tier", "value": "active-active-core" }
}
```

The same body shape runs against PC B for `PC-B-Azure → PC-C-GCP`. Two policies, one target, both async, both scoped to a category so any VM tagged `app-tier:active-active-core` is covered without a per-VM edit later.

## Step 4 — recovery plan, v4 `dataprotection`

The recovery plan is the failover script: which VMs power on, in what order, on what network, at the standby side. It is a resource, not a one-shot action, so it can be dry-run (validated) long before it is ever executed:

```http
POST https://<PC-C-GCP>:9440/api/dataprotection/v4.1/config/recovery-plans
{
  "name": "promote-gcp-standby",
  "stages": [
    { "stageWork": { "recoverEntities": { "entities": [
        { "anyEntityReference": { "categoryReference": { "key": "app-tier", "value": "active-active-core" } } }
      ] } },
      "durationBetweenStageMinutes": 2 }
  ],
  "primaryLocation": { "locationReference": "PC-A-AWS" },
  "recoveryLocation": { "locationReference": "PC-C-GCP" }
}
```

Validate before you ever need it:

```http
POST /api/dataprotection/v4.1/config/recovery-plans/{planId}/$actions/validate
```

## Step 5 — the failover call, and the poll

Executing a recovery plan is one call; like every other v4 mutation in this series it returns a task to poll, not a result:

```http
POST /api/dataprotection/v4.1/config/recovery-plans/{planId}/$actions/failover
{ "failoverType": "PLANNED" }
```

`PLANNED` assumes the primary is reachable and does a clean shutdown first; `UNPLANNED` skips that and is the one you use when AWS and Azure are both actually down, not drilled. Poll `/api/prism/v4.1/config/tasks/{taskId}` the same way the single-cloud posts did until `status: SUCCEEDED`; the VMs come up on PC C in the order the stages defined, and floating IPs re-attach on the Google Cloud side per the earlier GCP post's networking calls.

Failback is the same shape, reversed: a protection policy from C back to A (or B), a recovery plan promoting A, executed once the original region is confirmed healthy and resynced.

## The three native services — beside the cluster, never inside the API path

None of these are Nutanix resources. That is the point: NC2's v4 API stops at the VM, the disk and the network. Everything below reads from or writes to the VMs over a VPC/VNet endpoint, on the active side only, and is entirely absent from the failover call above.

```text
 AWS (active) ── VM writes events ──▶ S3 (raw) ──▶ Glue Catalog ──▶ Athena
                                         "the data lake": land it, catalog it, query it in place

 Azure (active) ── VM emits ──▶ Event Grid topic ──▶ Azure Function
                                         "FaaS": react to an event, no server to patch or fail over

 Google Cloud (standby, promoted) ── BigQuery / Cloud SQL ──▶ Looker
                                         "the BI layer": stays cold with the cluster, wakes with it
```

- **AWS data lake:** the active-side VMs write append-only events to an S3 bucket in the same VPC (gateway endpoint, no NAT egress); a Glue crawler catalogs the schema; Athena queries it directly. No compute to fail over — S3 and Glue Catalog are already regional-durable, so this leg needs nothing from the DR plan above.
- **Azure Function:** the active-side VMs publish to an Event Grid topic; a Function subscribes and does the small stateless thing (notify, transform, write a row) that would be wasteful to run on a VM 24/7. If Azure is the side that fails over, the Function goes dark with it — deliberately not part of the recovery plan, because there is nothing to recover, only to redeploy from its own IaC once the region is back.
- **Google Looker:** sits over BigQuery/Cloud SQL on the Google Cloud side. While GCP is standby this is quiet; the moment the recovery plan promotes PC C, the underlying data source is live NC2 VMs again and Looker's dashboards start reflecting them; no Looker-specific step in the failover.

## What this pattern does not claim

Three-way availability-zone pairing, two async protection policies and one recovery plan is the minimum shape for active/active/standby; it is not a substitute for reading your own RPO/RTO requirement against async replication's real floor (minutes, driven by cross-cloud WAN, not seconds). `UNPLANNED` failover on real data loss and `PLANNED` failover as a drill are different operations with different blast radii — treat the first as a last resort, not a monthly exercise. And the native-service half is illustrative, not exhaustive: any AWS/Azure/Google Cloud managed service that talks to a VPC endpoint fits the same "beside the cluster, not inside the API path" rule.
