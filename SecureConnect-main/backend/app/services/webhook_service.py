import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebhookService:
    """
    Handles sending automated notifications to team collaboration tools (Slack/Discord/Teams)
    or custom CI/CD Webhooks upon completion of a pipeline security scan.
    """
    
    @staticmethod
    def send_scan_alert(webhook_url: str, report: Dict[str, Any]):
        """
        Sends the scan report summary to the specified webhook.
        """
        if not webhook_url:
            logger.warning("No webhook URL provided. Skipping notification.")
            return False
            
        target = report.get("target", "Unknown Target")
        status = report.get("scan_status", "Failed")
        oracle_message = report.get("oracle_message", "N/A")
        auto_patch = report.get("auto_patch_suggestion")
        
        # Build a generic markdown payload compatible with most incoming webhooks (Slack/Discord)
        message = (
            f"🚀 **SECUREWAY Scan Completed** 🚀\n"
            f"**Target:** {target}\n"
            f"**Status:** {status}\n"
            f"**Oracle System Status:** {oracle_message}\n"
        )
        
        if auto_patch:
            message += f"**Cure Agent Auto-Fix Recommendation:**\n```\n{auto_patch}\n```"

        payload = {
            "text": message
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Successfully dispatched webhook alert to {webhook_url}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send webhook alert: {e}")
            return False
