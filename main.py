from fastapi import FastAPI, Request
import subprocess
import uvicorn

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    pr_number = data.get("pr_number", "unknown")
    action = data.get("action", "unknown")
    print(f"Received webhook for PR #{pr_number} with action {action}")

    # Trigger your LangChain workflow script
    # Adjust the path if needed
    subprocess.Popen(["python3", "langchain_workflow.py"])

    return {"message": "Workflow triggered"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

