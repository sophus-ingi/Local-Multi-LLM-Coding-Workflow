from langchain_ollama import ChatOllama
from state import ProjectState

# Endpoint B — Worker model
_llm = ChatOllama(model="llama3.2:latest", temperature=0)

_SYSTEM = """You are a Python developer. Given a ticket, write production-ready Python code.
Return ONLY the raw Python source — no markdown fences, no explanations.
The first line must be a comment with the filename, e.g.:  # filename: server.py"""


def _code_for_ticket(ticket: dict) -> tuple[str, str]:
    prompt = (
        f"{_SYSTEM}\n\n"
        f"Ticket {ticket['id']}: {ticket['title']}\n"
        f"Target file: {ticket['file']}\n"
        f"Details: {ticket['details']}"
    )
    res = _llm.invoke(prompt)
    code = res.content.strip().lstrip("```python").lstrip("```").rstrip("```").strip()
    return ticket["file"], code


def coder_node_a(state: ProjectState) -> dict:
    """Worker A — handles the first half of the task list."""
    print("--- 💻  Phase 3a: Coder A ---")
    task_list = state.get("task_list", [])
    half = (len(task_list) + 1) // 2
    tickets = task_list[:half]

    code_files: dict[str, str] = dict(state.get("code_files") or {})
    for ticket in tickets:
        print(f"  → coding {ticket['id']}: {ticket['title']}")
        filename, code = _code_for_ticket(ticket)
        # Merge into same file if multiple tickets target it
        if filename in code_files:
            code_files[filename] += f"\n\n# --- {ticket['id']} ---\n{code}"
        else:
            code_files[filename] = code
    return {"code_files": code_files}


def coder_node_b(state: ProjectState) -> dict:
    """Worker B — handles the second half of the task list."""
    print("--- 💻  Phase 3b: Coder B ---")
    task_list = state.get("task_list", [])
    half = (len(task_list) + 1) // 2
    tickets = task_list[half:]

    code_files: dict[str, str] = dict(state.get("code_files") or {})
    for ticket in tickets:
        print(f"  → coding {ticket['id']}: {ticket['title']}")
        filename, code = _code_for_ticket(ticket)
        if filename in code_files:
            code_files[filename] += f"\n\n# --- {ticket['id']} ---\n{code}"
        else:
            code_files[filename] = code
    return {"code_files": code_files}
