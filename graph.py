"""
graph.py — Wires all agents into a LangGraph workflow.

Pipeline:
  START → architect → tech_lead → [coder_a ‖ coder_b] → tester → docs → deployer → END

Coder A and Coder B run in parallel (Send API / fan-out) to satisfy the
"N ≥ 2 workers" requirement.
"""

import sys
import os

# Make sure sibling modules are importable when running from any directory
sys.path.insert(0, os.path.dirname(__file__))

from langgraph.graph import StateGraph, START, END

from state import ProjectState
from agents.architect import architect_node
from agents.tech_lead import tech_lead_node
from agents.coder import coder_node_a, coder_node_b
from agents.tester import tester_node, docs_node
from agents.deployer import deployer_node


def _merge_code_files(state: ProjectState) -> dict:
    """Fan-in node: both coders write to code_files; LangGraph merges dicts automatically."""
    # Nothing extra needed — LangGraph merges dict reducers.
    # This node is a named sync-point so the graph topology is explicit.
    return {}


def build_graph() -> StateGraph:
    g = StateGraph(ProjectState)

    # ── nodes ──────────────────────────────────────────────────────────────
    g.add_node("architect", architect_node)
    g.add_node("tech_lead", tech_lead_node)
    g.add_node("coder_a",   coder_node_a)
    g.add_node("coder_b",   coder_node_b)
    g.add_node("merge",     _merge_code_files)
    g.add_node("tester",    tester_node)
    g.add_node("docs",      docs_node)
    g.add_node("deployer",  deployer_node)

    # ── edges ──────────────────────────────────────────────────────────────
    g.add_edge(START,        "architect")
    g.add_edge("architect",  "tech_lead")

    # Fan-out to two parallel coders
    g.add_edge("tech_lead",  "coder_a")
    g.add_edge("tech_lead",  "coder_b")

    # Fan-in — both coders must finish before tester starts
    g.add_edge("coder_a",    "merge")
    g.add_edge("coder_b",    "merge")
    g.add_edge("merge",      "tester")

    g.add_edge("tester",     "docs")
    g.add_edge("docs",       "deployer")
    g.add_edge("deployer",   END)

    return g.compile()
