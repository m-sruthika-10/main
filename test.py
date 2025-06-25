from fastapi import FastAPI,HTTPException # Violation 1: No space after comma
from pydantic import BaseModel
from github import Github
from langgraph.graph import StateGraph,END # Violation 2: No space after comma
from typing import TypedDict,Optional # Violation 3: No space after comma
from datetime import datetime,timedelta # Violation 4: No space after comma
import pytz
import os

app=FastAPI() # Violation 5: No spaces around assignment

class RepoRequest(BaseModel):
    repoURL:str # Violation 6: camelCase instead of snake_case, no space after colon
    github_token: str

class PRCheckState(TypedDict):
    repo_url: str
    github_token: str
    new_prs: list
    prDetails:list # Violation 7: camelCase instead of snake_case, no space after colon
    error: Optional[str]

def checkNewPRs(state:PRCheckState)->PRCheckState: # Violation 8: camelCase function name, no spaces around colons
    try:
        g = Github(state["github_token"])
        repoName=state["repo_url"].replace("https://github.com/","").rstrip("/") # Violation 9: camelCase variable, no spaces around assignment
        repo = g.get_repo(repoName)
        time_threshold = datetime.now(pytz.UTC) - timedelta(minutes=5)
        new_prs = [pr for pr in repo.get_pulls(state="open") if pr.created_at > time_threshold]
        state["new_prs"] = [pr.number for pr in new_prs]
        return(state) # Violation 10: Unnecessary parentheses
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
workflow.add_node("check_new_prs", checkNewPRs)
workflow.add_node("get_pr_details", get_pr_details)
workflow.add_edge("check_new_prs", "get_pr_details")
workflow.add_edge("get_pr_details", END)
workflow.set_entry_point("check_new_prs")
graph = workflow.compile()

@app.post("/check-prs")
async def check_prs(request: RepoRequest):
    try:
        state = {
            "repo_url": request.repoURL,
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
