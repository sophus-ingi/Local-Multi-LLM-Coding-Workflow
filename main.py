"""
main.py — Entry point for the AI Factory.

Usage:
    python main.py "Build a REST API that tracks daily step counts"
"""

import sys
import os
import json

# ── path fix so agents can import state.py ─────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from graph import build_graph
from state import ProjectState

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def save_artifacts(state: ProjectState) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. README.md
    readme_path = os.path.join(OUTPUT_DIR, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(state.get("docs", ""))
    print(f"  📄  {readme_path}")

    # 2. Generated code files
    for filename, code in (state.get("code_files") or {}).items():
        code_path = os.path.join(OUTPUT_DIR, filename)
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"  📄  {code_path}")

    # 3. Test report
    report_path = os.path.join(OUTPUT_DIR, "test_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(state.get("test_results", ""))
    print(f"  📄  {report_path}")

    # 4. ADR
    adr_path = os.path.join(OUTPUT_DIR, "architecture_adr.md")
    with open(adr_path, "w", encoding="utf-8") as f:
        f.write(state.get("architecture_adr", ""))
    print(f"  📄  {adr_path}")

    # 5. Task list (for traceability)
    tickets_path = os.path.join(OUTPUT_DIR, "task_list.json")
    with open(tickets_path, "w", encoding="utf-8") as f:
        json.dump(state.get("task_list", []), f, indent=2)
    print(f"  📄  {tickets_path}")

    # 6. Deployment report
    deploy_path = os.path.join(OUTPUT_DIR, "deployment_report.md")
    with open(deploy_path, "w", encoding="utf-8") as f:
        f.write(state.get("deployment_report", ""))
    print(f"  📄  {deploy_path}")


def main() -> None:
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "Build a Python CLI tool that converts temperatures between Celsius, "
        "Fahrenheit, and Kelvin"
    )

    print(f"\n🚀  AI Factory starting")
    print(f"    Task: {task}\n")

    initial_state: ProjectState = {
        "task": task,
        "architecture_adr": "",
        "task_list": [],
        "code_files": {},
        "test_results": "",
        "docs": "",
        "deployment_report": "",
        "iteration": 0,
    }

    graph = build_graph()
    final_state = graph.invoke(initial_state)

    print("\n✅  Pipeline complete — saving artifacts …")
    save_artifacts(final_state)
    print(f"\n🏁  Done. All artifacts saved to: {OUTPUT_DIR}/\n")


if __name__ == "__main__":
    main()
