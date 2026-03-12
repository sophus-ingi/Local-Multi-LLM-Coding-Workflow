from langchain_ollama import ChatOllama
from state import ProjectState

# Endpoint A — Reasoning model
_llm = ChatOllama(model="qwen3:8b", temperature=0)

_SYSTEM = """You are a senior software architect.
When given a task, produce a concise Architecture Decision Record (ADR) with these sections:
## Title
## Status
## Context
## Decision
## Consequences
Be specific. No filler text."""


def architect_node(state: ProjectState) -> dict:
    print("--- 🏗️  Phase 1: Architecture ---")
    prompt = f"{_SYSTEM}\n\nTask: {state['task']}"
    res = _llm.invoke(prompt)
    return {"architecture_adr": res.content}
