---
title: "Show us your screens: seventy years of computer music, and a lab that plays its own state"
date: 2026-09-23
time: 07:00
by: Alex Alvord
slug: show-us-your-screens-live-coding-to-infrastructure-as-music
section: blog
draft: true
summary: Live coding has a founding document with one rule in it, written in a Hamburg bar in 2004. The rule applies to infrastructure better than anyone at the time could have known. The lineage from a monk with a four-line staff to Sonic Pi, and what it looks like when the performer is a set of agents and the input is a lab's own health.
---

There is a history page on this site now, under Site, and it is there because the lab's strangest feature has a family tree. Code as Music, the instrument at the top of `/live`, is a Sonic Pi program. Sonic Pi is a 2013 branch of live coding. Live coding got its name in 2004. The thing it names reached a computer in 1957, and a monastery around 1025. The dates below come from the three sources at the end; the argument is mine.

## A thousand years, in one column

| Year | What happened | Why it is on this page |
|---|---|---|
| c. 1025 | Guido d'Arezzo encodes music on a four-line staff, and describes a table-lookup procedure for turning text into melody | Notation is the first musical programming language; text to music by rule is not a 2020s idea |
| 18th century | The musical dice game: 176 fragments, dice for selection, every combination harmonically coherent by design | The constraint is the intelligence, not the randomness |
| 19th century | Programmable carillons, pneumatic orchestrions playing dozens of instruments from perforated rolls | Automated performance with expression, written into the roll |
| 1957 | Hiller and Isaacson's Illiac Suite: a string quartet composed partly by computer | Music from logic, before anyone could hear a computer speak |
| 1985, then 2019 | IRCAM's CHANT: the manual survives, the rule layer does not | What it looks like when the score is not in git |
| late 1950s | Max Mathews writes MUSIC I at Bell Labs; the 1962 Science article follows | The first program that made sound itself; the MUSIC-N family underlies everything after |
| 1990, 1996 | Max, then Pure Data and SuperCollider | The tools become playable in real time; SuperCollider goes free in 2002 and is still the engine under much of the field |
| Feb 2004 | TOPLAP founded in Hamburg; the "Read Me" | "Show us your screens": the code is part of the performance |
| 2009 | Tidal Cycles | Music as infinite cycles of patterns; a language you can rewrite while it runs |
| 17 Mar 2012 | The first algorave, London | Code projected large, performers visibly thinking, mistakes included |
| 2013 | Sonic Pi, Cambridge and the Raspberry Pi Foundation | Code as pedagogy; the instrument this lab runs |
| 2015 | First International Conference on Live Coding, Leeds | The academic and club branches in one room |
| 2022 | Strudel: Tidal in the browser | No install; the pattern engine in any tab |
| Feb 2024 | TOPLAP at twenty | A community whose one shared habit is writing code in public |
| 19 May 2024 | Live Code panel at the Museum of the Moving Image | The performance itself, code on a screen in front of an audience, is the artwork; and the practice has a visual half going back to the mid-1980s |
| Mar to Jun 2026 | Kenneth Reitz, Music as Code: PyTheory, NumPy as synth engine, an album of twenty-four Python scripts | The score is the script; the same premise as this lab, arrived at from the drum stool |

## The rule

The TOPLAP Read Me is short and most of it is optional. The part that stuck is one instruction: if you perform with a computer, project the screen. Do not hide the thinking behind an interface. The audience should watch the code change and hear the change land.

Read that as an infrastructure rule and it is uncomfortable. Most operations work is performed with the screen turned away: a change goes in, a dashboard goes green, and the audience (the people who depend on the system) sees the result and never the reasoning. When the change is wrong, the screen stays turned away a little longer.

## The lab, with the screen projected

Code as Music takes the rule literally. The Sonic Pi program on this site is not played by a person. Its input is the lab's own state file: every site answering or not, the last deploys, the last faults. While everything answers it plays E major, a slow plucked arpeggio and an airy pad. When something is down it drops to minor, slower, with a low tone underneath. When a deploy lands, a rising bell figure. The score is code in git; the browser holds a second copy of the instrument so nothing streams from the lab. A visitor cannot see the cluster, but they can hear it, and the recording of each fault, recovery and deploy is kept, twenty seconds around each event, assembled nightly.

That is the algorave half of the lineage: the process made audible, mistakes included. The Sonic Pi half, code as pedagogy, is the rest of the site. The architecture decisions are published as they are made, identifiers masked. The test pipeline shows planned, running and failed tests with sanitized reasons. The reading list carries what each paper changed here. None of it is polished after the fact. Show us your screens, for infrastructure, means the performer's mistakes are part of the record, and the performer here is a set of agents operating the lab under boundaries, receipts and a budget.

## What it costs

There is an older exhibit for why the score lives in git. In 2019 a researcher went looking for the source of CHANT, IRCAM's synthesis program, and was told in public that it was lost. An IRCAM staff member corrected it: not lost, on an internal server, but the surviving implementation is a decades-old command-line tool that dropped the rule layer, the part that governed how synthesis parameters depend on each other and change over time. The binary runs behind a subscription. The 1985 manual reached the thread as a download link that had expired by the time the next person asked for it. The sound outlived the reasoning, which is the ordinary failure mode for infrastructure too.

Projecting the screen has a price the Read Me does not mention: you have to build the projector. A health signal the instrument can trust has to come from somewhere the state file cannot reach, or the music is a mirror of what the lab wrote about itself rather than a check on it. A published test has to have a pass condition someone else can verify, or it is a wish with a date. A recording has to be assembled without a human in the loop, or it stops the first busy week. The lab learned each of those the expensive way, and the decisions are on the ASR page.

The Hamburg group wrote their rule for a room with a laptop and a projector. Twenty-two years on, the room is a rack in Duvall and the projector is a website, and the rule holds: the cursor is blinking, and whatever happens next is on the screen.

Sources for the dated entries: Michael Filimowicz, [The Ancient Code: How Musical Intelligence Was Born Centuries Before Computers](https://michael-filimowicz.medium.com/the-ancient-code-how-musical-intelligence-was-born-centuries-before-computers-4090bb293e3a); Soniare, [The History of Live Coding: From Bell Labs to the Algorave](https://www.soniare.net/blog/history-of-livecoding); Kenneth Reitz, [Music as Code](https://kennethreitz.org/themes/music-as-code); Museum of the Moving Image, [Live Code: Real-Time Visual Music Since the 1980s](https://movingimage.org/event/live-code/); IRCAM Forum, [CHANT source code](https://discussion.forum.ircam.fr/t/chant-source-code/20309). The lab's timeline, with these entries and its own, lives at [/history](/history).
