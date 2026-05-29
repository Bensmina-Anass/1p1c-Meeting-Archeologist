# 1 prompt 1 project team :) Meeting archeologist. the only extension you need in your long boring meetings


## What is this?

Meeting Archeologist is a system that analyzes meeting transcripts the way a team of specialists would — not just one person reading through notes, but multiple experts each looking at the same conversation from a different angle.

## The problem

When someone reads meeting notes, they bring one perspective. They might catch the action items but miss a strategic shift. They might spot a risk but overlook a deadline. And when meetings pile up over weeks, contradictions between decisions slip through — nobody remembers that last month's direction was the opposite of today's.

A single AI reading a transcript has the same limitation: one perspective, one pass, one blind spot pattern.

## The approach

Instead of one AI analyzing everything, Meeting Archeologist uses three specialized analysts working in parallel on the same transcript:

- **The Action Analyst** focuses on accountability: who committed to what, by when, and what depends on what.
- **The Strategic Analyst** focuses on direction: what decisions were made, what priorities shifted, and why.
- **The Risk Analyst** focuses on what could go wrong: unresolved questions, missing owners, unrealistic timelines, and contradictions with past meetings.

Each finding is grounded in a verbatim quote from the transcript (`source_quote`), so every extracted item can be traced back to the exact sentence that produced it.

Because all three read the same transcript, they often identify the same items — but frame them differently. A budget cut might be an "action" to one, a "strategic pivot" to another, and a "risk" to the third.

A fourth agent — the **Consensus Agent** — takes all three outputs, finds where they agree, flags where they disagree, and produces a single unified meeting summary with confidence scores.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Meeting Transcript                       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │     Orchestrator     │
                    │      (main.py)       │
                    │  loads transcript,   │
                    │  drives both crews   │
                    └──────────┬──────────┘
                               │
              ╔════════════════╧═════════════════╗
              ║          Crew 1 — parallel        ║
              ╠══════════════════════════════════╣
              │                │                 │
   ┌──────────▼──────┐ ┌───────▼───────┐ ┌──────▼──────────┐
   │  Action Analyst  │ │  Strategic    │ │  Risk Analyst   │
   │                  │ │  Analyst      │ │                 │
   │  action items    │ │  decisions    │ │  risks          │
   │  owner           │ │  rationale    │ │  severity       │
   │  deadline        │ │  priority     │ │  category       │
   │  depends_on      │ │  shift        │ │  contradictions │
   │  source_quote    │ │  source_quote │ │  source_quote   │
   └──────────┬───────┘ └───────┬───────┘ └──────┬──────────┘
              └─────────────────┼─────────────────┘
                                │
              ╔═════════════════╧════════════════╗
              ║          Crew 2 — sequential      ║
              ╠══════════════════════════════════╣
                                │
                    ┌───────────▼─────────┐
                    │   Consensus Agent    │
                    │                      │
                    │  agreements          │
                    │  conflicts           │
                    │  unified summary     │
                    │  confidence score    │
                    └───────────┬──────────┘
                                │
                    ┌───────────▼──────────┐
                    │     SQLite Memory     │
                    │                       │
                    │  meetings   tasks     │
                    │  decisions  risks     │
                    │  consensus_results    │
                    └───────────────────────┘
```

## The core question

Can a well-orchestrated team of small, specialized AI agents produce better meeting analysis than a single, general-purpose AI doing everything alone?

The hypothesis: architecture matters more than model size. Three focused perspectives plus consensus beats one broad pass.

## Who is this for?

This is an academic project for the Multi-Agent Systems course at ENSIAS (École Nationale Supérieure d'Informatique et d'Analyse des Systèmes), Université Mohammed V, Rabat. It demonstrates key MAS properties: agent specialization, parallel execution, shared memory, and consensus-based conflict resolution.

## Authors

Bensmina Anass & Moubarak Benaqqa
