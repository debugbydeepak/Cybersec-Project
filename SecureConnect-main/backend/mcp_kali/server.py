import subprocess
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SecureWay MCP Kali Server")


class PortScanRequest(BaseModel):
    target: str
    fast: bool = True


@app.get("/")
async def root():
    return {"service": "secureway-mcp-kali", "status": "ok"}


@app.post("/tools/port_scan")
async def port_scan(req: PortScanRequest):
    target = req.target.strip()
    if not target:
        raise HTTPException(status_code=400, detail="Target is required")

    # Basic safety: avoid obviously bad targets
    if target in {"127.0.0.1", "localhost"}:
        raise HTTPException(status_code=400, detail="Localhost scanning is disabled in this demo server")

    cmd = ["nmap"]
    if req.fast:
        cmd.append("-F")
    cmd.append(target)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Port scan timed out")

    output = result.stdout or result.stderr or "(no output)"

    return {
        "target": target,
        "command": " ".join(cmd),
        "exit_code": result.returncode,
        "output": output,
    }
