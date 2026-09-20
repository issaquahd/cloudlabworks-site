---
title: Low Code / No Code removes the barrier to entry for automation & orchestration!
date: 2021-07-15
time: 14:15
by: Alex Alvord
slug: low-code-no-code
summary: Automation is too complex and the barrier to entry is too high. IFTTT turned ten, the hyperscalers are coming for low code, and Nutanix Test Drive, Prism Central playbooks, and Beam already show what "stupid simple" looks like. Reposted from LinkedIn.
---

*First published as a [LinkedIn article](https://www.linkedin.com/pulse/low-code-removes-barrier-entry-automation-alex-alvord) on July 15, 2021. Reposted here so it lives alongside the rest of the lab notes. Product names and trial terms are as they were in 2021.*

---

![Nutanix Beam Cost Governance — the action gallery](/media/low-code-no-code-cover.png)

I am a huge fan of low code/no code. We have a huge "problem statement" in the USA: automation and orchestration is too complex and the barrier to entry is too high. It requires too many dependencies and a significant investment in one or more languages. In order to reap the benefits of automation and orchestration we must lower the barrier of entry.

A simple definition from the web on some of the benefits:

> Low-code platforms provide visual editors and reusable actions that users can drag-and-drop into processes for rapid development. Low-code development platforms enable IT to quickly assemble new processes and build applications without having to research, write, and test new scripts.

*The ability to automate tasks without being invested in languages (PoSH, Python, Bash, Go, etc.). The ability to automate tasks with visual editors. The ability to automate without researching, writing and testing new scripts (languages).*

You can also substitute "enable IT" to fit almost any noun. Enable humans, enable Ops, enable DevSecOps, enable consumers, enable end users.

We will all see a large push over the next 12–18 months with the hyperscalers (AWS, GCP, Azure) and some may argue OCI, Digital Ocean, OVH, among others in the low code/no code space, and eventually it will trickle down to OLPs and into the hands of folks trying to upskill.

Yes, bring it please! Imagine a world riddled with complexities in workflows of automation and orchestration suddenly opened by removing those barriers to entry — deep technical skills. I personally am looking forward to the diversity of thought and how that will improve automation at scale.

For those deep into automation & orchestration — none of this is new.

## Examples, examples, examples

The consumer application If This Then That (IFTTT) has a 10 year anniversary this September — IFTTT's initial release was September 7th, 2011. This September marks a decade of the most glaring and simple example of low code/no code. Check it out here:

- Android: [ifttt.com/android_device](https://ifttt.com/android_device)
- Apple: [ifttt.com/explore/ios-collection](https://ifttt.com/explore/ios-collection)

The application is very cool but really doesn't impact my current workflow as a Sr System Engineer and Cloud Architect. I want IFTTT for my role!

Here are some familiar low code platforms — ServiceNow, Workato, Bubble IO, Mendix, Microsoft Power Platform, etc… but those are platforms and not end states or workflows.

Where in the world can I see a finished product using some of these systems in the backend for creation?

The answer I came across is Nutanix Test Drive. A guided tour of the workflow that allows me to experience the low code/no code automation with minimal investment and minimal knowledge.

Nutanix offers a test drive for many of the platform options. Test Drive is delivered on top of K8s, allowing for endless opportunities to explore the experience of Nutanix: [nutanix.com/one-platform](https://www.nutanix.com/one-platform)

AI Ops and Automation is a great track as you can use Prism Central to create real time workflows using low code/no code. Check out the playbooks and action gallery. The action gallery has the visual editor and reusable action buttons. It's stupid simple!

Another great example of using Nutanix for low code/no code outcomes is our SaaS platform Nutanix Beam. Nutanix Beam is a FinOps SaaS application used to optimize public cloud resources (GCP FY22, Azure GA, AWS GA) and private cloud resources (Nutanix AHV GA). The end product is excellent, allowing for multi-tenant charge-back, budgeting, and flexible ways to visually show your resources by service type, geography, cluster or VM/container.

Nutanix Beam 90 day trial — for AWS you need your parent account that includes a CUR, and for Azure use your EA account which holds the billing aspects. Nutanix uses read-only API calls to comb through the billing metadata and in as little as 2 hours you have a baseline to start optimizing costs: [nutanix.com/products/beam](https://www.nutanix.com/products/beam)

The low code/no code is effective for eliminating waste with action buttons such as Cleanup EBS Snapshots, Cleanup AMIs, Create EBS Snapshots, and of course the ability to define your own low code/no code action buttons.

Keep calm and automate on!

---

*Originally published on [LinkedIn](https://www.linkedin.com/pulse/low-code-removes-barrier-entry-automation-alex-alvord), July 15, 2021. Reposted with light typo fixes and the bare URLs turned into links; the text is otherwise unchanged. The cover image is the Beam action gallery from the original article.*

Find me on [LinkedIn](https://www.linkedin.com/in/alexalvord/).
