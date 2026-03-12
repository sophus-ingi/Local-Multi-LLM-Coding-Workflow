from langchain_ollama import ChatOllama
from state import ProjectState

# Endpoint B — Worker model
_llm = ChatOllama(model="llama3.2:latest", temperature=0)

_SYSTEM = """You are a QA engineer. Given Python source files, write a pytest test suite
and then provide a plain-text test report.

Return your response in exactly two sections separated by the marker ---REPORT---:

Section 1: the pytest code (raw Python, no fences)
Section 2: a short test report listing which tests pass/fail (simulate execution)"""

_DOC_SYSTEM = """You are a technical writer. Given an Architecture Decision Record and
the final code files, write a concise README.md.
Include: Overview, Architecture, Files, How to run. Use standard Markdown."""


def tester_node(state: ProjectState) -> dict:
    print("--- 🧪  Phase 4: Tester ---")
    files_summary = "\n\n".join(
        f"# {name}\n{code}" for name, code in (state.get("code_files") or {}).items()
    )
    prompt = f"{_SYSTEM}\n\nCode files:\n{files_summary}"
    res = _llm.invoke(prompt)

    parts = res.content.split("---REPORT---", 1)
    test_code = parts[0].strip()
    report = parts[1].strip() if len(parts) > 1 else "No report section found."
    return {"test_results": f"=== TEST CODE ===\n{test_code}\n\n=== REPORT ===\n{report}"}


def docs_node(state: ProjectState) -> dict:
    print("--- 📝  Phase 5: Docs ---")
    files_summary = "\n\n".join(
        f"### {name}\n```python\n{code}\n```"
        for name, code in (state.get("code_files") or {}).items()
    )
    prompt = (
        f"{_DOC_SYSTEM}\n\n"
        f"ADR:\n{state.get('architecture_adr', '')}\n\n"
        f"Code:\n{files_summary}"
    )
    res = _llm.invoke(prompt)
    return {"docs": res.content}
