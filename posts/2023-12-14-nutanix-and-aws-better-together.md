---
title: Nutanix and AWS, Better Together!
date: 2023-12-14
time: 10:03
by: Alex Alvord
slug: nutanix-and-aws-better-together
summary: In 1930 Indiana Bell rotated a 22-million-pound building 90 degrees with 600 people working inside and nobody felt it move. Ninety years later a workload move to cloud should feel the same — the NC2 on AWS recipe for datacenter divestment, L2 stretch, and refactoring on your own time and dime. Reposted from LinkedIn.
---

*First published as a [LinkedIn article](https://www.linkedin.com/pulse/nutanix-aws-better-together-alex-alvord-xdblf) on December 14, 2023. Reposted here so it lives alongside the rest of the lab notes.*

---

![The Indiana Bell building being rotated, 1930](/media/nutanix-aws-better-together-cover.gif)

Nutanix Cloud Clusters on AWS are laser aligned for datacenter divestment, application modernization, workload portability and, if it's in your future, a cutover to AWS native. Nutanix has a platform for application modernization, excels at cloud commit burndown and helps show the hyperscalers you are meeting your commits.

When I think about the alignment between Nutanix and AWS I can't help but think back to this magnificent engineering triumph; the scaffolding, automation and framework with tons of preplanning helped execute this marvel during a time when technology innovation was mostly in infancy and forming in the ether.

In 1930 the Indiana Bell building was rotated 90 degrees. Over a month, the 22-million-pound structure was moved 15 inches an hour… all while 600 employees still worked there. There was no interruption to gas, heat, electricity, water, sewage, or the telephone service they provided. No one inside felt it MOVE.

90 years later, shifting workloads to the cloud should be the same — seamless and invisible to the customer (internal and external).

Why shouldn't I have my cake and eat it too? Bell, in my opinion, not only solved this incredibly diverse set of problem statements, they did it with grandeur! A modern marvel of the 1930's.

## Workload portability

Movement of a workload from one environment to another isn't an easy endeavor. It involves thorough planning, coordination, and execution. The most common and impactful decision that companies make is whether to run their workloads on-premises or in public cloud. Other options like edge, hosted and colocation environments would fall into the same decision-making bucket, as these don't involve the major migration exercise that organizations need to undertake in the case of movement from on-premises to public cloud — the application modification.

There are six approaches to cloud migration, most of which involve some form of application modification:

- Rehosting
- Replatforming
- Refactoring
- Repurchase
- Retire
- Retain

For this example we are focusing on the first three. Nutanix can help immensely with Retain and Repurchase as well. How do Nutanix Cloud Clusters and AWS align to divest from the on-prem datacenter and have our apps quickly shift to cloud?

Single cloud operating model! Single substrate!

Here is what makes the recipe bake the best hybrid cloud platform in the ether:

- Bring Your Own AWS Account. Bring Your Own Nutanix Account.
- Strong APIs (Nutanix and AWS both live up to this very well)
- AWS Marketplace
- Layer 2 Stretch / Layer 2 Extension (L2S)
- UVM — User VM inside Nutanix software on top of AWS bare metal
- Native AWS networking (ENI / Nitro cards)

This recipe combined with a single operating model and substrate allows for unique value to shrink your timeline on deriving value (innovation — that's why we go to cloud).

**Layer 2 stretch:** at Nutanix we use a generic VyOS device with a couple of VTEP gateways at source and destination. This allows me to extend my on-prem subnets to NC2 AWS and replicate those VMs/applications out without changing IP.

**UVM:** an application/utility/VM that resides inside the Nutanix Cloud Cluster. All UVMs in NC2 AWS have a native AWS IP.

Info on AWS Elastic Network Interfaces (ENIs) and Nitro cards — ENI: [New Elastic Network Interfaces in the Virtual Private Cloud](https://aws.amazon.com/blogs/aws/new-elastic-network-interfaces-in-the-virtual-private-cloud/); Nitro: [The Security Design of the AWS Nitro System](https://docs.aws.amazon.com/whitepapers/latest/security-design-of-aws-nitro-system/security-design-of-aws-nitro-system.html).

Some core attributes of ENIs:

- Description
- Private IP address
- Elastic IP address
- [MAC address](https://en.wikipedia.org/wiki/MAC_address)
- Security group(s)
- Source/destination check flag
- Delete on termination flag

So, I have the best of both worlds. An operating model that allows me to tap into my existing broadcast domain, extend it to AWS and have a platform with guardrails to deliver a more efficient, FinOps-driven model where I can refactor and retool on my time and my dime.

Post deployment, my UVMs are connecting directly to my AWS data lakes and I am tapping into EKS Anywhere for proximity to native services, and if I have a use case, I can hit go and cut over that app to a native service!

The world is your hybrid oyster!

Here are some great resources to explore:

- [nutanixbible.com](https://www.nutanixbible.com/)
- [nutanix.com/one-platform](https://www.nutanix.com/one-platform)
- [developer.nutanix.com](https://www.developer.nutanix.com/)
- [aws.amazon.com](https://aws.amazon.com/)

---

*Originally published on [LinkedIn](https://www.linkedin.com/pulse/nutanix-aws-better-together-alex-alvord-xdblf), December 14, 2023. Reposted with light typo fixes and LinkedIn's redirect links replaced by the direct URLs; the text is otherwise unchanged. The cover animation is the one from the original article.*

Find me on [LinkedIn](https://www.linkedin.com/in/alexalvord/).
