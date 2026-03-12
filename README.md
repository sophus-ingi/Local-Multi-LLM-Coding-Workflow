# AI Factory

A local multi-LLM coding pipeline that takes a plain-English task and autonomously produces architecture, code, tests, documentation, and a deployment report — all using models running on your own machine via Ollama.

## How it works

```
START → architect → tech_lead → coder_a ┐
                                coder_b ┘→ merge → tester → docs → deployer → END
```

| Phase | Agent | Model (Endpoint) | Output |
|---|---|---|---|
| 1 | Architect | qwen3:8b (A) | `architecture_adr.md` |
| 2 | Tech Lead | qwen3:8b (A) | `task_list.json` |
| 3 | Coder A + B (parallel) | llama3.2 (B) | source files |
| 4 | Tester | llama3.2 (B) | `test_report.txt` |
| 5 | Docs | llama3.2 (B) | `README.md` |
| 6 | Deployer | llama3.2 (B) | `deployment_report.md` |

All artifacts are saved to `output/`.

## Setup

**1. Install Ollama and pull both models**
```bash
ollama pull qwen3:8b
ollama pull llama3.2:latest
```

**2. Install Python dependencies**
```bash
pip install -r requirements.txt
```

## Usage

```bash
# Default task (temperature converter)
python main.py

# Custom task
python main.py "Build a REST API that tracks daily step counts"
```

## Project structure

```
ai-factory/
├── agents/
│   ├── architect.py    # ADR generation
│   ├── tech_lead.py    # Ticket breakdown
│   ├── coder.py        # Parallel code workers
│   ├── tester.py       # Tests + docs
│   └── deployer.py     # Deployment validation
├── state.py            # Shared ProjectState
├── graph.py            # LangGraph pipeline
├── main.py             # Entry point
├── requirements.txt
├── slides.md           # Evaluation presentation (10 slides)
├── SETUP.md            # Detailed setup & reproduction guide
└── output/             # Generated artifacts (commit this to git)
```

## Switching models

Each agent file has a single constant at the top. Change the model name there:

```python
# agents/architect.py
_llm = ChatOllama(model="qwen3:8b", temperature=0)  # ← change here
```

To point at a second machine on your network:
```python
_llm = ChatOllama(model="qwen3:8b", base_url="http://192.168.1.50:11434")
```

## Evaluation

See [slides.md](slides.md) for the full two-candidate evaluation (LangGraph vs CrewAI) and recommendation rationale.
See [SETUP.md](SETUP.md) for the detailed reproduction guide.
