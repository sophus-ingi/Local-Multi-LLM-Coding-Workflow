from langchain_ollama import ChatOllama
from state import ProjectState

# Endpoint B — Worker model
_llm = ChatOllama(model="llama3.2:latest", temperature=0)

_SYSTEM = """You are a DevOps engineer performing deployment validation.
Given code files and architecture notes, produce a deployment validation report with these sections:

## Deployment Checklist
- [ ] item (pass/fail/n-a)

## Dockerfile
A minimal Dockerfile for the project (if applicable).

## Environment / Config
Required environment variables and config files.

## Runbook
Step-by-step operational notes: how to start, stop, and verify the service.

## Risks & Limitations
Known gaps, unresolved dependencies, or security concerns.

Be specific to the actual files provided. Do not invent features not present in the code."""


def deployer_node(state: ProjectState) -> dict:
    print("--- 🚀  Phase 6: Deployment Validation ---")
    files_summary = "\n\n".join(
        f"### {name}\n```python\n{code}\n```"
        for name, code in (state.get("code_files") or {}).items()
    )
    prompt = (
        f"{_SYSTEM}\n\n"
        f"Architecture:\n{state.get('architecture_adr', '')}\n\n"
        f"Code:\n{files_summary}"
    )
    res = _llm.invoke(prompt)
    return {"deployment_report": res.content}
