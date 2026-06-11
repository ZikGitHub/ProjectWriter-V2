================================================================================
V2 AUTONOMOUS SOFTWARE DEVELOPER ENGINE: COMPREHENSIVE SPECIFICATION REFERENCE
================================================================================

1. PROJECT VISION & OBJECTIVES

--------------------------------------------------------------------------------
This specification establishes a production-ready, autonomous, self-healing
development engine engineered specifically for Small Language Models (SLMs)
(such as Llama-3-8B or Mistral-7B). The core operating thesis moves away from
monolithic, high-context code generation, establishing a highly deterministic,
state-driven execution loop using parallel micro-task nodes.

Key Objectives:

* Context Efficiency: Enforces rigid prompt limits (<4,000 tokens) to maintain the
  SLM's optimal reasoning capability and eliminate attention decay.
* Ultra-Low Latency: Implements concurrent async multi-threading pipelines to
  drive complete execution iterations under 30 seconds.
* Self-Healing Execution: Automatically intercepts runtime/compiler tracebacks,
  proactively executes live Web-Search RAG, patches source code, and re-tests.
* User Trust Workspace: Provides an absolute, transparent layout mirroring
  live filesystem directory changes directly to an interactive IDE dashboard.

1. END-TO-END ENGINE ARCHITECTURE TOPOLOGY

--------------------------------------------------------------------------------
The execution topology maps directly to the following execution sequence:

[User Input or Project Rerun Trigger]
       │
       ▼
[1. STATE SELECTOR NODE] ◄─── (Scans Local Directory & Hydrates state.json)
       │
       ▼
[2. SUPERVISOR PLANNER]  ──── (Forks Concurrent Async Component Planners)
       │
       ▼
[3. PLAN RECTIFIER NODE] ──── (Performs Contract Aggregation & Topological Sort)
       │
       ▼
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
         ▼                           ▼
   [Build Passes]              [Build Fails]
         │                           │
         ▼                           ▼
[7. STATE PERSISTER]        [6. PROBLEM IDENTIFIER & FIXER] ◄── JIT Web Search RAG
         │                           │
         ▼                           ▼
   [Process Complete]       (Re-injects Patched Source files into Sync Node)

1. COMPONENT FUNCTIONAL SPECIFICATIONS

--------------------------------------------------------------------------------

PHASE 1: INITIALIZATION & STRUCTURAL PLANNING

* 1. State Selector (The Context Reconstructor)
  * Execution Rule: Triggers instantly on initial boot or consecutive rerun loops.
  * Operation: Scans the target workspace root folder (`./generated_project/`),
    parses existing files, evaluates Abstract Syntax Trees (AST) to map
    existing code modules, and parses the historical `state.json` tracker file.
  * Output: Restores the system state ledger, allowing executions to resume
    exactly where they halted, bypassing already-completed code files.

* 1. Supervisor Planner & Parallel Domain Workers
  * Execution Rule: Activated when new features are requested or plan adjustments occur.
  * Operation: The Supervisor breaks the global feature request into isolated
    boundaries (e.g., "Authentication System", "Database Layer", "API Endpoints").
    It launches asynchronous worker tasks across all domains concurrently.
  * Sub-task Logic: Every worker runs a highly specific SLM instruction block,
    mapping out a task checklist restricted exclusively to its structural domain.

* 1. Plan Rectifier (The Knowledge Transfer & Sorting Layer)
  * Execution Rule: Aggregates parallel execution matrices from step 2.
  * Contract-Based Knowledge Exchange: Forces workers to communicate via strict
    data contracts instead of unstructured sentences. Components register using
    JSON schema objects (e.g., `"Provides: JWT_Object, Requires: Data_Model"`).
  * Topological Sorting: Processes the data contracts using a deterministic
    topological sort algorithm. It models components as a Directed Acyclic Graph
    (DAG), ensuring foundations (like data schemas) are compiled before
    dependent layers (like routes) are built.
  * Output: Compiles a flattened, step-by-step sequential "Master Execution Queue".

* 1. Architecture Agent (The Interface Gatekeeper)
  * Execution Rule: Operates prior to code generation.
  * Operation: Analyzes the Master Execution Queue. Standardizes abstract
    properties into explicit coding models, mock signatures, and validation
    parameters (such as Pydantic declarations) to guide generation workers.
    Physically builds the folder directory layout and places empty file stubs.

PHASE 2: RUNTIME EXECUTION & MACHINE SELF-HEALING

* 1. Component Writers & Global Integration Sync
  * Map Phase: Launches concurrent File Writer instances across individual file stubs.
    Each worker receives only its assigned micro-task file logic and schema contracts.
    It streams code into the file stub and fires a local syntax validation check.
  * Reduce Phase: Merges the independent code streams. Triggers a full project
    compilation loop via headless validation shells (`pytest`, `tsc`, `vite build`)
    in under 3 seconds to catch logical or structural integration anomalies.

* 1. Problem Identifier & Fixer (With Just-In-Time Web RAG)
  * Execution Rule: Activates only if the Global Sync node captures a standard
    error (`stderr`) payload or testing stack trace.
  * Operation: Isolates the broken file paths, feeds the traceback string to a
    troubleshooting SLM context layer, updates code structure on disk, and routes
    the system back into the Global Integration Sync verification loop.

* 1. State Persister (The Engine Ledger)
  * Execution Rule: Executes upon milestone completion or terminal error halts.
  * Operation: Formats internal dependency modifications, active token registries,
    source block modifications, and remediation logs, writing it down to disk.

1. JUST-IN-TIME (JIT) WEB-SEARCH RAG ENGINE

--------------------------------------------------------------------------------
To prevent syntax hallucinations on fast-moving libraries (like Ragas evaluations,
FastAPI OAuth2 schemas, or Pydantic updates), the system pulls documentation
on demand to update worker prompts.

[Target Node Needs Info / Encounters Exception]
                       │
                       ▼
       [1. SEARCH QUERY PROMPT ENFORCER]
(Transforms errors/goals into a precise, targeted search query string)
                       │
                       ▼
       [2. LLM-OPTIMIZED WEB API SEARCH]
(Hits Tavily / Serper API to return raw Markdown documentation in <1 second)
                       │
                       ▼
       [3. CONTEXT EXTRACTOR & COMPRESSOR]
(Strips HTML/fluff, isolates code blocks/signatures, injects into target worker)

1. FRONT-END INTERACTIVE IDE DASHBOARD WORKSPACE

--------------------------------------------------------------------------------
To resolve the trust gap, the agent streams live operations to an interactive
IDE interface via WebSockets or Server-Sent Events (SSE) data pipelines.

Visual UI Structure:
+--------------------------------------------------------------------------------+

| BAR: [Phase: Injecting Code] | [Active SLM: Llama3-8B] | [Tokens: 14,210]     |
+--------------------------------------------------------------------------------+

| 📁 WORKSPACE TREE      | 📝 SYNTAX HIGH-LIGHTED CODE VIEW                      |
|                        |                                                        |
|  📁 app/               |  1  from pydantic import BaseModel                    |
|    📁 routes/          |  2                                                     |
|      📄 auth.py 🟢      |  3  class UserSchema(BaseModel):                       |
|    📁 database/        |  4      email: str                                     |
|      📄 db.py 🟡        |  5      password: str                                  |
|                        |                                                        |
+------------------------+--------------------------------------------------------+

| 🚀 TERMINAL COMPILER MONITOR & LOG TRACE ENGINE                                |
|  $ pytest app/test_auth.py                                                     |
|  ❌ AttributeError: 'BaseSettings' object has no attribute 'validator'         |
|  🤖 System Notification: Querying JIT RAG for Pydantic v2 validator migration...|
+--------------------------------------------------------------------------------+

Dashboard Component Matrix:

* Virtualized File Explorer: Built via high-speed structural tree components
  (e.g., `React-Arborist`). Flags active statuses using color codes:
  * 🟢 Green Badge: Component compiled successfully, unit/integration test passed.
  * 🟡 Yellow Badge: Parallel Worker currently has an open file lock and is writing.
  * 🔴 Red Badge: Compiler check failed; Problem Fixer loop is actively targeting it.
* Production-Grade Code Canvas: Integrates `Monaco Editor` (the open-source engine
  behind VS Code) or `CodeMirror`. Renders themes, active line metrics, and syntax
