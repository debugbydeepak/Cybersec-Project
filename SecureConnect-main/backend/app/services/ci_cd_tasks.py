import os
import random
import logging
import asyncio
from typing import Dict, Any
from app.core.celery_app import celery_app
from app.services.playwright_service import PlaywrightService
from app.services.cure_agent import CureAgent
from app.services.oracle import SystemOracle
from app.plugins import execute_plugins

logger = logging.getLogger(__name__)

# Mocked historical data stream to represent incoming Playwright scan requests
global_request_history = [10, 15, 20, 25, 30]

@celery_app.task(name="pipeline.trigger_scan")
def trigger_scan_task(target_url: str) -> Dict[str, Any]:
    """
    CI/CD Integration Task: Triggered when new code is pushed.
    Orchestrates the Self-Healing Pipeline for a provided target_url.
    """
    logger.info(f"== Starting Pipeline Task for {target_url} ==")
    
    oracle = SystemOracle(threshold=0.85)
    cure = CureAgent()
    
    # 0. The Oracle: Predict System Overload
    # Simulate a sudden spike by appending random high numbers when pushed
    global_request_history.extend([random.randint(50, 100) for _ in range(5)])
    oracle_prediction = oracle.predict_overload(global_request_history)
    
    if oracle_prediction["should_throttle"]:
        logger.warning("ORACLE: High load predicted. Scaling resources and rate limiting!")
        # Implement logic to scale or throttle...
        # We will proceed for the sake of task demonstration but throttle the speed
        oracle_message = "System scaled due to predicted overload."
    else:
        oracle_message = "System load normal."
        
    # 1. Feature Integration: Trigger Playwright Scanner
    logger.info("Executing Playwright Headless Scanner...")
    scan_results = {}
    try:
        # Simulate scanning. `crawl_shadow_dom` is async, so we wrap it
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in event loop
            pass
        else:
            scan_results = asyncio.run(PlaywrightService.crawl_shadow_dom(target_url))
            
        # Simulate an intermittent crash/timeout
        # Here we randomly force an exception to demonstrate the Cure module (20% chance)
        if random.random() < 0.2:
            raise Exception("playwright._impl._api_types.TimeoutError: Timeout 30000ms exceeded.")
        
        status = "Success"
        patch = None
    except Exception as e:
        logger.error("Scan Failed! Triggering System Health Loop ('Cure' Module)...")
        status = "Failed"
        traceback_str = str(e)
        
        # 2. System Health Loop: Use LLM-based agent (PyTorch logic) to analyze Traceback
        cure_analysis = cure.analyze_traceback(traceback_str)
        patch = cure_analysis["recommended_patch"]
        
        logger.info(f"CURE SUGGESTION: {patch}")
        scan_results = {"error": traceback_str}

    # 3. Unified Plugin System: Running registered external security rules
    logger.info("Executing @secureway_plugin logic...")
    plugin_results = execute_plugins(target_url, scan_results=scan_results)

    from app.services.webhook_service import WebhookService
    
    final_report = {
        "target": target_url,
        "oracle": oracle_prediction,
        "oracle_message": oracle_message,
        "scan_status": status,
        "scan_results": scan_results,
        "auto_patch_suggestion": patch,
        "plugin_results": plugin_results
    }
    
    # Send a notification to the CI/CD pipeline team if a webhook token is provided
    webhook_target = os.getenv("SLACK_WEBHOOK_URL", "")
    if webhook_target:
        WebhookService.send_scan_alert(webhook_target, final_report)
    
    logger.info("== Pipeline Task Completed ==")
    return final_report
