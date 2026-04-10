import logging
from typing import List

try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

if TORCH_AVAILABLE:
    from app.ai.models import AnomalyDetectorLSTM
else:
    AnomalyDetectorLSTM = None

class SystemOracle:
    """
    Failure Prediction (The Oracle)
    Repurposes the Abuse Detection data source. Tracks massive spikes in scan requests
    to automatically scale resources or rate-limit the pipeline before a Playwright crash occurs.
    """
    def __init__(self, threshold=0.85):
        self.real_mode = False
        if TORCH_AVAILABLE:
            try:
                self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                self.model = AnomalyDetectorLSTM().to(self.device)
                self.model.eval()
                self.real_mode = True
            except Exception as e:
                logger.error(f"Failed to initialize Oracle model: {e}")
        
        self.threshold = threshold
        
    def predict_overload(self, concurrent_requests_history: List[int]) -> dict:
        """
        Uses historical data (e.g. from the last 10 minutes of Abuse logs)
        to predict an impending overload condition.
        Returns:
            boolean should_throttle: True if a predicted crash probability > threshold
        """
        if len(concurrent_requests_history) == 0:
            return {"should_throttle": False, "probability": 0.0}
            
        should_throttle = False
        prob = 0.0
        
        if self.real_mode:
            # Pad or truncate sequence for inference
            max_seq_len = 60 # minutes or ticks
            padded_history = concurrent_requests_history[-max_seq_len:]
            if len(padded_history) < max_seq_len:
                padded_history = [0] * (max_seq_len - len(padded_history)) + padded_history
                
            # Convert to tensor shaped (1, SeqLength, Features)
            tensor_data = torch.tensor(padded_history, dtype=torch.float32).unsqueeze(0).unsqueeze(-1).to(self.device)
            
            try:
                with torch.no_grad():
                    prob = self.model(tensor_data).item()
            except Exception as e:
                logger.error(f"Oracle model inference failed: {e}")
                # Fallback heuristic prediction if model fails
                prob = min(sum(concurrent_requests_history[-10:]) / 500.0, 1.0)
        else:
            # Fully Heuristic Fallback Mode
            prob = min(sum(concurrent_requests_history[-10:]) / 500.0, 1.0)

        should_throttle = prob > self.threshold
        
        if should_throttle:
           logger.warning(f"ORACLE PREDICTION: System overload probability {prob:.2f}. Scaling required.")
           
        return {
            "should_throttle": should_throttle,
            "probability": prob,
            "action": "RATE_LIMIT" if should_throttle else "NORMAL"
        }

if __name__ == '__main__':
    oracle = SystemOracle(threshold=0.8)
    res = oracle.predict_overload([10, 12, 50, 80, 150, 400, 480, 520, 600, 650])
    print(res)
