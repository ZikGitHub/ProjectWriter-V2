# ProjectWriter-V2: Autonomous Software Developer Engine

ProjectWriter-V2 is a production-ready, autonomous, self-healing development engine engineered for Small Language Models (SLMs). It utilizes a state-driven execution loop with parallel micro-task nodes to overcome SLM context limits.

## 🚀 Key Features

- **Async Execution:** Powered by FastAPI and Uvicorn for ultra-low latency iterations.
- **Local Intelligence:** Uses Ollama with `qwen2.5-coder:1.5b` (Coding) and `llama3.2:1b` (Planning).
- **Self-Healing:** Automated traceback interception and Just-In-Time (JIT) Web-Search RAG.
- **Dockerized Architecture:** Modular services orchestrated via Docker Compose.
- **Interactive Dashboard:** Real-time IDE-like workspace with live file tree and logs.

## 🛠️ Technology Stack

- **Backend:** FastAPI, Uvicorn, Pydantic, Redis.
- **Frontend:** React, TypeScript, Vite, TailwindCSS, Axios.
- **AI/LLM:** Ollama (Local SLMs).
- **Orchestration:** Docker, Docker Compose.

## 📋 Prerequisites

- [Docker](https://www.docker.com/get-started) & Docker Compose.
- [Ollama](https://ollama.com/) installed and running on your host (if not using the Dockerized Ollama service).

## 🏃 Getting Started

### 1. Prerequisites
- **Docker & Docker Compose:** Installed and running.
- **Ollama:** (Optional) If you want to use a host-level Ollama instance instead of the dockerized one.

### 2. Startup Orchestration
From the root of the project, run:
```bash
docker-compose up --build -d
```
*The `-d` flag runs it in the background. Remove it if you want to see live logs from all services.*

### 3. Model Initialization (Crucial)
The engine requires specific Small Language Models (SLMs) to function. Run the initialization script inside the API container:
```bash
docker exec -it api-gateway python setup_models.py
```
This will pull:
- `llama3.2:1b` (Planner)
- `qwen2.5-coder:1.5b` (Coder)

### 4. Access Points
- **UI Dashboard:** [http://localhost:3000](http://localhost:3000)
- **API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redis Insight:** (If you have it installed) [http://localhost:6379](http://localhost:6379)

## ✅ Verification Steps

To ensure everything is working correctly, follow these steps:

1. **Check Service Status:**
   ```bash
   docker-compose ps
   ```
   All services (`api-gateway`, `ui-dashboard`, `ollama`, `redis`) should be "Up".

2. **Verify API Connectivity:**
   Visit `http://localhost:8000/` in your browser. You should see:
   ```json
   {"message": "ProjectWriter-V2 Engine Active", "status": "online"}
   ```

3. **Verify Ollama Models:**
   Check if the models were pulled successfully:
   ```bash
   docker exec -it ollama ollama list
   ```
   You should see `llama3.2:1b` and `qwen2.5-coder:1.5b` in the list.

4. **Run a Test Plan:**
   - Open the Dashboard ([http://localhost:3000](http://localhost:3000)).
   - Click **"Init Project"**.
   - Enter a simple request like "Create a hello world python script".
   - Click **"Plan"** and watch the task list populate.

## 🕹️ How to Use

1. **Initialize Project:** Click the "Init Project" button on the dashboard to set up the workspace state.
2. **Enter Feature Request:** Type your request in the input field (e.g., "Create a simple Todo API with FastAPI").
3. **Generate Plan:** Click **"Plan"**. The `llama3.2:1b` model will decompose your request into modular tasks.
4. **Execute:** Click **"Run"**. The `qwen2.5-coder:1.5b` model will start generating code for each task in parallel.
5. **Monitor:** Watch the **Active Logs** and **Workspace Tree** update in real-time as the engine writes and validates code.

## 📁 Project Structure

- `/backend`: FastAPI source code, models, and orchestration logic.
- `/frontend`: React + TypeScript dashboard.
- `/generated_project`: The output directory where the engine writes your software.
- `docker-compose.yml`: Orchestration configuration.
- `initial_plan.md`: The technical blueprint of the engine.

## 🛡️ Self-Healing Mechanism

If a task fails syntax validation or a test case, the **Self-Heal-Node** intercepts the error. It uses JIT RAG to search for documentation and attempts to patch the code automatically before re-running the validation loop.

## 📄 License

MIT License - See LICENSE for details.
