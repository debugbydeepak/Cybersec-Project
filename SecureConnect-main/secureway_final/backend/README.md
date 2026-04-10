
# SECUREWAY Agentic Backend (Prototype)

This backend implements the "Autonomous Logic Engine" using a high-performance Python/Rust hybrid stack.

## 🏗 Tech Stack Architecture

1.  **Core API**: `Python 3.12` + `FastAPI` (Async I/O)
2.  **Performance Layer**: `Rust` Extensions (Simulated in `services/rust_binding.py`) for regular expressions and packet hashing.
3.  **Task Queue**: `Celery` + `Redis` for distributed crawling tasks.
4.  **Agentic Discovery**: `Playwright` (Simulated in `services/playwright_service.py`) for Shadow DOM traversal.
5.  **Logic Engine**: `Google Gemini 2.0` (Simulated via `services/gemini_service.py`) for cognitive reasoning.
6.  **Anomaly Detection**: `PyOD` (Python Outlier Detection) for behavioral analysis.
7.  **Data Protection**: `Microsoft Presidio` for PII Scrubbing.
8.  **Knowledge Base**: `Pinecone` Vector DB (Simulated in `services/pinecone_service.py`) for attack fingerprinting.

## 🚀 How to Run (Local Prototype)

Since this is a Hackathon Prototype, we've included a self-contained simulation mode that runs without external API keys or heavy dependencies.

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```
*(Note: For the prototype, standard libraries like `random` and `time` are used to simulate heavy ML modules if they are not installed.)*

### 2. Run the Server
The entry point is configured to run `uvicorn` programmatically.

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

## 📂 Project Structure

- `app/`
    - `api/` - REST Endpoints
    - `core/` - Configuration (Celery, Redis)
    - `services/` - The Logic Engines (Playwright, Gemini, PyOD, Rust bindings)
- `main.py` - Application Entry Point
- `Dockerfile` - Production container specification
