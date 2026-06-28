from fastapi import FastAPI, BackgroundTasks, HTTPException
from models import ProjectState, ProjectTask
from state_manager import StateManager
from planner import Planner
from orchestrator_v2 import Orchestrator
from logger_config import setup_logging, get_logger
import os

# Initialize logging
setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="ProjectWriter-V2 API Gateway")
logger.info("API Gateway starting up...")
state_manager = StateManager(base_dir="./workspace")
planner = Planner()
orchestrator = Orchestrator(state_manager)
# ...

@app.on_event("startup")
async def startup_event():
    if not os.path.exists("./workspace"):
        os.makedirs("./workspace")
    state_manager.load_state()

@app.get("/")
async def root():
    return {"message": "ProjectWriter-V2 Engine Active", "status": "online"}

@app.get("/state")
async def get_state():
    return state_manager.load_state()

@app.post("/initialize")
async def initialize_project(project_name: str):
    logger.info(f"Initializing project: {project_name}")
    project_id = state_manager.set_project(project_name)
    state = state_manager.load_state()
    return {"message": f"Project {project_name} initialized", "project_id": project_id, "state": state}

@app.post("/plan")
async def generate_plan(user_request: str):
    logger.info(f"Generating plan for request: {user_request[:50]}...")
    try:
        tasks = await planner.decompose_request(user_request)
        state = state_manager.load_state()
        state.tasks = tasks
        state_manager.save_state()
        logger.info(f"Plan generated successfully with {len(tasks)} tasks")
        return {"message": "Plan generated successfully", "tasks": tasks}
    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
async def execute_tasks(background_tasks: BackgroundTasks):
    logger.info("Starting execution loop")
    background_tasks.add_task(orchestrator.run_execution_loop)
    return {"message": "Execution loop started in background"}
