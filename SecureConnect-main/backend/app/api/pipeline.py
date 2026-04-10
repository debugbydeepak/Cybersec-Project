from fastapi import APIRouter, BackgroundTasks, HTTPException, Security
from typing import Optional
from app.services.ci_cd_tasks import trigger_scan_task
from app.services.example_plugins import * # ensure plugins get registered

router = APIRouter()

from fastapi.security.api_key import APIKeyHeader
from app.api.auth import get_api_keys_db

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header:
        # Fallback for hackathon testing without headers if needed, 
        # or require it strictly.
        pass
    else:
        keys_db = get_api_keys_db()
        if api_key_header not in keys_db or not keys_db[api_key_header].get("active"):
            raise HTTPException(status_code=403, detail="Could not validate API Key")
    return api_key_header
    
@router.post("/trigger-scan")
async def trigger_cicd_pipeline(target_url: str, api_key: str = Security(verify_api_key)):
    """
    Feature Integration: Automatically triggers the Playwright scanner 
    when invoked (e.g. by a CI/CD pushed commit or webhook).
    """
    if not target_url:
        raise HTTPException(status_code=400, detail="target_url is required")
        
    # Triggering Celery task
    task = trigger_scan_task.delay(target_url)
    
    return {
        "status": "Pipeline Triggered Successfully",
        "task_id": task.id,
        "message": f"Self-Healing CI/CD workflow started for {target_url}. Plugins loaded."
    }

@router.get("/status/{task_id}")
async def get_pipeline_status(task_id: str):
    """
    Gets the completion status and report of a pipeline task.
    """
    from app.core.celery_app import celery_app
    task_result = celery_app.AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        return {"status": task_result.state, "info": "Task is waiting or running."}
    elif task_result.state != 'FAILURE':
        return {"status": task_result.state, "report": task_result.info}
    else:
        return {"status": task_result.state, "info": str(task_result.info)}
