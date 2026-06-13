================================================================================
V2 AUTONOMOUS SOFTWARE DEVELOPER ENGINE: COMPREHENSIVE TECHNICAL SPECIFICATION
================================================================================

1. PROJECT VISION & OBJECTIVES
--------------------------------------------------------------------------------
This specification establishes a production-ready, autonomous, self-healing development engine optimized for Small Language Models (SLMs). The engine moves away from monolithic code generation toward a deterministic, state-driven execution loop using parallel micro-task nodes.

Key Objectives:
* Context Efficiency: Rigid prompt limits (<4,000 tokens) to eliminate attention decay.
* Ultra-Low Latency: Async execution using FastAPI/Uvicorn for <30s iterations.
* Local-First Intelligence: Powered by Ollama (qwen2.5-coder:1.5b for coding, llama3.2:1b for planning).
* Self-Healing Execution: Automated traceback interception and JIT Web-Search RAG.
* User Trust Workspace: Interactive IDE dashboard mirroring live filesystem changes.
* Dockerized Modularity: Phase-based isolation using Docker Compose.

2. END-TO-END ENGINE ARCHITECTURE TOPOLOGY
--------------------------------------------------------------------------------
The execution topology is orchestrated via FastAPI/Uvicorn across Dockerized nodes:

[User Input / UI Dashboard]
       │
       ▼ (Container: API-Gateway)
[1. STATE SELECTOR NODE] ◄─── (Scans Local Directory & Hydrates state.json)
       │
       ▼ (Container: Planner-Node - llama3.2:1b)
[2. SUPERVISOR PLANNER]  ──── (Forks Concurrent Async Component Planners)
       │
       ▼
[3. PLAN RECTIFIER NODE] ──── (Performs Contract Aggregation & Topological Sort)
       │
       ▼ (Container: Coder-Node - qwen2.5-coder:1.5b)
[4. ARCHITECTURE AGENT]  ──── (Generates Schemas, Mock Contracts, Folder Stubs)
       │
       ├───────────────────────────────┐ (Forks Async Independent Writing Tasks)
       ▼                               ▼
[Parallel File Writer 1]       [Parallel File Writer 2]
       │                               │
[Local Structural Check]       [Local Structural Check]
       │                               │
       └───────────────┬───────────────┘ (Map-Reduce Join/Merge Point)
                       ▼
         [5. GLOBAL INTEGRATION SYNC] ◄─── [LANGGRAPH BREAKPOINT / INTERRUPT]
                       │                   (Halts for Manual In-IDE Overrides)
         ┌─────────────┴─────────────┐
         ▼ (Container: Self-Heal-Node) ▼
   [Build Passes]              [Build Fails]
         │                           │
         ▼                           ▼
[7. STATE PERSISTER]        [6. PROBLEM IDENTIFIER & FIXER] ◄── JIT Web Search RAG
         │                           │
         ▼                           ▼
   [Process Complete]       (Re-injects Patched Source files into Sync Node)

3. COMPONENT FUNCTIONAL SPECIFICATIONS
--------------------------------------------------------------------------------

PHASE 1: INITIALIZATION & STRUCTURAL PLANNING
* 1. State Selector (The Context Reconstructor)
  * Operation: Scans `./generated_project/`, parses AST to map modules, and hydrates `state.json`.
  * Technical: Python-based AST parser running in the API-Gateway container.
* 2. Supervisor Planner (llama3.2:1b)
  * Operation: Breaks global feature requests into isolated boundaries (Auth, DB, API).
  * Technical: Concurrent async worker tasks managed via FastAPI/asyncio.
* 3. Plan Rectifier (The Knowledge Transfer Layer)
  * Operation: Aggregates parallel execution matrices and performs Topological Sort (DAG).
  * Contract: Components register via JSON schema (e.g., `"Provides: JWT, Requires: DataModel"`).

PHASE 2: RUNTIME EXECUTION & MACHINE SELF-HEALING
* 4. Architecture Agent & File Writers (qwen2.5-coder:1.5b)
  * Operation: Standardizes abstract properties into explicit coding models (Pydantic/Mocks).
  * Implementation: Async File Writers stream code into stubs and fire local syntax checks.
* 5. Global Integration Sync
  * Operation: Triggers project compilation loop (`pytest`, `tsc`, `vite build`) in <3s.
* 6. Problem Identifier & Fixer (JIT Web RAG)
  * Operation: Isolates broken file paths, feeds traceback to troubleshooting SLM, and patches source.
  * JIT RAG: Pulls documentation on demand (Tavily/Serper) to prevent syntax hallucinations.

4. IMPLEMENTATION ROADMAP (DOCKERIZED MODULES)
--------------------------------------------------------------------------------

MODULE 1: INFRASTRUCTURE (FastAPI + Docker)
* 1.1: Docker Compose Setup (API, Ollama, UI, Redis).
* 1.2: FastAPI Base with Uvicorn ASGI configuration.
* 1.3: State Engine & `state.json` persistence layer.

MODULE 2: PLANNING & DAG (llama3.2:1b)
* 2.1: Async Supervisor prompts for task decomposition.
* 2.2: DAG Rectifier for dependency resolution.
* 2.3: Contract Pydantic schemas for data exchange.

MODULE 3: GENERATION (qwen2.5-coder:1.5b)
* 3.1: Architecture Agent directory/stub builder.
* 3.2: Parallel File Writers using `asyncio.gather`.
* 3.3: Headless validation (syntax/test) service.

MODULE 4: SELF-HEALING (JIT RAG)
* 4.1: Traceback parser & JIT Search API integration.
* 4.2: Automated code patcher & re-verification loop.

MODULE 5: DASHBOARD (React + WebSocket)
* 5.1: Real-time File Tree (React-Arborist).
* 5.2: Monaco Editor streaming integration.

5. FRONT-END INTERACTIVE IDE DASHBOARD WORKSPACE
--------------------------------------------------------------------------------
Visual UI Structure:
+--------------------------------------------------------------------------------+
| BAR: [Phase: Injecting Code] | [Active SLM: Qwen2.5-Coder] | [Latency: 120ms]  |
+--------------------------------------------------------------------------------+
| 📁 WORKSPACE TREE      | 📝 SYNTAX HIGH-LIGHTED CODE VIEW                      |
| (React-Arborist)       | (Monaco Editor / CodeMirror)                          |
|  📁 app/               |  1  from pydantic import BaseModel                    |
|    📁 routes/          |  2                                                     |
|      📄 auth.py 🟢      |  3  class UserSchema(BaseModel):                       |
|    📁 database/        |  4      email: str                                     |
|      📄 db.py 🟡        |  5      password: str                                  |
+------------------------+--------------------------------------------------------+
| 🚀 TERMINAL COMPILER MONITOR & LOG TRACE ENGINE                                |
| $ pytest app/test_auth.py                                                     |
| ❌ AttributeError: 'BaseSettings' object has no attribute 'validator'         |
| 🤖 System: Querying JIT RAG for Pydantic v2 validator migration...             |
+--------------------------------------------------------------------------------+
