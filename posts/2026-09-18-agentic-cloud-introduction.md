---
title: Agentic Cloud — An Introduction
date: 2026-09-18
time: 21:00
by: Alex Alvord
summary: Who is writing this, where he is from, and why a cloud architect with twenty-five years of wires behind him is spending his nights on harnesses and agents.
---

I am Alex. Born and raised in the Pacific Northwest, still here — Duvall, Washington, on the wet side of the Cascades, where the lab lives in a rack and the weekends live outside. Rivers, bikes, a playground with my kids, and then back to the bench.

By trade I am a cloud architect. Hybrid multicloud, which is a long way of saying I help companies run the same platform on their own floor and inside AWS, Azure, and Google Cloud without losing track of the boundaries between them. I have done that since 2020 at Nutanix, most of it on the Cloud Clusters team, and for a couple of decades before that in every form the data center has taken: enterprise architecture, hosted private cloud, one of the first multi-cloud orchestration shops, and a point-of-sale system I wired up as a kid who thought he was going into finance.

The receipts are on the [work page](/work). This post is about what comes next.

## What I am working on now

Harnesses and agentic engineering. Not chatbots — the plumbing around them.

A harness is the thing that decides what an agent is allowed to do, what it must write down, and what it has to undo before it tries again. I spend my nights building one: a persona compiled from files, a memory that lives in git, a written constitution that says money, third parties, publishing, and my employer's systems need a human, and everything else proceeds and logs. It runs the lab. It wrote half of the first post on this blog and it will deploy this one.

The clouds are the other half. The same agent patterns have to work across AWS, Azure, and Google Cloud, on bare metal in someone else's data center, and on an ARM cluster the size of a lunchbox under my stairs. If a design only works on one of those, it is a demo, not a design.

## Why I am loud about AI

Because I have watched this movie before. Virtualization, then infrastructure-as-a-service in 2007, then multicloud, then the cost bill that arrived after each of them. Every wave was oversold at the front and under-operated at the back, and the people who got value were the ones who treated it as infrastructure: owned it, measured it, gave it an undo.

Agents are the same. I am an advocate — a loud one — because the work is real and the runway is short, and because the alternative is letting the vendors and the hype cycle decide how this gets run. It should get run the way the rest of the stack gets run: with boundaries, receipts, and someone whose name is on it.

## What is under the belt

Twenty-five years, three hyperscaler architect certifications, a user group I founded and still run, a couple of awards from a company I am proud to work for, and a lab that has been rebuilt more times than I will admit in print. Enough to know what breaks. Not enough to stop being surprised by what breaks next.

That is the blog. Concrete, from the bench, with the commit hash attached.
