# SECUREWAY / SentinelNexus AI – Prototype Architecture

## 1. High-level overview

This repo contains a **frontend-only security dashboard prototype** plus a **mock backend scanner API**.

- **Goal**: Pitch SentinelNexus AI – an autonomous AI-powered web security platform – with a realistic SaaS UI and fake but believable scan flows.
- **Stack**:
  - **Frontend**: Next.js (App Router), React, TailwindCSS v4, Chart.js + react-chartjs-2.
  - **Backend mock**: FastAPI, Uvicorn, Pydantic.
  - **Optional infra**: Dockerfile for the backend.

The prototype is designed for **demo / hackathon / investor decks**, not production use.

---

## 2. Frontend (Next.js) structure

Root folder: `secureway/`

- `src/app/layout.tsx`
  - Global layout wrapper.
  - Loads **Geist** font, imports `globals.css`.
  - Sets `<head>` metadata:
    - Title: `SECUREWAY | SentinelNexus AI – Autonomous Web Security`.
    - Description focused on AI web security and logic vulnerabilities.

- `src/app/globals.css`
  - Tailwind v4 entry (`@import "tailwindcss";`).
  - Defines **dark neumorphic theme**:
    - CSS variables for background, foreground, accent colors.
    - Radial gradient background and cyber grid overlay.
    - Utility classes:
      - `.nx-container`, `.nx-section` – layout spacing.
      - `.nx-card` – glassy / elevated cards.
      - `.nx-badge`, `.nx-eyebrow` – label styles.
      - `.nx-gradient-text` – gradient heading text.
      - `.nx-btn-primary`, `.nx-btn-ghost` – pill-shaped CTA buttons.

- `src/app/page.tsx` (main UI – can later be split into components)
  - Marked with `"use client"` because it uses React state and browser APIs.
  - Imports Chart.js + `react-chartjs-2` for the **vulnerability severity chart**.

### 2.1 State and behaviors

Inside `Home()` component:

- `scanStatus: "idle" | "running" | "completed"`
  - Drives the **Live Scan** status pill, security score animation, and attack timeline.

- `score: number`
  - Controls the security score bar width.

- `chatInput: string`, `chatMessages: { role: "user" | "assistant"; content: string }[]`
  - Power the **SentinelNexus copilot** chat panel.
  - Replies are generated on the client using simple keyword matching – no real LLM call.

- `handleStartScan()`
  - When user presses **Start Scan**:
    1. Sets state to `running`, resets score to 86.
    2. `POST http://localhost:8000/scan/start` with body `{ target_url }`.
    3. Reads `scan_id` from the response.
    4. Immediately calls `GET http://localhost:8000/scan/status/{scan_id}`.
    5. Updates `score` and `scanStatus` based on the FastAPI response.
    6. If the backend is unavailable, falls back to a local timeout that sets
       `score = 92` and `scanStatus = "completed"` after ~2 seconds.

- `handleChatSubmit()`
  - Pushes the user message into `chatMessages`.
  - Chooses a canned assistant reply based on keywords:
    - Mentions of **BOLA / authorization** → explain how BOLA detection works.
    - **Score / risk** → explain how the security score is derived.
    - **How + work** → high-level pipeline explanation.

### 2.2 Main sections on the page

Rendered in order from top to bottom:

1. **Navbar**
   - Brand mark ("S"), `SECUREWAY` label, `SentinelNexus AI` eyebrow.
   - Nav links (Features, Dashboard, Workflow, Pricing).
   - `Request Demo` ghost pill.

2. **Hero + Dashboard Preview**
   - Left: headline, subtext, `Start Scan` + `View Architecture` buttons.
   - Right: **Live Scan card**:
     - Security score gauge.
     - Chart.js bar chart of findings by severity.
     - Agent activity list.
     - Short description of the scanned flow.

3. **Copilot AI Assistant section**
   - Description of SentinelNexus copilot.
   - Chat panel where user can type questions and see mock answers.

4. **About & Key Features**
   - Explains autonomous red-teaming and AI behavioral scanning.
   - Highlights React/Next.js focus and modern app challenges.

5. **Technology Stack**
   - Grid of cards listing Backend, AI Layer, Scanning Engine, Data, Security, and Infrastructure.

6. **Attack Simulation Timeline**
   - Animated horizontal bar showing phases: Recon → Traversal → Privilege test → Exploit chain → Reporting.
   - Uses `scanStatus` to animate differently when a scan is running.

7. **Workflow**
   - Five cards: Crawl → Behavioral analysis → Attack simulation → Vulnerability reasoning → Secure reporting.

8. **Security & Privacy + Pricing**
   - Security guarantees (encryption, zero-knowledge, PII masking, enterprise controls).
   - Pricing tiles: Lite, Guardian, Compliance, Enterprise.

9. **Footer**
   - Reminder this is a **prototype UI**.
   - Placeholder links for docs and GitHub/research.
   - Demo contact line.

---

## 3. Backend mock (FastAPI)

Location: `backend/`

- `main.py`
  - Creates a FastAPI app titled `"SentinelNexus Mock Scanner"`.
  - Enables CORS for `http://localhost:3000`.

### 3.1 Data models

- `StartScanRequest`
  - `target_url: str`

- `StartScanResponse`
  - `scan_id: str`
  - `status: str`

- `ScanStatusResponse`
  - `scan_id: str`
  - `status: str`
  - `score: int`
  - `critical: int`
  - `high: int`
  - `medium: int`
  - `low: int`

An in-memory dictionary `_scan_states` holds scan state while the server is running.

### 3.2 Endpoints

- `POST /scan/start`
  - Generates a UUID `scan_id`.
  - Stores a `ScanStatusResponse` with `status="running"` and default finding counts.
  - Returns `StartScanResponse(scan_id, "running")`.

- `GET /scan/status/{scan_id}`
  - Looks up the `ScanStatusResponse` in `_scan_states`.
  - If missing, returns a `not_found` status with zeroed counts.
  - If status is `running`, it simulates completion by updating:
    - `status = "completed"`
    - `score = 92`
  - Returns the updated state.

This mimics a **real scanner** without performing any actual security testing.

---

## 4. Docker (backend only)

- `backend/Dockerfile`
  - Based on `python:3.12-slim`.
  - Copies `requirements.txt`, installs dependencies.
  - Copies the rest of the backend code.
  - Exposes port `8000` and runs:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

Build and run commands:

```bash
cd backend
docker build -t sentinel-backend .
docker run -p 8000:8000 sentinel-backend
```

The frontend still runs with `npm run dev` from `secureway/` and talks to `http://localhost:8000`.

---

## 5. How to run locally (without Docker)

1. **Backend – FastAPI**

   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

   - API docs: http://localhost:8000/docs

2. **Frontend – Next.js**

   ```bash
   cd secureway
   npm install   # first time only
   npm run dev
   ```

   - UI: http://localhost:3000

3. **Demo flow**

   - Open the UI, click **Start Scan** in the hero.
   - The dashboard will:
     - Show `Simulated Attack In Progress`.
     - Call the FastAPI backend.
     - Update the security score and status.
   - Use the copilot chat panel to ask about BOLA, risk score, or how the system works.

---

## 6. Next steps / possible extensions

- Split `page.tsx` into smaller components under `src/components/` for each major section.
- Add more real-time polling of `/scan/status/{id}` instead of a single call.
- Integrate a real LLM endpoint for the copilot (Gemini, etc.) – **remember to keep API keys out of the repo**.
- Add a `/dashboard` route focused purely on the SaaS-style scan view.
