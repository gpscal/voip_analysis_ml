import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from ml_models.feature_extraction.py import extract_features
from ml_models.model import VoIPQualityModel
import logging

logger = logging.getLogger(__name__)

def load_data():
    """Load and preprocess data for training."""
    # Placeholder for data loading logic
    voip_data = []
    labels = []
    return voip_data, labels

def main():
    voip_data, labels = load_data()
    X = extract_features(voip_data)
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = VoIPQualityModel()
    model.train(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    logger.info(f"Model accuracy: {accuracy}")

    model.save_model('voip_quality_model.pkl')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
