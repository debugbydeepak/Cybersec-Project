import torch
import torch.nn as nn
import logging

logger = logging.getLogger(__name__)

class SimpleTracebackEncoder(nn.Module):
    """
    Core Model for The Cure Agent.
    Encodes traceback signatures to predict the architectural fix category.
    """
    def __init__(self, vocab_size=1000, hidden_dim=128, num_classes=3):
        super(SimpleTracebackEncoder, self).__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_dim)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)
        
    def forward(self, x):
        embedded = self.embedding(x)
        out, (hn, _) = self.lstm(embedded)
        return self.fc(hn[-1])

class AnomalyDetectorLSTM(nn.Module):
    """
    Core Model for The Oracle.
    Models the sequence of incoming scanner requests to predict sudden system overloads.
    """
    def __init__(self, input_dim=1, hidden_dim=64, num_layers=2):
        super(AnomalyDetectorLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

def save_model(model: nn.Module, path: str):
    torch.save(model.state_dict(), path)
    logger.info(f"Model saved to {path}")

def load_model(model: nn.Module, path: str):
    try:
        model.load_state_dict(torch.load(path))
        model.eval()
        logger.info(f"Model loaded from {path}")
    except FileNotFoundError:
        logger.warning(f"Weights file {path} not found. Running with uninitialized weights.")
    return model
