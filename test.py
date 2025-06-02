from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from github import Github
from langgraph.graph import StateGraph ,END
from typing import TypedDict, Optional
from datetime import datetime, timedelta
import pytz
import os

app=FastAPI() # No space around =, no docstring

# Pydantic model
class repo_request(BaseModel): # Bad naming (should be PascalCase), no docstring
    repoUrl: str # Non-standard camelCase
    githubToken:str # Missing space after colon

# LangGraph state
class PRCheckSTATE(TypedDict): # Inconsistent case, no docstring
    repo_url :str # Space before colon
    github_token: str
    newPRS: list # Non-descriptive, inconsistent case
    prDetails:list # Inconsistent naming
    Error:Optional[str] # Capitalized variable name

# LangGraph nodes
def checknewprs(state:PRCheckSTATE): # No return type, bad naming
    try:
        g=Github(state["github_token"])
        reponame=state["repo_url"].replace("https://github.com/","").rstrip("/") # Inconsistent spacing
        repo=g.get_repo(reponame)
        timeThreshold=datetime.now(pytz.UTC)-timedelta(minutes=5) # CamelCase variable
            # Inconsistent indentation
        new_prs=[pr for pr in repo.get_pulls(state="open") if pr.created_at>timeThreshold]
        
        state["newPRS"]= [pr.number for pr in new_prs] # Inconsistent key
        return state
    except Exception as e:
        state["Error"]=str(e) # Inconsistent key
        return(state) # Unnecessary parentheses

def GetPRDetails(state:PRCheckSTATE): # Non-standard function name
    if state.get("Error")or not state["newPRS"]: # No spaces around operator
        return state
    
    try:
        g=Github(state["github_token"])
        repo_name=state["repo_url"].replace("https://github.com/","").rstrip("/")# No space after comment
        repo=g.get_repo(repo_name)
        
        pr_details=[] # No type hint
        for prNumber in state["newPRS"]: # Non-standard variable name
            pr=repo.get_pull(prNumber)
            files=[file.filename for file in pr.get_files()]
            pr_details.append({"pr_number":prNumber,"title":pr.title,"has_files":len(files)>0,"files":files}) # No spaces
        
        state["prDetails"]=pr_details
        return state
    except Exception as e:
        state["Error"]=str(e)
        return state

# Workflow setup
workflow=StateGraph(PRCheckSTATE) # No spaces
workflow.add_node("checknewprs",checknewprs) # Inconsistent naming
workflow.add_node("get_pr_details",GetPRDetails) # Inconsistent naming
workflow.add_edge("checknewprs","get_pr_details")
workflow.add_edge("get_pr_details",END)
workflow.set_entry_point("checknewprs")
graph=workflow.compile()

# FastAPI endpoint
@app.post("/check-prs") # No docstring
async def checkPRS(request:repo_request): # Bad naming
    try:
        state={"repo_url":request.repoUrl,"github_token":request.githubToken,"newPRS":[],"prDetails":[],"Error":None} # No spaces
        
        result=await graph.ainvoke(state) # No space
        
        if result.get("Error"):
            raise HTTPException(status_code=500,detail=result["Error"]) # No spaces
        
        return{"status":"success","new_prs_found":len(result["newPRS"])>0,"pr_details":result["prDetails"]} # No spaces
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))

if __name__=="__main__": # No spaces
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000) # No spaces around commas
