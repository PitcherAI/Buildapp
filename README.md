---

title: Gemini Task Automation

emoji: 🤖

colorFrom: blue

colorTo: purple

sdk: docker

app\_port: 8080

pinned: false

---



\# 🤖 Buildapp



\*\*An AI web applications builder using Gemini AI, and automatically deploys them to GitHub Pages.\*\*



\## 🎯 What Does This Project Do?



\### 1️⃣ Request Reception

```json

POST /ready

{

&nbsp; "email": "user@example.com",

&nbsp; "secret": "auth-token",

&nbsp; "task": "chess-game",

&nbsp; "round": 1,

&nbsp; "brief": "Create a chess game with...",

&nbsp; "checks": \["Has license", "Works in browser"],

&nbsp; "evaluation\_url": "https://callback.example.com",

&nbsp; "attachments": \[]

}

```



\## ⚙️ Environment Variables



Create a `.env` file in the project root:



```env

GEMINI\_API\_KEY=AIzaSy...your\_key\_here

GITHUB\_TOKEN=ghp\_...your\_token\_here

GITHUB\_USERNAME=your\_github\_username

STUDENT\_SECRET=your\_custom\_secret\_string

```



\## 📊 Project Architecture



```

┌─────────────┐      ┌──────────────┐      ┌─────────────┐

│   Client    │─────▶│  FastAPI     │─────▶│  Gemini AI  │

│  (Postman)  │◀─────│  /ready      │◀─────│  (Code Gen) │

└─────────────┘      └──────────────┘      └─────────────┘

&nbsp;                           │

&nbsp;                           ▼

&nbsp;                    ┌──────────────┐

&nbsp;                    │  GitPython   │

&nbsp;                    │  (Local Ops) │

&nbsp;                    └──────────────┘

&nbsp;                           │

&nbsp;                           ▼

&nbsp;                    ┌──────────────┐      ┌─────────────┐

&nbsp;                    │  GitHub API  │─────▶│GitHub Pages │

&nbsp;                    │ (Create Repo)│      │  (Deploy)   │

&nbsp;                    └──────────────┘      └─────────────┘

&nbsp;                           │

&nbsp;                           ▼

&nbsp;                    ┌──────────────┐

&nbsp;                    │ Callback URL │

&nbsp;                    │ (Notify Done)│

&nbsp;                    └──────────────┘

```



\## 🛠️ Technology Stack



| Component | Technology | Purpose |

|-----------|-----------|---------|

| \*\*API Framework\*\* | FastAPI | High-performance REST API |

| \*\*AI Model\*\* | Gemini 2.5 Flash | Code generation from natural language |

| \*\*Validation\*\* | Pydantic | Request/config validation |

| \*\*Git Operations\*\* | GitPython | Local repo management |

| \*\*GitHub Integration\*\* | GitHub REST API | Repo creation, Pages deployment |

| \*\*Async Tasks\*\* | asyncio | Background task processing |

| \*\*HTTP Client\*\* | httpx | Async HTTP requests |

| \*\*Container\*\* | Docker | Production deployment |



\## 📁 Project Structure



```

GEMINI\_TDS\_PROJECT1/

├── main.py              # FastAPI app + orchestration logic

├── config.py            # Environment config with validation

├── models.py            # Pydantic request/response models

├── requirements.txt     # Python dependencies

├── Dockerfile           # Production container definition

├── .dockerignore        # Docker build exclusions

├── .gitignore           # Git exclusions

├── .env.example         # Template for environment variables

├── LICENSE              # MIT license

└── README.md            # This file

```



\## 📖 API Documentation



\### POST /ready



\*\*Description:\*\* Submit a task for AI-powered code generation and deployment



\*\*Request Body:\*\*

```json

{

&nbsp; "email": "user@example.com",

&nbsp; "secret": "your\_student\_secret",

&nbsp; "task": "unique-task-id",

&nbsp; "round": 1,

&nbsp; "nonce": "unique-request-id",

&nbsp; "brief": "Detailed description of what to build...",

&nbsp; "checks": \["Requirement 1", "Requirement 2"],

&nbsp; "evaluation\_url": "https://webhook.site/your-id",

&nbsp; "attachments": \[

&nbsp;   {

&nbsp;     "name": "logo.png",

&nbsp;     "url": "data:image/png;base64,iVBORw0KGgo..."

&nbsp;   }

&nbsp; ]

}

```



\*\*Response:\*\*

```json

{

&nbsp; "message": "Task received successfully!",

&nbsp; "task\_id": "unique-task-id"

}

```



\*\*Status Codes:\*\*

\- `200 OK` - Task accepted, processing in background

\- `403 Forbidden` - Invalid secret

\- `422 Unprocessable Entity` - Invalid request format



\### Callback Notification



When deployment completes, the API POSTs to your `evaluation\_url`:



```json

{

&nbsp; "email": "user@example.com",

&nbsp; "task": "unique-task-id",

&nbsp; "round": 1,

&nbsp; "nonce": "unique-request-id",

&nbsp; "repo\_url": "https://github.com/username/unique-task-id",

&nbsp; "commit\_sha": "abc123def456...",

&nbsp; "pages\_url": "https://username.github.io/unique-task-id"

}

```



\## 🧪 Testing



\### Test with Postman / cURL



\*\*1. Get a webhook URL:\*\*

\- Go to https://webhook.site

\- Copy your unique URL



\*\*2. Send test request:\*\*



```bash

curl -X POST http://localhost:8080/ready \\

&nbsp; -H "Content-Type: application/json" \\

&nbsp; -d '{

&nbsp;   "email": "test@example.com",

&nbsp;   "secret": "your\_student\_secret",

&nbsp;   "task": "hello-world-test",

&nbsp;   "round": 1,

&nbsp;   "nonce": "test-001",

&nbsp;   "brief": "Create a simple hello world webpage with a gradient background and centered text saying Hello World!",

&nbsp;   "checks": \["Has index.html", "Has MIT license", "Text displays"],

&nbsp;   "evaluation\_url": "YOUR\_WEBHOOK\_URL\_HERE",

&nbsp;   "attachments": \[]

&nbsp; }'

```



\*\*3. Check results:\*\*

\- API returns immediately: `{"message": "Task received successfully!"}`

\- Watch webhook.site for completion notification (~30-60 seconds)

\- Visit the `pages\_url` in notification to see live site



\### Example Tasks



<details>

<summary><b>Calculator App</b></summary>



```json

{

&nbsp; "email": "test@example.com",

&nbsp; "secret": "your\_secret",

&nbsp; "task": "calculator-app",

&nbsp; "round": 1,

&nbsp; "nonce": "calc-001",

&nbsp; "brief": "Create a calculator with: 1) Basic operations (+, -, ×, ÷), 2) Clear button, 3) Decimal support, 4) Keyboard input, 5) Responsive design with Tailwind CSS",

&nbsp; "checks": \[

&nbsp;   "Has MIT license",

&nbsp;   "README explains usage",

&nbsp;   "Calculator performs addition",

&nbsp;   "Calculator performs subtraction",

&nbsp;   "Has clear button",

&nbsp;   "Responsive design"

&nbsp; ],

&nbsp; "evaluation\_url": "https://webhook.site/your-id",

&nbsp; "attachments": \[]

}

```

</details>



<details>

<summary><b>Todo List</b></summary>



```json

{

&nbsp; "email": "test@example.com",

&nbsp; "secret": "your\_secret",

&nbsp; "task": "todo-list-app",

&nbsp; "round": 1,

&nbsp; "nonce": "todo-001",

&nbsp; "brief": "Create a todo list with: 1) Add new tasks, 2) Mark tasks as complete, 3) Delete tasks, 4) LocalStorage persistence, 5) Filter by All/Active/Completed, 6) Task counter, 7) Beautiful UI with animations",

&nbsp; "checks": \[

&nbsp;   "Can add tasks",

&nbsp;   "Can mark complete",

&nbsp;   "Can delete tasks",

&nbsp;   "Tasks persist on refresh",

&nbsp;   "Has filter buttons",

&nbsp;   "Shows task count"

&nbsp; ],

&nbsp; "evaluation\_url": "https://webhook.site/your-id",

&nbsp; "attachments": \[]

}

```

</details>



<details>

<summary><b>Chess Game (With Attachments)</b></summary>



```json

{

&nbsp; "email": "test@example.com",

&nbsp; "secret": "your\_secret",

&nbsp; "task": "chess-game-pro",

&nbsp; "round": 1,

&nbsp; "nonce": "chess-001",

&nbsp; "brief": "Create a chess game with: 1) Full chess rules, 2) Drag-and-drop pieces, 3) Move validation, 4) Check/Checkmate detection, 5) Timed modes (Blitz 5min, Rapid 10min), 6) Move history, 7) Captured pieces display",

&nbsp; "checks": \[

&nbsp;   "All pieces move correctly",

&nbsp;   "Check detection works",

&nbsp;   "Checkmate ends game",

&nbsp;   "Timer counts down",

&nbsp;   "Move history displays"

&nbsp; ],

&nbsp; "evaluation\_url": "https://webhook.site/your-id",

&nbsp; "attachments": \[]

}

```

</details>



\## 🐛 Troubleshooting



\### Common Issues



\*\*Problem:\*\* `403 Forbidden` response

\- \*\*Solution:\*\* Check that `secret` in request matches `STUDENT\_SECRET` env var



\*\*Problem:\*\* Task accepted but no notification received

\- \*\*Solution:\*\* Check Hugging Face Space logs or local console for errors. Common causes:

&nbsp; - Invalid GitHub token or insufficient permissions

&nbsp; - Gemini API quota exceeded

&nbsp; - Invalid evaluation\_url



\*\*Problem:\*\* GitHub API errors (403, 404)

\- \*\*Solution:\*\* Verify GitHub token has `repo` scope:

&nbsp; ```bash

&nbsp; curl -H "Authorization: token YOUR\_TOKEN" https://api.github.com/user

&nbsp; ```



\*\*Problem:\*\* Gemini AI returns invalid JSON

\- \*\*Solution:\*\* Check logs for response. The system now has improved error handling with specific error messages.



\*\*Problem:\*\* Pages deployment times out

\- \*\*Solution:\*\* GitHub Pages can take 1-2 minutes to activate. The system retries 5 times with exponential backoff.



\### Debug Mode



Enable detailed logging:

```python

\# In main.py, add at top:

import logging

logging.basicConfig(level=logging.DEBUG)

```



Or set environment variable:

```bash

export LOG\_LEVEL=DEBUG  # Linux/Mac

$env:LOG\_LEVEL="DEBUG"  # Windows PowerShell

```



\### Viewing Logs



\*\*Docker:\*\*

```bash

docker logs -f CONTAINER\_ID

```



\*\*Hugging Face Space:\*\*

Go to Space → "Logs" tab



\## 🔒 Security Best Practices



1\. \*\*Never commit `.env` file\*\* - Already in `.gitignore`

2\. \*\*Rotate API keys regularly\*\* - Every 90 days recommended

3\. \*\*Use environment-specific secrets\*\* - Different keys for dev/prod

4\. \*\*Limit GitHub token scope\*\* - Only `repo` or `public\_repo` needed

5\. \*\*Validate incoming requests\*\* - `secret` field prevents unauthorized access

6\. \*\*Monitor API usage\*\* - Check Gemini and GitHub API quotas



\## 📈 Performance \& Limits



| Metric | Value | Notes |

|--------|-------|-------|

| Average task duration | 30-60s | Depends on complexity |

| Gemini API rate limit | 15/min | Free tier |

| GitHub API rate limit | 5000/hour | Authenticated |

| Max attachment size | ~10MB | Base64 encoding adds 33% |

| Concurrent tasks | Unlimited | Background processing |



\## 🤝 Contributing



Contributions welcome! Areas for improvement:

\- \[ ] Add support for GitLab/Bitbucket deployment

\- \[ ] Implement task queue with Redis

\- \[ ] Add progress tracking API

\- \[ ] Support multiple AI models (Claude, GPT-4)

\- \[ ] Add unit tests

\- \[ ] Implement rate limiting

\- \[ ] Add metrics/monitoring



\## 📄 License



MIT License - see \[LICENSE](LICENSE) file for details



\## 🙏 Acknowledgments



\- \*\*Google Gemini AI\*\* - Code generation capabilities

\- \*\*FastAPI\*\* - Modern Python web framework

\- \*\*GitHub\*\* - Repository hosting and Pages deployment

\- \*\*Hugging Face\*\* - Spaces platform for easy deployment



---



\*\*Built for TDS Project 1\*\* - Automated task generation and deployment system

