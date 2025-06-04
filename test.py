from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from github import Github
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Dict
from datetime import datetime, timedelta
import pytz
import os

app = FastAPI()

# Pydantic model for request validation
class RepoRequest(BaseModel):
    """Request model for GitHub repository URL and token."""
    repo_url: str
    github_token: str

# LangGraph state definition
class PRCheckState(TypedDict):
    """State for tracking pull request check workflow."""
    repo_url: str
    github_token: str
    new_prs: List[int]
    pr_details: List[Dict]
    error: Optional[str]

# LangGraph nodes
def check_new_prs(state: PRCheckState) -> PRCheckState:
    """Check for new pull requests created in the last 5 minutes."""
    try:
        g=Github(state["github_token"])
        reponame=state["repo_url"].replace("https://github.com/","").rstrip("/")
        repo=g.get_repo(reponame)
        timeThreshold=datetime.now(pytz.UTC)-timedelta(minutes=5)
        new_prs=[pr for pr in repo.get_pulls(state="open") if pr.created_at>timeThreshold]
        
        state["newPRS"]= [pr.number for pr in new_prs]
        return state
    except Exception as e:
        state["error"] = str(e)
        return state

def get_pr_details(state: PRCheckState) -> PRCheckState:
    """Retrieve details for new pull requests."""
    if state.get("error") or not state.get("newPRS"):
        return state
    
    try:
        github = Github(state["github_token"])
        repo_name = state["repo_url"].replace("https://github.com/", "").rstrip("/")
        repo = github.get_repo(repo_name)
        
        pr_details: List[Dict] = []
        for pr_number in state["newPRS"]:
            pr = repo.get_pull(pr_number)
            files = [file.filename for file in pr.get_files()]
            pr_details.append({
                "pr_number": pr_number,
                "title": pr.title,
                "has_files": len(files) > 0,
                "files": files
            })
        
        state["pr_details"] = pr_details
        return state
    except Exception as e:
        state["error"] = str(e)
        return state

# Workflow setup
workflow=StateGraph(PRCheckSTATE)
workflow.add_node("checknewprs",checknewprs)
workflow.add_node("get_pr_details", get_pr_details)
workflow.add_edge("checknewprs","get_pr_details")
workflow.add_edge("get_pr_details", END)
workflow.set_entry_point("checknewprs")
graph = workflow.compile()

# FastAPI endpoint
@app.post("/check-prs")
async def check_prs(request: RepoRequest):
    """Check for new pull requests in the specified GitHub repository."""
    try:
        state={"repo_url":request.repoUrl,"github_token":request.githubToken,"newPRS":[],"prDetails":[],"Error":None}
        
        result = await graph.ainvoke(state)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "new_prs_found": len(result["newPRS"]) > 0,
            "pr_details": result["pr_details"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
