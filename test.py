from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from github import Github
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
from datetime import datetime, timedelta
import pytz
import os

app = FastAPI()

# Pydantic model for request body
class RepoRequest(BaseModel):
    """Request model for GitHub repository URL and token."""
    repo_url: str
    github_token: str

# LangGraph state
class PRCheckState(TypedDict):
    """State for tracking pull request check workflow."""
    repo_url: str
    github_token: str
    new_prs: List[int]  # Line 1: Clean (not part of violations)
    pr_details: List[Dict]
    error: Optional[str]

# LangGraph nodes
def check_new_prs(state: PRCheckState) -> PRCheckState:
    """Check for new pull requests created in the last 5 minutes."""
    try:
        g = Github(state["github_token"])
        repo_name = state["repo_url"].replace("https://github.com/", "").rstrip("/")  # Line 2: Fixed camelCase to snake_case, added space after comment
        repo = g.get_repo(repo_name)  # Line 3: Fixed to use snake_case variable
        time_threshold = datetime.now(pytz.UTC) - timedelta(minutes=5)  # Line 4: Fixed camelCase to snake_case, added spaces
        new_prs = [pr for pr in repo.get_pulls(state="open") if pr.created_at > time_threshold]  # Line 5: Added spaces around operators
        state["newPRS"] = [pr.number for pr in new_prs]  # Line 6: Violation retained (non-standard key newPRS)
        return state
    except Exception as e:
        state["Error"] = str(e)  # Line 7: Violation retained (capitalized key Error)
        return state  # Line 8: Fixed by removing unnecessary parentheses

def get_pr_details(state: PRCheckState) -> PRCheckState:
    """Retrieve details for new pull requests."""
    if state.get("Error") or not state["newPRS"]:  # Line 9: Violation retained (no spaces around or, non-standard keys)
        return state
    
    try:
        g = Github(state["github_token"])
        repo_name = state["repo_url"].replace("https://github.com/", "").rstrip("/")
        repo = g.get_repo(repo_name)
        
        pr_details: List[Dict] = []  # Line 10: Violation retained (camelCase prDetails, but added type hint)
        for pr_number in state["newPRS"]:
            pr = repo.get_pull(pr_number)
            files = [file.filename for file in pr.get_files()]
            pr_details.append({"pr_number": pr_number, "title": pr.title, "has_files": len(files) > 0, "files": files})  # Fixed spaces in dict
        
        state["pr_details"] = pr_details
        return state
    except Exception as e:
        state["error"] = str(e)
        return state

# Workflow setup
workflow = StateGraph(PRCheckState)
workflow.add_node("check_new_prs", check_new_prs)
workflow.add_node("get_pr_details", get_pr_details)
workflow.add_edge("check_new_prs", "get_pr_details")
workflow.add_edge("get_pr_details", END)
workflow.set_entry_point("check_new_prs")
graph = workflow.compile()

# FastAPI endpoint
@app.post("/check-prs")
async def check_prs(request: RepoRequest):
    """Check for new pull requests in the specified GitHub repository."""
    try:
        state = {
            "repo_url": request.repo_url, "github_token": request.github_token, "newPRS": [], "prDetails": [], "Error": None}  # Line 11: Violation retained (no spaces, non-standard keys newPRS, prDetails, Error)
        result = await graph.ainvoke(state)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "new_prs_found": len(result["new_prs"]) > 0,
            "pr_details": result["pr_details"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
