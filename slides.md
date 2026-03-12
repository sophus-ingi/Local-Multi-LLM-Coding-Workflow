# Local Multi-LLM Coding Workflow — Evaluation
### Presentation · 10 Slides

---

## Slide 1 — Objective & Scope

**Goal:** Identify the most viable way to run a *local*, *multi-LLM* workflow that
collaboratively produces software artifacts end-to-end:
architecture → implementation → testing → docs → deployment validation.

**Constraints:**
- All models run locally (no cloud APIs required)
- Minimum two separate model endpoints
- Fully open-source toolchain
- Must cover 6 defined responsibilities (Architect, Tech Lead, Coder, Tester, Docs, Deployer)

**Two candidates evaluated:**

| # | Candidate | Orchestrator | Model Backend |
|---|-----------|-------------|---------------|
| A | **LangGraph + Ollama** | LangGraph (LangChain) | Ollama |
| B | **CrewAI + Ollama** | CrewAI | Ollama |

---

## Slide 2 — Candidate A: LangGraph + Ollama

**What it is:**
LangGraph is a low-level graph execution engine from LangChain.
You define nodes (Python functions) and edges (control flow) explicitly.
Ollama serves quantised open-source LLMs locally over a REST API.

**Key characteristics:**
- State machine model — each node reads and writes a typed `ProjectState` dict
- Parallel fan-out/fan-in is a first-class graph primitive
- Full Python control — any logic between nodes is just code
- `ChatOllama` lets you point each node at a *different* model by name
- No agent "magic" — deterministic flow unless you explicitly add conditionals

**Effort to set up:** ~30 min (install Ollama, pull 2 models, `pip install langgraph langchain-ollama`)

---

## Slide 3 — Candidate B: CrewAI + Ollama

**What it is:**
CrewAI is a higher-level "crew of agents" framework.
You define `Agent` objects with roles/goals/backstories and `Task` objects with descriptions.
A `Crew` then orchestrates agents over tasks sequentially or in parallel.

**Key characteristics:**
- Role-based — agents have natural-language personas (Architect, Dev, QA…)
- Task dependency graph via `context=` parameter on each Task
- Each Agent can have its own `llm=` parameter — maps to different Ollama endpoints
- Built-in memory (short-term / long-term via embeddings) — requires Chroma or similar
- Less code for simple pipelines; harder to control exact output format

**Effort to set up:** ~45–60 min (install CrewAI + Chroma + Ollama, configure embedding model)

---

## Slide 4 — Evaluation Matrix

| Criterion | LangGraph + Ollama | CrewAI + Ollama |
|---|---|---|
| **Setup complexity** | Low — 3 pip packages, no vector DB needed | Medium — needs embedding model + Chroma for memory |
| **Multi-endpoint routing** | Explicit: each node instantiates its own `ChatOllama(model=…)` | Explicit: each `Agent(llm=…)` takes its own LLM instance |
| **Parallel workers (N≥2)** | Native fan-out edges; coders run truly concurrently | Parallel tasks via `Process.hierarchical`; less granular |
| **Typed state / no context loss** | `TypedDict` state flows through every node; nothing is implicit | Shared task context passed via `context=[]`; risks verbose re-injection |
| **Output format control** | You own the prompt — you enforce JSON/Markdown directly | Agent backstory nudges output; harder to force strict schema |
| **Reproducibility** | Same graph + same model = same structure every run | Agent re-planning can vary; non-deterministic on restarts |
| **Failure isolation** | Node raises Python exception — caught, logged, retried explicitly | Agent failure surfaces as string in output — easy to miss silently |
| **Git / diff integration** | Artifacts written to files → `git add/commit` in main.py | Same — no built-in VCS, but artifacts can be written to files |
| **Security** | Ollama listens on localhost only by default | Same |

---

## Slide 5 — Architecture of the Recommended Solution (LangGraph)

```
                        ┌─────────────────────────────────────────────┐
                        │              ProjectState (shared)           │
                        │  task · adr · task_list · code_files        │
                        │  test_results · docs · deployment_report    │
                        └─────────────────────────────────────────────┘
                                           │
START ──► [architect] ──► [tech_lead] ─────┼──► [coder_a] ─┐
          qwen3:8b        qwen3:8b          │                ├──► [merge] ──► [tester] ──► [docs] ──► [deployer] ──► END
                                            └──► [coder_b] ─┘   llama3.2    llama3.2     llama3.2     llama3.2
                                                llama3.2
```

**Two endpoints:**
- **Endpoint A** (`qwen3:8b`): High-reasoning tasks — Architect, Tech Lead
- **Endpoint B** (`llama3.2:latest`): Fast execution tasks — Coder A, Coder B, Tester, Docs, Deployer

**Routing is configuration-only** — changing a model means editing one line per agent file.

---

## Slide 6 — How Each Responsibility Is Satisfied

| Responsibility | Node | Endpoint | Output Artifact |
|---|---|---|---|
| **Architecture** | `architect_node` | A (qwen3:8b) | `architecture_adr.md` — ADR with component breakdown, interface contracts, deployment topology |
| **Tech Lead** | `tech_lead_node` | A (qwen3:8b) | `task_list.json` — tickets with scope, acceptance criteria, dependency order |
| **Implementation** | `coder_node_a` + `coder_node_b` (parallel) | B (llama3.2) | Code files in `output/` — multi-file changes |
| **Testing & Quality** | `tester_node` | B (llama3.2) | `test_report.txt` — pytest suite + simulated results + known limitations |
| **Documentation** | `docs_node` | B (llama3.2) | `README.md` — setup, run, API usage, operational notes |
| **Deployment Validation** | `deployer_node` | B (llama3.2) | `deployment_report.md` — checklist, Dockerfile, env vars, runbook, risks |

---

## Slide 7 — Non-Functional Requirements

### Predictability & Control
- The `StateGraph` is compiled — you can call `graph.get_graph().draw_mermaid()` to
  visualise the full DAG before running.
- All file writes happen in `main.py::save_artifacts()` — a single reviewable function.
- Swap to `graph.stream()` instead of `graph.invoke()` to get node-by-node output
  for human review before proceeding (ask-before-run equivalent).

### Reproducibility
- `temperature=0` on all LLMs — deterministic token sampling.
- `output/` artifacts → `git add output/ && git commit -m "run: <task>"` — full diff history.
- Re-running the same task with the same models produces structurally identical artifacts.

### Context Management
- `ProjectState` is the **only** channel between nodes — no hidden prompt history.
- Each node receives exactly the fields it needs; there is no runaway context window.
- When repo grows: pass only relevant file summaries into prompts (truncate at token budget).
  The `docs_node` already does this: it summarises `code_files` rather than injecting raw state.

### Security
- Ollama binds to `127.0.0.1:11434` by default — never exposed publicly.
- No API keys, no cloud egress, no unauthenticated external endpoints.

---

## Slide 8 — Failure Modes & Mitigations

| Failure | How it surfaces | Mitigation in this design |
|---|---|---|
| JSON parse failure in tech_lead | `json.JSONDecodeError` | `_extract_json()` strips fences; fallback creates a single catch-all ticket |
| Model returns empty string | `res.content == ""` | `state.get(field, "")` default; downstream nodes still run with empty input |
| Coder produces markdown fences instead of Python | Saved file has ` ``` ` lines | Strip logic in `_code_for_ticket()` removes fences before saving |
| Context window overflow on large ADR | Model truncates or errors | Tech Lead summarises ADR → tickets; coders only see their ticket, not the full ADR |
| Ollama model not pulled | `httpx.ConnectError` | Caught at startup; setup guide includes `ollama pull` as prerequisite step |
| Parallel coders write conflicting keys | Dict merge collision | Both workers use filename as key; same-file tickets are concatenated, not overwritten |

---

## Slide 9 — Tradeoffs & Risks

**LangGraph strengths:**
- Maximum control — every prompt, every node, every output format is in your code
- No hidden state — `ProjectState` is the complete picture at all times
- Parallel workers are trivial to add (duplicate a coder node + two edges)
- Lightweight — no vector database required for basic pipelines

**LangGraph weaknesses:**
- More boilerplate than CrewAI for simple chains
- No built-in long-term memory across runs (must implement yourself if needed)
- Agent "personalities" are just system prompts — less expressive than CrewAI role cards

**CrewAI strengths:**
- Fast to prototype role-based agents
- Built-in memory with Chroma gives cross-run persistence

**CrewAI weaknesses:**
- Less control over exact output format — harder to guarantee JSON schema compliance
- Non-deterministic re-planning can break reproducibility
- Heavier dependency footprint (Chroma, embeddings)

**Chosen approach: LangGraph + Ollama** — the assignment's Hard Requirements
(multi-endpoint routing, reproducibility, explicit context management) favour
explicit graph control over higher-level agent abstraction.

---

## Slide 10 — Recommendation & Rationale

### Recommended: LangGraph + Ollama ✅

**Justification against requirements:**

| Requirement | How LangGraph satisfies it |
|---|---|
| ≥2 local endpoints | `ChatOllama(model="qwen3:8b")` vs `ChatOllama(model="llama3.2:latest")` — one line per agent |
| Routing via config | Model name is a single string constant at the top of each agent file |
| All 6 responsibilities | One node per responsibility; all covered |
| N≥2 parallel workers | `coder_a` and `coder_b` are fan-out parallel nodes |
| Predictability | Deterministic graph; `temperature=0`; stream mode for human-in-the-loop |
| Reproducibility | Artifacts committed to git; same input → same structure |
| No silent context loss | Typed `ProjectState`; each node only reads what it needs |
| Security | Ollama localhost-only; no cloud calls |
| Open source | LangGraph (MIT), LangChain (MIT), Ollama (MIT), qwen3 (Apache 2), Llama 3.2 (Meta Llama 3 Community) |

**Next steps:**
1. Run `python main.py` with the default task to validate the pipeline end-to-end
2. Commit `output/` artifacts to demonstrate git-reproducibility
3. Add `graph.stream()` checkpointing for human-in-the-loop review
