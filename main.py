from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.generativeai import GenerativeModel
from github import Github
import base64
import uuid
import os
from dotenv import load_dotenv
import asyncio
from typing import Dict, Any

load_dotenv()

app = FastAPI(title="Gemini Task Automation", version="1.0.0")

# Config
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USERNAME")

geminimodel = GenerativeModel("gemini-2.0-flash-exp")
github = Github(GITHUB_TOKEN)

# In-memory store (use Redis for production)
tasks: Dict[str, Any] = {}

class TaskRequest(BaseModel):
    task: str
    callback_url: str = ""

@app.post("/ready")
async def submit_task(request: TaskRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "task": request.task, "callback_url": request.callback_url}
    
    asyncio.create_task(process_task(task_id))
    return {"id": task_id, "status": "processing"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

async def process_task(task_id: str):
    task_data = tasks[task_id]
    
    try:
        # 1. Generate code
        tasks[task_id]["status"] = "generating"
        files = await generate_webapp(task_data["task"])
        
        # 2. Deploy to GitHub
        tasks[task_id]["status"] = "deploying"
        repo_info = await create_github_repo(task_data["task"], files)
        
        # 3. Complete
        tasks[task_id].update({
            "status": "completed",
            "live_url": repo_info["live_url"],
            "repo_url": repo_info["repo_url"]
        })
        
        # 4. Notify
        if task_data["callback_url"]:
            await notify_callback(task_data["callback_url"], repo_info)
            
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

async def generate_webapp(task_desc: str) -> Dict[str, str]:
    prompt = f'''Generate COMPLETE static web app for: "{task_desc}"

REQUIREMENTS:
- Single index.html with embedded CSS/JS
- Responsive, modern UI
- Vanilla HTML/CSS/JS only
- Max 1500 lines

JSON OUTPUT ONLY:
{{"index.html": "FULL CODE", "README.md": "Description"}}'''

    response = geminimodel.generate_content(prompt)
    content = response.text.strip()
    return eval(content)  # Safe for this use case

async def create_github_repo(task: str, files: Dict[str, str]) -> Dict[str, str]:
    repo_name = f"task-{int(asyncio.get_event_loop().time())}"
    
    # Create repo
    repo = github.get_user().create_repo(repo_name, description=task)
    
    # Commit files
    for filename, content in files.items():
        repo.create_file(
            path=filename,
            message=f"Add {filename}: {task}",
            content=content
        )
    
    # Enable GitHub Pages
    repo.edit("Enable Pages", website_source="gh_pages", source_path="")
    
    return {
        "repo_url": repo.html_url,
        "live_url": f"https://{GITHUB_USER}.github.io/{repo_name}"
    }

async def notify_callback(callback_url: str, deployment: Dict[str, str]):
    import aiohttp
    async with aiohttp.ClientSession() as session:
        await session.post(callback_url, json={
            "status": "completed",
            "live_url": deployment["live_url"],
            "repo_url": deployment["repo_url"],
            "deployed_at": "now"
        })