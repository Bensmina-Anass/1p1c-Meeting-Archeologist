# Execution Plan — Meeting Archeologist

4-day sprint. Each day has a clear deliverable. Don't move to the next day until the current one works end-to-end.

---

## Day 1 — Foundation + Corpus

**Goal:** Everything runs, nothing is smart yet.

**Morning:**
- Set up the project folder structure and Git repo
- Install dependencies: CrewAI, llama-cpp-python, sqlite3, sentence-transformers or TF-IDF tooling
- Download and test Qwen 2.5 7B Instruct (Q4) via llama-server with `--parallel 6`
- Verify you can hit the local LLM endpoint from Python and get a response

**Afternoon:**
- Define the JSON schema for meeting transcripts (date, participants, agenda, raw text)
- Define Pydantic output models for each agent (ActionOutput, StrategicOutput, RiskOutput, ConsensusOutput)
- Generate 10 synthetic meeting transcripts with planted contradictions, overlapping items, and ambiguous ownership
- Set up SQLite schema: tables for decisions, tasks, risks, consensus results, and meeting metadata
- Write the basic read/write functions for the memory layer

**Deliverable:** You can load a transcript, call the LLM, parse a response into a Pydantic model, and write/read from SQLite. The agents don't exist yet, but the plumbing works.

---

## Day 2 — Agents + Pipeline

**Goal:** All agents work individually and together.

**Morning:**
- Build the 3 analyzer agents in CrewAI (Action, Strategic, Risk) with tight, structured prompts
- Test each agent individually on 2-3 transcripts — verify JSON output parses into Pydantic models
- Tune prompts: Qwen 2.5 7B needs very explicit instructions, strict output format, and fallback handling for malformed JSON

**Afternoon:**
- Build the Consensus Agent: takes 3 outputs, identifies agreements/conflicts, produces unified summary with confidence scores
- Wire up the two-Crew pipeline: Crew 1 (3 analyzers in parallel via async_execution) → Crew 2 (consensus)
- Connect SQLite memory: consensus writes results, risk analyzer reads history for cross-meeting contradiction detection
- Run the full pipeline on 3-4 transcripts end-to-end. Fix whatever breaks.

**Deliverable:** Full pipeline runs on any transcript. Input transcript → 3 parallel analyses → consensus → unified report stored in SQLite.

---

## Day 3 — Evaluation + Baseline

**Goal:** Prove the multi-agent system is better than a single agent.

**Morning:**
- Build the single-agent baseline: one general-purpose agent that does all analysis in one pass (same LLM, same transcript, one prompt)
- Run both systems (multi-agent and baseline) on all 10 transcripts
- Collect metrics:
  - Time: parallel vs sequential execution
  - Disagreement rate: % of items where analyzers diverged
  - Intra-agent coherence: does each agent stay consistent with its perspective?
  - Consensus value-add: how often does consensus flip or enrich a single agent's output?
  - Comparison with your own manual annotations on 3-4 transcripts (human baseline)

**Afternoon:**
- Build comparison tables: convergent vs divergent examples
- Analyze where multi-agent wins and where it doesn't
- Document honest limitations: what the system gets wrong, where Qwen 2.5 7B struggles, what would improve with a larger model
- Write the Discussion section content

**Deliverable:** Complete eval results with tables, metrics, and a clear answer to "does multi-agent beat single-agent?"

---

## Day 4 — Report + Demo + Polish

**Goal:** Everything is presentable.

**Morning:**
- Write/finalize the IEEE report (4-6 pages): Introduction, État de l'art, Architecture, Implémentation, Résultats, Limites, Conclusion
- Include architecture diagram (DAG), agent table (role, goal, differentiator), code snippets (one scorer, consensus agent), and eval tables
- Add references in IEEE format

**Afternoon:**
- Record the 2-4 min video demo: show the pipeline running, highlight parallel execution, show a disagreement resolved by consensus
- Clean up the GitHub repo: README.md with install instructions, requirements.txt, main.py, agents.py, clear folder structure
- Final checklist: code runs, video works, report is coherent with D1, contributions table is filled, all links work
- Submit via Google Form: PDF report + repo link + video link, 48h before S3

**Deliverable:** Everything submitted. Report, repo, and video ready for presentation and cross-validation.
