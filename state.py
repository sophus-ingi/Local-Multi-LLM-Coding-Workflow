from typing import TypedDict, List, Dict


class ProjectState(TypedDict):
    task: str
    architecture_adr: str
    task_list: List[Dict]       # Tickets produced by Tech Lead
    code_files: Dict[str, str]  # filename -> content, produced by Coders
    test_results: str
    docs: str
    deployment_report: str
    iteration: int
