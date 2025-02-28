import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from ml_models.feature_extraction import extract_features
from ml_models.model import VoIPQualityModel
from data_processing.pcap_processor import extract_packets, filter_voip_packets
from utils.config import Config
import logging
import os
import glob
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.all import Raw

logger = logging.getLogger(__name__)

def get_packet_time(packet_tuple):
    """Extract time from a packet tuple."""
    _, packet = packet_tuple
    return float(packet.time)

def get_packet_size(packet_tuple):
    """Extract size from a packet tuple."""
    _, packet = packet_tuple
    return len(packet)

def get_packet_protocol(packet_tuple):
    """Get the protocol type from a packet tuple."""
    protocol, _ = packet_tuple
    return protocol

def calculate_jitter(packet_times):
    """Calculate jitter from a list of packet times."""
    if len(packet_times) < 2:
        return 0
    
    differences = np.diff(packet_times)
    return np.std(differences)

def process_voip_calls(voip_packets):
    """
    Group VoIP packets into calls and extract relevant metrics.
    """
    # Group packets by call ID (based on SIP dialog)
    calls = {}
    current_call = None
    
    # Sort packets by time
    sorted_packets = sorted(voip_packets, key=get_packet_time)
    
    for packet_tuple in sorted_packets:
        protocol = get_packet_protocol(packet_tuple)
        packet = packet_tuple[1]
        
        if protocol == 'SIP':
            # Check for SIP INVITE (new call)
            if Raw in packet and b'INVITE' in packet[Raw].load:
                call_id = extract_call_id(packet)
                if call_id not in calls:
                    calls[call_id] = {
                        'start_time': get_packet_time(packet_tuple),
                        'packets': [],
                        'sip_packets': [],
                        'rtp_packets': []
                    }
                current_call = call_id
            
            # Check for SIP BYE (end call)
            elif Raw in packet and b'BYE' in packet[Raw].load and current_call:
                if current_call in calls:
                    calls[current_call]['end_time'] = get_packet_time(packet_tuple)
        
        # Store packet in appropriate call
        if current_call and current_call in calls:
            calls[current_call]['packets'].append({
                'time': get_packet_time(packet_tuple),
                'size': get_packet_size(packet_tuple),
                'protocol': protocol
            })
            
            if protocol == 'SIP':
                calls[current_call]['sip_packets'].append(packet_tuple)
            elif protocol == 'RTP':
                calls[current_call]['rtp_packets'].append(packet_tuple)

    # Process each call to extract metrics
    processed_calls = []
    for call_id, call_data in calls.items():
        if 'end_time' in call_data:  # Only process completed calls
            packet_times = [p['time'] for p in call_data['packets']]
            
            processed_call = {
                'start_time': call_data['start_time'],
                'end_time': call_data['end_time'],
                'duration': call_data['end_time'] - call_data['start_time'],
                'packet_count': len(call_data['packets']),
                'sip_count': len(call_data['sip_packets']),
                'rtp_count': len(call_data['rtp_packets']),
                'jitter': calculate_jitter(packet_times)
            }
            processed_calls.append(processed_call)
    
    logger.info(f"Processed {len(processed_calls)} complete VoIP calls")
    return processed_calls

def extract_call_id(packet):
    """Extract Call-ID from SIP packet."""
    if Raw in packet:
        payload = packet[Raw].load.decode('utf-8', errors='ignore')
        for line in payload.split('\r\n'):
            if line.startswith('Call-ID:'):
                return line.split(':', 1)[1].strip()
    return str(hash(str(packet)))  # Fallback to packet hash if Call-ID not found

def determine_call_quality(call):
    """
    Determine call quality based on metrics.
    Returns 0 for poor quality, 1 for good quality.
    """
    # Thresholds for good quality
    MIN_DURATION = 5  # seconds
    MAX_JITTER = 50  # milliseconds
    MIN_RTP_PACKETS = 50
    
    if (call['duration'] >= MIN_DURATION and
        call['jitter'] <= MAX_JITTER and
        call['rtp_count'] >= MIN_RTP_PACKETS):
        return 1  # Good quality
    return 0  # Poor quality

def load_data(pcap_directory):
    """Load and preprocess PCAP files for training."""
    voip_data = []
    labels = []
    
    pcap_files = glob.glob(os.path.join(pcap_directory, "*.pcap"))
    
    for pcap_file in pcap_files:
        try:
            logger.info(f"Processing {pcap_file}")
            packets = extract_packets(pcap_file)
            voip_packets = filter_voip_packets(packets)
            
            if not voip_packets:
                logger.warning(f"No VoIP packets found in {pcap_file}")
                continue
            
            # Process calls and extract features
            calls = process_voip_calls(voip_packets)
            
            for call in calls:
                voip_data.append(call)
                quality_label = determine_call_quality(call)
                labels.append(quality_label)
                
        except Exception as e:
            logger.error(f"Error processing {pcap_file}: {e}")
            continue
    
    return voip_data, labels

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create model directory if it doesn't exist
    os.makedirs(os.path.dirname(Config.MODEL_PATH), exist_ok=True)
    
    logger.info("Loading training data...")
    voip_data, labels = load_data(Config.DATA_DIR)
    
    if not voip_data:
        logger.error("No training data found!")
        return
    
    logger.info(f"Loaded {len(voip_data)} calls for training")
    
    # Extract features
    logger.info("Extracting features...")
    X = extract_features(voip_data)
    y = np.array(labels)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train and evaluate the model
    logger.info("Training model...")
    model = VoIPQualityModel()
    model.train(X_train, y_train)
    
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    logger.info(f"Model accuracy: {accuracy:.2f}")
    logger.info("\nClassification Report:")
    logger.info(classification_report(y_test, predictions))
    
    # Save the model
    logger.info(f"Saving model to {Config.MODEL_PATH}")
    model.save_model(Config.MODEL_PATH)
    logger.info("Training completed successfully!")

if __name__ == "__main__":
    main()
