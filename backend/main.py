from fastapi import FastAPI, BackgroundTasks, HTTPException
from models import ProjectState, ProjectTask
from state_manager import StateManager
from planner import Planner
from orchestrator import Orchestrator
import os

app = FastAPI(title="ProjectWriter-V2 API Gateway")
state_manager = StateManager(state_dir="./generated_project")
planner = Planner()
orchestrator = Orchestrator(state_manager)

@app.on_event("startup")
async def startup_event():
    if not os.path.exists("./generated_project"):
        os.makedirs("./generated_project")
    state_manager.load_state()

@app.get("/")
async def root():
    return {"message": "ProjectWriter-V2 Engine Active", "status": "online"}

@app.get("/state")
async def get_state():
    return state_manager.load_state()

@app.post("/initialize")
async def initialize_project(project_name: str):
    state = state_manager.load_state()
    state.project_name = project_name
    state_manager.save_state()
    return {"message": f"Project {project_name} initialized", "state": state}

@app.post("/plan")
async def generate_plan(user_request: str):
    try:
        tasks = await planner.decompose_request(user_request)
        state = state_manager.load_state()
        state.tasks = tasks
        state_manager.save_state()
        return {"message": "Plan generated successfully", "tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
async def execute_tasks(background_tasks: BackgroundTasks):
    background_tasks.add_task(orchestrator.run_execution_loop)
    return {"message": "Execution loop started in background"}
