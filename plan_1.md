# Project Roadmap: ProjectWriter-V2

**Role:** Lead AI Core Architect & Senior Software Engineer  
**Target Repository:** ProjectWriter-V2 (FastAPI, Redis, Docker, LangGraph, Ollama backend / Vite, React, Vanilla CSS frontend)  
**Objective:** Systematically implement a 6-phase engineering plan to transform ProjectWriter-V2 into a highly concurrent, schema-safe, and self-healing agent engine.

---

## === CURRENT STATUS (June 13, 2026) ===

- **Core Engine:** Operational. Backend (FastAPI), Frontend (Vite/React), and Ollama/Redis connectivity established.
- **Code Generation:** Successful conversion to enforced Python output.
- **Execution Loop:** Basic sequential/parallel task execution is functional.
- **Immediate Bottlenecks:** System currently relies on basic sequential task execution. Needs the planned architectural transition to LangGraph/Branching to handle complex projects effectively.

---

## PHASE 1: LANGGRAPH ASYNC BRANCHING (MAP-REDUCE TOPOLOGY) - [IN PROGRESS]

1.1 **Define localized `TaskState(TypedDict)` containing:**
    - `file_path`: str
    - `instruction`: str
    - `target_model`: str
    - `current_code`: Optional[str]

1.2 **Implement a Dispatcher Node** that parses the global execution plan and yields a list of `Send("execute_node", task_state)` instances.

1.3 **Implement the `Global Integration Sync` node** as a reducer that aggregates concurrent outputs, handles merge conflicts, and updates the primary state graph.

---

## PHASE 2: SCHEMA ENFORCEMENT & SHARED CONTRACTS

2.1 **Implement an `Interface Architect Agent` node** running post-planning phase. It must generate an immutable `openapi.json` / `api_contract.ts` file in the root workspace.

2.2 **Update the state schema** to hold a `contract_snapshot` variable.

2.3 **Refactor System Prompts** for Frontend and Backend Agent nodes to aggressively parse and align all generated code against this schema snapshot.

---

## PHASE 3: STRUCTURED OUTPUT HARDENING

3.1 **Integrate the `instructor` library** or LangChain's `.with_structured_output()` syntax to wrap the local Ollama clients (`llama3.2:1b` and `qwen2.5-coder:1.5b`).

3.2 **Define Pydantic models** for code generation, architectural planning, and self-healing error structures.

3.3 **Implement an inline validation interceptor middleware** to catch raw text strings or structural markdown errors before they enter the state nodes, auto-retrying with an error log on failure.

---

## PHASE 4: HEADLESS MOCK-BASED LOCAL VERIFICATION SUITE

4.1 **Build a `Test Generator Agent` node** to autonomously write complementary mock tests (`test_*.py` via pytest or `*.test.ts` via vitest).

4.2 **Write an isolated execution engine block** using Python's `subprocess` to trigger headless runs safely inside the workspace container.

4.3 **Capture `stdout`/`stderr` stack traces** and map test breakages into structured JSON payloads for the `Self-Heal-Node`.

---

## PHASE 5: TWO-TIER REDIS RAG CACHE

5.1 **Configure the current Redis backend** to act as a document-store cache mapping `sha256(search_query)` keys to raw markdown text.

5.2 **Build a middleware lookup function** inside the JIT Web-Search utility tool to intercept outgoing API queries and pull from Redis first.

5.3 **Apply a strict 48-hour Time-To-Live (TTL) rule** on all cached entries.

---

## PHASE 6: SERVER-SENT EVENTS (SSE) LIVE TOKEN STREAMING

6.1 **Create a FastAPI asynchronous router** utilizing `sse_starlette.sse.EventSourceResponse`.

6.2 **Design a custom `AsyncIteratorCallbackHandler`** and bind it into the LangGraph streaming configuration loop.

6.3 **Provide clear frontend structural examples** for consuming the token stream hooks within the React application.
