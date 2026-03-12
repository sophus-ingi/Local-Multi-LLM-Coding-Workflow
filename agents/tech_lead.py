import json
import re
from langchain_ollama import ChatOllama
from state import ProjectState

# Endpoint A — Reasoning model (same "Brain" endpoint as Architect)
_llm = ChatOllama(model="qwen3:8b", temperature=0)

_SYSTEM = """You are a Tech Lead. Given an Architecture Decision Record, break the work into
implementation tickets. Return ONLY a valid JSON array — no markdown fences, no prose.

Each ticket must have exactly these keys:
  "id"       : string  (e.g. "T-01")
  "title"    : string
  "file"     : string  (the Python filename this ticket produces, e.g. "server.py")
  "details"  : string  (clear instructions for a junior developer)

Example:
[
  {"id": "T-01", "title": "Create HTTP server", "file": "server.py", "details": "..."},
  {"id": "T-02", "title": "Add /health endpoint", "file": "server.py", "details": "..."}
]"""


def _extract_json(text: str) -> list:
    """Strip any accidental markdown fences and parse JSON."""
    # Remove ```json ... ``` or ``` ... ``` wrappers if present
    cleaned = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    return json.loads(cleaned)


def tech_lead_node(state: ProjectState) -> dict:
    print("--- 📋  Phase 2: Tech Lead — breaking ADR into tickets ---")
    prompt = f"{_SYSTEM}\n\nADR:\n{state['architecture_adr']}"
    res = _llm.invoke(prompt)
    try:
        task_list = _extract_json(res.content)
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"  ⚠️  JSON parse failed ({exc}). Storing raw response as single ticket.")
        task_list = [
            {
                "id": "T-01",
                "title": "Implement full solution",
                "file": "solution.py",
                "details": res.content,
            }
        ]
    print(f"  ✅  {len(task_list)} ticket(s) created")
    return {"task_list": task_list}
