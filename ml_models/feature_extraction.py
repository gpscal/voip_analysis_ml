import numpy as np
import logging

logger = logging.getLogger(__name__)

def extract_features(voip_data):
    """Extract features from VoIP data for machine learning."""
    features = []
    for call in voip_data:
        duration = call['end_time'] - call['start_time']
        packet_count = len(call['packets'])
        jitter = np.std([pkt['jitter'] for pkt in call['packets']])
        features.append([duration, packet_count, jitter])
    logger.info(f"Extracted features for {len(voip_data)} calls")
    return np.array(features)
