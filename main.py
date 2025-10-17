from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.generativeai import GenerativeModel, configure
import uuid, os, asyncio, aiohttp, json, requests
import base64 
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

try:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    configure(api_key=gemini_api_key)
except ValueError as e:
    print(f"Configuration Error: {e}")
    configure(api_key="placeholder") 

app = FastAPI()

geminimodel = GenerativeModel("gemini-2.0-flash-exp") 
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USER = os.getenv("GITHUB_USERNAME")
STUDENT_SECRET = os.getenv("STUDENT_SECRET", "secret123")
tasks: Dict[str, Any] = {}

class TaskRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: List[Dict[str, str]]

@app.get("/")
async def get_dashboard():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    raise HTTPException(status_code=404, detail="Dashboard index.html not found")

@app.post("/ready")
async def submit_task(request: TaskRequest):
    if request.secret != STUDENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    if not GITHUB_TOKEN or not GITHUB_USER:
        raise HTTPException(status_code=500, detail="Server misconfigured: GITHUB_TOKEN or GITHUB_USERNAME missing.")

    task_id = request.task
    
    # 🔥 FIXED: SHORT REPO NAME (UNDER 100 CHARS)
    repo_name = f"{task_id[:20]}-r{request.round}"
    
    # Remove invalid chars
    repo_name = "".join(c for c in repo_name if c.isalnum() or c in "-_")

    tasks[task_id] = {
        "status": "processing",
        "brief": request.brief,
        "evaluation_url": request.evaluation_url,
        "attachments": request.attachments,
        "repo_name": repo_name,
        "nonce": request.nonce
    }
    
    asyncio.create_task(process_task(task_id))
    
    return {"id": task_id, "status": "processing", "repo_name": repo_name}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks: 
        raise HTTPException(status_code=404, detail="Task ID not found")
    return tasks[task_id]

async def process_task(task_id: str):
    task_data = tasks[task_id]
    try:
        tasks[task_id]["status"] = "generating"
        
        files = await generate_webapp(task_data["brief"], task_data.get("attachments", []))
        
        tasks[task_id]["status"] = "deploying"
        
        repo_info = await create_github_repo(task_data["brief"], files, task_data["repo_name"])
        
        tasks[task_id].update({
            "status": "completed",
            "live_url": repo_info["live_url"],
            "repo_url": repo_info["repo_url"]
        })
        
        if "evaluation_url" in task_data:
            callback_payload = {
                "nonce": task_data["nonce"],
                "repo_url": repo_info["repo_url"],
                "live_url": repo_info["live_url"],
                "task_id": task_id,
            }
            await notify_callback(task_data["evaluation_url"], callback_payload)
            
    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

async def generate_webapp(task_brief: str, attachments: List[Dict[str, str]]) -> Dict[str, str]:
    attachment_summary = ""
    if attachments:
        attachment_summary = "\nAttachments provided (use the data URIs as needed):"
        for att in attachments:
            data_uri_start = att.get('url', 'N/A')
            attachment_summary += f"\n- Name: {att.get('name', 'N/A')}, URL (Data URI Start): {data_uri_start[:50]}..."

    prompt = f'''Generate a COMPLETE static web app for the following brief: "{task_brief}"
{attachment_summary}

Single index.html with embedded CSS/JS. Responsive. Vanilla only.
Provide the output as a JSON object with exactly two keys: "index.html" and "README.md".
Example JSON format: {{"index.html": "FULL HTML CODE HERE", "README.md": "A brief description of the app."}}'''
    
    response = await geminimodel.generate_content_async(prompt)
    text = response.text.strip()
    
    if text.startswith('```json'):
        try:
            text = text.split('```json')[1].split('```')[0].strip()
        except IndexError:
            pass
    
    return json.loads(text)

async def create_github_repo(task_brief: str, files: Dict[str, str], repo_name: str) -> Dict[str, str]:
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    print(f"🔥 Creating repo: {repo_name}")  # DEBUG
    
    repo_response = requests.post(f"https://api.github.com/user/repos", 
        json={"name": repo_name, "description": task_brief[:100], "private": False}, 
        headers=headers)
    
    print(f"Repo response: {repo_response.status_code} - {repo_response.text[:200]}")  # DEBUG
    
    if repo_response.status_code not in (201, 200):
        raise Exception(f"Failed to create GitHub repository. Status: {repo_response.status_code}. Response: {repo_response.text[:200]}")
    
    await asyncio.sleep(5) 
    
    for filename, content in files.items():
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        file_payload = {
            "message": f"Add {filename}",
            "content": encoded_content
        }
        
        file_url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/contents/{filename}"
        file_response = requests.put(file_url, json=file_payload, headers=headers)
        
        if file_response.status_code not in (201, 200):
            raise Exception(f"Failed to commit file {filename}. Status: {file_response.status_code}")
    
    pages_url = f"https://api.github.com/repos/{GITHUB_USER}/{repo_name}/pages"
    pages_payload = {"source": {"branch": "main", "path": "/"}}
    
    pages_response = requests.post(pages_url, json=pages_payload, headers=headers)
    
    if pages_response.status_code != 201:
        pages_response = requests.patch(pages_url, json=pages_payload, headers=headers)
    
    await asyncio.sleep(60) 
    
    return {
        "repo_url": f"https://github.com/{GITHUB_USER}/{repo_name}",
        "live_url": f"https://{GITHUB_USER}.github.io/{repo_name}"
    }

async def notify_callback(callback_url: str, deployment: Dict[str, str]):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(callback_url, json=deployment) as response:
                if response.status != 200:
                    print(f"Callback failed: {response.status}")
        except Exception as e:
            print(f"Error during callback notification: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)