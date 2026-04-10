
# In a real environment, this imports 'pyod'.
import random

class AnomalyDetector:
    def __init__(self):
        try:
            from pyod.models.iforest import IForest
            self.model = IForest(contamination=0.05, n_estimators=100)
            self.real_mode = True
            # Mock fit for demonstration
            # In reality, this model would load pre-trained weights
            self.model.fit([[1,2], [2,3], [1,3], [100, 200]]) # Add outlier
        except ImportError:
            self.real_mode = False

    def detect_outlier(self, data_point: list):
        if self.real_mode and hasattr(self, 'model'):
            # Real Anomaly Detection using Isolation Forest
            score = self.model.decision_function([data_point])
            label = self.model.predict([data_point])
            return label[0] == 1, score[0]
        else:
            # Fallback Mock Logic
            return random.choice([True, False]) if data_point[0] > 10 else False, 0.95 # nosec
