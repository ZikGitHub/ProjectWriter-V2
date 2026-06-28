import asyncio
import os
import sys
import argparse

# Add current directory to path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from planner import Planner
from orchestrator_v2 import Orchestrator
from state_manager import StateManager
from logger_config import setup_logging

async def main():
    parser = argparse.ArgumentParser(description="ProjectWriter-V2 CLI")
    parser.add_argument("prompt", type=str, help="The project request or prompt")
    parser.add_argument("--execute", action="store_true", help="Execute the generated plan")
    args = parser.parse_args()

    setup_logging()
    state_manager = StateManager(base_dir="./workspace")
    planner = Planner()
    orchestrator = Orchestrator(state_manager)
    
    print(f"\n[CLI] Processing Request: {args.prompt}")
    
    try:
        # 0. Initialize unique project
        project_id = state_manager.set_project("cli_project")
        print(f"\n[INFO] Workspace initialized at: workspace/{project_id}")
        
        # 1. Planning
        tasks = await planner.decompose_request(args.prompt)
        state = state_manager.load_state()
        state.tasks = tasks
        state_manager.save_state()
        
        print(f"\n[SUCCESS] Generated {len(tasks)} tasks.")
        
        # 2. Optional Execution
        if args.execute:
            print("\n[CLI] Starting execution...")
            await orchestrator.run_execution_loop()
            print(f"\n[SUCCESS] Execution complete. Check the 'workspace/{project_id}' directory.")
        else:
            print("\n[INFO] Use --execute to run these tasks.")
            
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
