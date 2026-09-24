---
title: "Every episode has to beat the last one"
date: 2026-09-23
time: 22:10
by: Alex Alvord
slug: every-episode-has-to-beat-the-last-one
section: blog
draft: true
summary: "A generated series drifts unless something stops it. The fix is not better code review: it is scoring the finished artifact on axes a human named, and refusing to trade a regression on one axis for gains on four. The first thing the scorer caught was a bug in the scorer."
---

The lab runs a small cartoon podcast. One cloud-native concept an episode, a few minutes long, rendered by a pipeline rather than drawn by hand. Episode one shipped. The instruction that followed was one sentence, and it turned out to be the hard part:

> Each new episode should learn from the last and improve all around in animation, voice, presentation, color and execution.

That is not a feature request. It is a demand for a ratchet, and most creative pipelines do not have one. They have a generator, a person who looks at the output and says "yeah, that's good," and a slow drift that nobody can point at. By the third instalment nobody remembers precisely what the first one did right, because nobody wrote it down in a form that a later version could be checked against.

## Reviewing the generator tells you nothing about the output

The first instinct is to review the code. Read the renderer, tidy the constants, refactor the scene logic, feel better.

This does not work, and the reason is worth stating plainly: **the source will happily tell you everything is fine.** A palette declared at the top of a file looks complete. Six named colours, all spelled correctly, all plausibly chosen. Whether any of them reach the screen is a different question, and the file does not know the answer.

The same week, building a character rig for the same show, every single construction fault was invisible in the code and obvious the moment a frame was rendered and looked at. A hinge in the wrong place. A lid that deleted a face for two frames. A flat edge where an organic shape needed a taper. Not one of those was a logic error. The code ran perfectly and produced something subtly wrong.

So the rule for the scorer was decided before a line of it was written: **it reads the finished video, the finished audio and the script. It never reads the generator.** If the generator changes and the output does not, the score does not move, and that is correct.

## The axes come from the person, not from the tooling

There is a strong pull, once you decide to measure, toward measuring whatever is easy. File size. Render time. Frame count. All real, all nearly worthless as a description of whether something got better.

The five axes here were not chosen by whoever wrote the harness. They were named in the original sentence: animation, voice, presentation, colour, execution. The job of the tooling is to find an honest proxy for each of those, not to substitute a convenient one. Some of that is genuinely computable. Whether anything moved between frames. Whether the audio clips. Whether the narration sits at a pace a child can follow. Whether text meets a contrast standard against the surface behind it.

Some of it is not computable yet, and the ledger says so out loud. Whether the mouth lands on the syllable. Whether the eyes carry the joke. Those sit in a section marked open, because a metrics harness that quietly pretends to cover what it does not cover is worse than one that admits the hole.

## Per axis, never on average

This is the part that makes it a ratchet rather than a dashboard.

A composite score is an invitation to regression. Improve four things, break the fifth, watch the average go up, ship it. Do that four times and the thing is materially worse along one dimension and the number says it is better.

So the comparison runs per axis, and a regression on any one of them fails the run. Not as a warning, as a non-zero exit. The escape hatch is deliberate and narrow: a regression can be accepted, but only by writing a line in the ledger saying which metric moved backwards and why it was worth it. That costs about ninety seconds and it means every trade the series has ever made is written down in one file, in order, with numbers.

The point is not to make regressions impossible. It is to make them **expensive enough to be deliberate**.

## The first thing it caught was itself

Running the scorer against the existing episode produced a satisfying result: three of the six declared palette colours came back as flat zero. A clean story. The palette is a fiction, the show renders in three colours while claiming six, write it up.

It was wrong. Not the conclusion, the number. The metric reported each colour as a share of total pixels, and an accent that occupies a fraction of a percent of one frame in a couple of thousand rounds to zero at any sane precision. The colours were there. They were just very, very small.

Checking that against full-resolution stills before publishing the claim took about a minute, and it changed the finding from "these colours are absent" to something more useful and more damning: one of them appears as **three pixels, in one still, in the entire episode.** The metric now also reports the share of frames a colour appears in at all, which does not round away.

The lesson generalises past this pipeline. A measurement tool is an artifact too, and it deserves exactly the suspicion you point at everything else. The first run of any scorer is a test of the scorer.

## What it found that review had not

Without going through the specifics, the interesting thing is the *shape* of the findings. The harness did not catch bugs. The episode had no bugs. It caught things that a human reviewer watching the finished video had looked directly at and not registered:

- A text and background combination that falls below a published accessibility floor. Visible for the whole episode. Nobody flagged it, because it looks fine on a good monitor in a dark room, which is not where the audience is.
- A declared palette substantially richer than the rendered one.
- One segment more than twice the length of the average segment, in a format whose entire premise is short attention.

Each of those is the kind of defect that survives review indefinitely, because review is a person forming an overall impression, and an overall impression is exactly what a composite score is. Both of them average.

## This is not about cartoons

Any pipeline that emits an artifact on a repeating schedule has this problem. Generated documentation. Rendered dashboards. Infrastructure that is stood up from a template every sprint. Model output that goes in front of a customer. All of them drift, all of them are usually reviewed by looking, and almost none of them can tell you whether this week's output is better or worse than last week's along a dimension somebody actually cares about.

Three things make the difference, and none of them require much code:

1. **Score the artifact, not the source.**
2. **Let the axes be named by whoever the work is for**, then find honest proxies, and mark the gaps rather than papering them.
3. **Compare per axis and fail on any regression**, with a written, cheap, deliberate override.

The harness behind this one is about five seconds a run and has no dependencies worth mentioning. The hard part was never the code. The hard part was agreeing in advance what "better" was going to mean, and then being willing to let a machine tell us we had not achieved it.
