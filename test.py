from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from github import Github
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from datetime import datetime, timedelta
import pytz
import os

app = FastAPI()

class RepoRequest(BaseModel):
    repo_url: str
    github_token: str

class PRCheckState(TypedDict):
    repo_url: str
    github_token: str
    new_prs: list
    pr_details: list
    error: Optional[str]

def check_new_prs(state: PRCheckState) -> PRCheckState:
    try:
        g = Github(state["github_token"])
        repo_name = state["repo_url"].replace("https://github.com/", "").rstrip("/")
        repo = g.get_repo(repo_name)
        time_threshold = datetime.now(pytz.UTC) - timedelta(minutes=5)
        new_prs = [pr for pr in repo.get_pulls(state="open") if pr.created_at > time_threshold]
        state["new_prs"] = [pr.number for pr in new_prs]
        return state
    except Exception as e:
        state["error"] = str(e)
        return state

def get_pr_details(state: PRCheckState) -> PRCheckState:
    if state.get("error") or not state["new_prs"]:
        return state
    
    try:
        g = Github(state["github_token"])
        repo_name = state["repo_url"].replace("https://github.com/", "").rstrip("/")
        repo = g.get_repo(repo_name)
        pr_details: list = []
        for pr_number in state["new_prs"]:
            pr = repo.get_pull(pr_number)
            files = [file.filename for file in pr.get_files()]
            pr_details.append({"pr_number": pr_number, "title": pr.title, "has_files": len(files) > 0, "files": files})
        state["pr_details"] = pr_details
        return state
    except Exception as e:
        state["error"] = str(e)
        return state

workflow = StateGraph(PRCheckState)
workflow.add_node("check_new_prs", check_new_prs)
workflow.add_node("get_pr_details", get_pr_details)
workflow.add_edge("check_new_prs", "get_pr_details")
workflow.add_edge("get_pr_details", END)
workflow.set_entry_point("check_new_prs")
graph = workflow.compile()

@app.post("/check-prs")
async def check_prs(request: RepoRequest):
    try:
        state = {
            "repo_url": request.repo_url,
            "github_token": request.github_token,
            "new_prs": [],
            "pr_details": [],
            "error": None
        }
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
