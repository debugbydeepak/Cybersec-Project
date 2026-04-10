import os
from typing import Any, Dict

import requests


class McpKaliService:
    """Client for the Docker-based MCP Kali server."""

    def __init__(self) -> None:
        self.base_url = os.getenv("MCP_KALI_URL", "http://localhost:9000")

    def port_scan(self, target: str, fast: bool = True) -> Dict[str, Any]:
        try:
            resp = requests.post(
                f"{self.base_url}/tools/port_scan",
                json={"target": target, "fast": fast},
                timeout=70,
            )
        except requests.RequestException as exc:
            return {
                "ok": False,
                "error_type": "network",
                "message": str(exc),
                "suggestion": "Ensure the secureway-mcp-kali Docker container is running and MCP_KALI_URL is reachable.",
            }

        if resp.status_code != 200:
            data = {}
            try:
                data = resp.json()
            except Exception:
                pass # nosec
            detail = data.get("detail") if isinstance(data, dict) else None
            return {
                "ok": False,
                "error_type": "remote",
                "status_code": resp.status_code,
                "message": detail or "Kali MCP server returned an error.",
                "suggestion": "Check target domain/IP and server logs inside the Kali container.",
            }

        try:
            data = resp.json()
        except Exception as exc:
            return {
                "ok": False,
                "error_type": "parse",
                "message": f"Failed to parse MCP response: {exc}",
                "suggestion": "Inspect the raw output from the Kali MCP server.",
            }

        return {"ok": True, "data": data}
