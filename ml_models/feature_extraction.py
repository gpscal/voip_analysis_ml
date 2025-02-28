import numpy as np
import logging

logger = logging.getLogger(__name__)

def extract_features(voip_data):
    """
    Extract features from VoIP call data for machine learning.
    
    Features extracted:
    - Call duration (seconds)
    - Total packet count
    - SIP packet count
    - RTP packet count
    - Jitter (ms)
    - Packets per second
    
    Parameters:
    voip_data (list): List of call dictionaries containing metrics
    
    Returns:
    numpy.ndarray: Array of feature vectors
    """
    features = []
    
    for call in voip_data:
        # Extract basic features
        duration = call['duration']
        total_packets = call['packet_count']
        sip_count = call['sip_count']
        rtp_count = call['rtp_count']
        jitter = call['jitter']
        
        # Calculate derived features
        packets_per_second = total_packets / duration if duration > 0 else 0
        
        # Create feature vector
        feature_vector = [
            duration,
            total_packets,
            sip_count,
            rtp_count,
            jitter,
            packets_per_second
        ]
        
        features.append(feature_vector)
    
    features_array = np.array(features)
    logger.info(f"Extracted {len(features)} feature vectors with {features_array.shape[1]} features each")
    
    # Log feature statistics for debugging
    if len(features) > 0:
        logger.debug("Feature statistics:")
        logger.debug(f"Duration (s): mean={np.mean(features_array[:, 0]):.2f}, std={np.std(features_array[:, 0]):.2f}")
        logger.debug(f"Total packets: mean={np.mean(features_array[:, 1]):.2f}, std={np.std(features_array[:, 1]):.2f}")
        logger.debug(f"Jitter (ms): mean={np.mean(features_array[:, 4]):.2f}, std={np.std(features_array[:, 4]):.2f}")
    
    return features_array
