# Setup Guide — AI Factory (LangGraph + Ollama)

Step-by-step instructions for reproducing the demo workflow on any Windows / macOS / Linux machine.

---

## 1. Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | ≥ 3.11 | https://www.python.org/downloads/ |
| Git | any | https://git-scm.com/ |
| Ollama | latest | https://ollama.com/download |

Verify:
```bash
python --version   # Python 3.11+
ollama --version   # ollama version …
git --version
```

---

## 2. Configure the Two Local Model Endpoints

Ollama runs a single local server (`http://localhost:11434`) that serves multiple models.
Each model is treated as a separate "endpoint" — the model name is the routing key.

### Pull Endpoint A — Reasoning model (Architecture & Tech Lead)
```bash
ollama pull qwen3:8b
```
Expected size: ~5 GB. Verify:
```bash
ollama run qwen3:8b "Say hello"
```

### Pull Endpoint B — Worker model (Coder, Tester, Docs, Deployer)
```bash
ollama pull llama3.2:latest
```
Expected size: ~2 GB. Verify:
```bash
ollama run llama3.2:latest "Say hello"
```

### Confirm both models are available
```bash
ollama list
# Should show both qwen3:8b and llama3.2:latest
```

---

## 3. Install the Toolchain

```bash
cd ai-factory
pip install -r requirements.txt
```

`requirements.txt` installs:
- `langchain-ollama` — Ollama adapter for LangChain
- `langgraph` — graph execution engine
- `langchain-core` — shared LangChain primitives

No vector database, no API keys, no cloud services required.

---

## 4. Configure Endpoints (Changing Models)

Each agent file has a single constant at the top:

```python
# agents/architect.py — change this to switch Endpoint A
_llm = ChatOllama(model="qwen3:8b", temperature=0)

# agents/coder.py — change this to switch Endpoint B
_llm = ChatOllama(model="llama3.2:latest", temperature=0)
```

To route to a different Ollama host (e.g. a second machine on your LAN):
```python
_llm = ChatOllama(model="qwen3:8b", base_url="http://192.168.1.50:11434", temperature=0)
```

No other changes needed — the graph wiring in `graph.py` is endpoint-agnostic.

---

## 5. Run the Demo Workflow

### Option A — Default task (temperature converter CLI tool)
```bash
cd ai-factory
python main.py
```

### Option B — Custom task
```bash
python main.py "Build a REST API that tracks daily step counts"
```

Expected console output:
```
🚀  AI Factory starting
    Task: Build a Python CLI tool …

--- 🏗️  Phase 1: Architecture ---
--- 📋  Phase 2: Tech Lead — breaking ADR into tickets ---
  ✅  4 ticket(s) created
--- 💻  Phase 3a: Coder A ---
  → coding T-01: …
  → coding T-02: …
--- 💻  Phase 3b: Coder B ---
  → coding T-03: …
  → coding T-04: …
--- 🧪  Phase 4: Tester ---
--- 📝  Phase 5: Docs ---
--- 🚀  Phase 6: Deployment Validation ---

✅  Pipeline complete — saving artifacts …
  📄  output/README.md
  📄  output/solution.py
  📄  output/test_report.txt
  📄  output/architecture_adr.md
  📄  output/task_list.json
  📄  output/deployment_report.md

🏁  Done. All artifacts saved to: output/
```

---

## 6. Verify the Artifacts

After the run, `output/` contains:

| File | Responsibility | Description |
|------|---------------|-------------|
| `architecture_adr.md` | Architecture | ADR with component decomposition, interface contracts, deployment topology |
| `task_list.json` | Tech Lead | Tickets with scope, acceptance criteria, dependency order |
| `*.py` | Implementation | Generated Python source files (multi-file) |
| `test_report.txt` | Testing & Quality | pytest suite + simulated results + known limitations |
| `README.md` | Documentation | Setup, run instructions, API usage, operational notes |
| `deployment_report.md` | Deployment Validation | Checklist, Dockerfile, env vars, runbook, risks |

Inspect each file to confirm all 6 responsibilities are covered.

---

## 7. Commit Artifacts to Git (Reproducibility)

```bash
git add output/
git commit -m "run: temperature converter CLI — $(date +%Y-%m-%d)"
```

To re-run and compare:
```bash
python main.py "Build a Python CLI tool that converts temperatures …"
git diff output/
```

Structure and section headings will be consistent across runs (same graph, `temperature=0`).

---

## 8. Running Tests from the Test Report

The `test_report.txt` contains a pytest file. Extract and run it:

```bash
# Copy the TEST CODE section from test_report.txt into a file
python -m pytest output/test_generated.py -v
```

Or run a static lint check on the generated code:
```bash
pip install ruff
ruff check output/
```

---

## 9. Troubleshooting

| Problem | Fix |
|---------|-----|
| `httpx.ConnectError: Connection refused` | Ollama is not running — start it with `ollama serve` |
| `model not found` | Run `ollama pull qwen3:8b` and `ollama pull llama3.2:latest` |
| `json.JSONDecodeError` in tech_lead | Tech Lead fallback activates automatically; check `task_list.json` for a single catch-all ticket |
| Empty `code_files` | The tester and deployer will still run with empty input; re-run or reduce task complexity |
| Slow first run | Models are cold-loaded on first inference — subsequent runs are faster |

---

## 10. Project Structure Reference

```
ai-factory/
├── agents/
│   ├── architect.py      # Endpoint A — produces ADR
│   ├── tech_lead.py      # Endpoint A — produces task_list.json
│   ├── coder.py          # Endpoint B — two parallel workers
│   ├── tester.py         # Endpoint B — tests + docs
│   └── deployer.py       # Endpoint B — deployment validation
├── state.py              # ProjectState TypedDict (shared memory)
├── graph.py              # LangGraph pipeline wiring
├── main.py               # Entry point + artifact saving
├── requirements.txt
├── slides.md             # Presentation (this evaluation)
├── SETUP.md              # This file
└── output/               # Generated artifacts (git-tracked)
```
