from sklearn.ensemble import RandomForestClassifier
import joblib
import logging

logger = logging.getLogger(__name__)

class VoIPQualityModel:
    def __init__(self):
        self.model = RandomForestClassifier()

    def train(self, X, y):
        self.model.fit(X, y)
        logger.info("Model training completed")

    def predict(self, X):
        predictions = self.model.predict(X)
        logger.info(f"Made predictions for {len(X)} samples")
        return predictions

    def save_model(self, path):
        joblib.dump(self.model, path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path):
        self.model = joblib.load(path)
        logger.info(f"Model loaded from {path}")
