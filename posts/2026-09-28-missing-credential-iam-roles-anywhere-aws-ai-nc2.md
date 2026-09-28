---
title: "The Missing Credential: How IAM Roles Anywhere Unlocks AWS AI on Nutanix Cloud Clusters"
date: 2026-09-28
time: 13:56
by: Alex Alvord
slug: missing-credential-iam-roles-anywhere-aws-ai-nc2
section: nutanix
summary: "Every hybrid AI conversation hits the same wall, and it is never bandwidth or the model. It is a credential. An AHV guest on NC2 is not an EC2 instance, so it has no instance profile and the SDK finds nothing. AWS IAM Roles Anywhere closes that gap with X.509 certificates and temporary credentials, which lets a fraud scoring VM call SageMaker and Bedrock over PrivateLink without refactoring, rehosting, or moving the regulated data off the cluster. Production shape is multi-AZ and multi-region on i7i metal. ASCII and Mermaid at every step."
---

Every hybrid AI conversation eventually hits the same wall, and it is never the one people expect. Not bandwidth. Not the model. A credential.

Picture a card issuer running Nutanix Cloud Clusters on AWS. The Nutanix stack sits on EC2 bare-metal instances inside their own VPC, running AHV. Production spans two Availability Zones in the primary region and replicates to a second region. A fraud scoring application runs there as an AHV guest: a queue consumer, a feature lookup against a ledger, a decision written back, and an audit trail somebody signed off on three years ago.

The team wants that application to call Amazon Bedrock and a SageMaker inference endpoint. Then somebody opens the AWS documentation, and every guide begins the same way. Attach an IAM role to the instance. The SDK picks up credentials from instance metadata automatically.

```
  EC2 instance                  AHV guest on NC2
  ────────────                  ────────────────
  instance profile attached     not an EC2 instance
  IMDS at 169.254.169.254       no instance profile
  SDK finds creds silently      SDK finds nothing
        │                              │
        ▼                              ▼
     it just works            <-- the wall every
                                  project hits
```

The AHV guest has no instance profile. It is not an EC2 instance. The bare-metal node underneath it is, but the guest is a virtual machine on a Nutanix hypervisor, and the instance-profile pattern simply does not describe it.

This is where most projects quietly do the wrong thing. Generate an access key, paste it into a VM template, move on. That key now lives in a golden image, rotates never, and turns up in an audit finding eighteen months later.

### The unlock

AWS IAM Roles Anywhere exists for exactly this shape of problem. In AWS's own words, it provides "temporary security credentials for your on-premises, hybrid, and multicloud workloads." It authenticates with X.509 certificates issued by your own certificate authority, and returns the temporary credentials of a real IAM role.

The guest presents a certificate. It receives short-lived credentials. It calls AWS services as a first-class IAM principal, with a role, a policy, and a CloudTrail record.

On the guest, it is one line of configuration:

```ini
[profile fraud-scoring]
region = us-east-1
credential_process = /usr/local/bin/aws_signing_helper credential-process \
  --certificate      /etc/pki/fraud-app.crt \
  --private-key      /etc/pki/fraud-app.key \
  --trust-anchor-arn arn:aws:rolesanywhere:us-east-1:111122223333:trust-anchor/EXAMPLE \
  --profile-arn      arn:aws:rolesanywhere:us-east-1:111122223333:profile/EXAMPLE \
  --role-arn         arn:aws:iam::111122223333:role/FraudScoringRole
```

Every AWS SDK understands that directive. Application code does not change. No key material in an image. The certificate becomes the identity, and certificate lifecycle is something enterprises already know how to operate.

### The path, end to end

```
                   Customer AWS VPC
 ┌───────────────────────────────────────────────────────┐
 │  NC2 cluster   (EC2 i7i metal · AHV + CVM)            │
 │                                                        │
 │   ┌─────────────────────┐   ┌────────────────────┐    │
 │   │ Fraud scoring app   │◄──┤ Ledger + card data │    │
 │   │ AHV guest           │   │ AHV guest, on NVMe │    │
 │   └──────────┬──────────┘   │ never leaves here  │    │
 │              │              └────────────────────┘    │
 └──────────────┼────────────────────────────────────────┘
                │
   (1) X.509 certificate   ──►  ┌──────────────────────┐
                                │  IAM Roles Anywhere  │
   (2) temporary credentials ◄──└──────────────────────┘
                │
                ▼  (3) signed calls, PrivateLink only
       ┌────────────┬─────────────┬────────────┐
       ▼            ▼             ▼            ▼
  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
  │SageMaker│  │ Bedrock │  │   S3    │  │  roles  │
  │  score  │  │narrative│  │features │  │ anywhere│
  └─────────┘  └─────────┘  └─────────┘  └─────────┘
       └──── all reached via interface endpoints ────┘
```


### What it actually unlocks

Once the credential problem is solved, the architecture that was always sitting there becomes available.

The fraud application stays exactly where it is. Card data and the ledger remain on cluster storage, on infrastructure the institution controls, never becoming an object in a managed service. Feature assembly and the audited rules stay in the guest. Only derived features cross the boundary.

Scoring goes to a SageMaker endpoint. High-risk cases go to Bedrock for an analyst narrative. Both travel over interface VPC endpoints, so traffic never touches the public internet. AWS is explicit that with PrivateLink you reach Bedrock "as if it were in your VPC, without the use of an internet gateway, NAT device, VPN connection, or Direct Connect connection."

Add the `rolesanywhere` endpoint to that list, or the credential exchange itself takes the public path and undoes the design.

| Concern | Where it lives | Why |
|---|---|---|
| Card data, ledger, PII | AHV guest, cluster NVMe | Never becomes an object in a managed service |
| Feature assembly, business rules | AHV guest | The audited code nobody wants to rewrite |
| Model scoring | SageMaker endpoint | Elastic, retrained without touching the VM |
| Analyst narrative on flagged cases | Bedrock | Generative work with no case for on-prem GPUs |
| Model artifacts, feature history | S3 | Cheap durable storage with lifecycle policies |

### The hardware makes the case easier

This pattern rewards keeping data local, and the current node types make that attractive. NC2 runs on AWS I7i metal instances. Nutanix put it plainly on the AWS launch page: bringing NC2 to I7i metal aligns with "delivering high-performance hybrid cloud solutions at a lower TCO."

I7i runs 5th generation Intel Xeon Scalable with PCIe Gen5 Nitro SSDs, up to 45TB of NVMe, 23 percent better compute than I4i, and 50 percent lower storage I/O latency. AWS lists relational and NoSQL databases, real-time analytics, and AI preprocessing among its target workloads.

A fraud ledger with a strict SLA is precisely that profile. Keep the data on fast local NVMe, and send only features to the model.

### Production posture

None of this is a single-cluster story. Production spans Availability Zones within the region and replicates to a second region.


```
  Region 1                            Region 2
 ┌──────────────────────────────┐    ┌──────────────────┐
 │  AZ-1             AZ-2       │    │  DR pod          │
 │ ┌───────┐        ┌───────┐   │    │ ┌───────┐        │
 │ │ Pod A │◄──────►│ Pod B │   │───►│ │ Pod C │        │
 │ └───────┘ Metro  └───────┘   │    │ └───────┘        │
 │           RPO 0              │    │                  │
 │                              │    │  SageMaker,      │
 │      AZ-3 · Witness          │    │  Bedrock, trust  │
 │      quorum + auto failover  │    │  anchors must    │
 │                              │    │  ALREADY exist   │
 └──────────────────────────────┘    └──────────────────┘
      VMs fail over.  Regional AI dependencies do not.
```

### Why this is the strategic point

The prevailing assumption in cloud AI is that an application must become something else before it can consume intelligent services. Containerize it. Rehost it. Refactor it into managed compute. Only then does it get to call the good APIs.

That assumption is expensive and, for a large class of workloads, unnecessary. A virtual machine in your own VPC on NC2 is already a network peer of every AWS service in that VPC. The only thing it lacked was a way to prove who it was.

IAM Roles Anywhere supplies exactly that. Nothing else has to change.

### Two honest edges

Certificate lifecycle becomes yours. Roles Anywhere moves the problem from key rotation to CA and certificate rotation. Better, not free.

Latency has a floor. Every inference call is a network round trip. Synchronous scoring inside an authorization path needs a budget and a documented fallback for when the endpoint times out.

There is a third edge, and it deserves its own article. Trust anchors, interface endpoints, SageMaker endpoints, and Bedrock model availability are all regional resources. When those virtual machines fail over to another region, the AI dependencies do not follow them automatically. A recovery plan that only proves the VMs booted has not tested the application. That is the next post.

### The takeaway

The barrier to running AI-enabled applications on Nutanix Cloud Clusters was never the infrastructure. It was an identity gap between a hypervisor guest and a cloud IAM model built for a different kind of compute.

That gap has a supported, auditable answer. Certificates in, temporary credentials out, full IAM semantics on the other side.

Worth an afternoon of anyone's time who has been told their workload has to move first.

---

*Sources: AWS IAM Roles Anywhere product and IAM documentation; Amazon Bedrock VPC interface endpoints; Amazon SageMaker interface VPC endpoints; Amazon EC2 I7i instance page, including the Nutanix statement on NC2 support; Nutanix portal documentation for NC2 on AWS. Amazon Fraud Detector is deliberately not used here: AWS closed it to new customers on 7 November 2025 and points to SageMaker, AutoGluon, and AWS WAF instead.*
