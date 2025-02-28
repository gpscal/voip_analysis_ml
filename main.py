import sys
import os
from pathlib import Path
import numpy as np
from data_processing.pcap_processor import extract_packets, filter_voip_packets
from ml_models.feature_extraction import extract_features
from ml_models.model import VoIPQualityModel
from ml_models.advanced_metrics import AdvancedVoIPMetrics
from ml_models.traffic_analyzer import VoIPTrafficAnalyzer
from utils.logger import setup_logger
from utils.config import Config

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

def process_voip_call(voip_packets):
    """Process VoIP packets and extract call metrics."""
    if not voip_packets:
        return None

    # Sort packets by time
    sorted_packets = sorted(voip_packets, key=get_packet_time)
    
    # Get start and end times
    start_time = get_packet_time(sorted_packets[0])
    end_time = get_packet_time(sorted_packets[-1])
    
    # Count packets by protocol
    sip_packets = [p for p in sorted_packets if get_packet_protocol(p) == 'SIP']
    rtp_packets = [p for p in sorted_packets if get_packet_protocol(p) == 'RTP']
    
    # Calculate jitter
    packet_times = [get_packet_time(p) for p in sorted_packets]
    jitter = np.std(np.diff(packet_times)) if len(packet_times) > 1 else 0

    # Create call data structure
    call_data = {
        'start_time': start_time,
        'end_time': end_time,
        'duration': end_time - start_time,
        'packet_count': len(voip_packets),
        'sip_count': len(sip_packets),
        'rtp_count': len(rtp_packets),
        'jitter': jitter
    }
    
    return call_data

def main(pcap_file):
    # Set up logging
    logger = setup_logger()

    # Ensure the PCAP file exists
    if not os.path.isfile(pcap_file):
        logger.error(f"PCAP file {pcap_file} does not exist.")
        return

    try:
        # Initialize analyzers
        quality_metrics = AdvancedVoIPMetrics()
        traffic_analyzer = VoIPTrafficAnalyzer()

        # Step 1: Extract packets from the PCAP file
        logger.info("Extracting packets from the PCAP file...")
        packets = extract_packets(pcap_file)

        # Step 2: Filter for VoIP packets
        logger.info("Filtering for VoIP packets...")
        voip_packets = filter_voip_packets(packets)

        if not voip_packets:
            logger.error("No VoIP packets found in the PCAP file.")
            return

        # Step 3: Process VoIP packets into call data
        logger.info("Processing VoIP packets...")
        call_data = process_voip_call(voip_packets)

        if not call_data:
            logger.error("Could not process VoIP call data.")
            return

        # Step 4: Perform advanced analysis
        logger.info("Performing advanced analysis...")
        
        # Extract traffic patterns
        patterns = traffic_analyzer.extract_traffic_patterns(voip_packets)
        traffic_behavior = traffic_analyzer.analyze_traffic_behavior(patterns)
        anomalies = traffic_analyzer.detect_anomalies(patterns)
        
        # Calculate advanced metrics
        flow_metrics = quality_metrics.analyze_call_flow(voip_packets)
        qos_report = quality_metrics.generate_qos_report(call_data, flow_metrics)

        # Step 5: Extract features and predict quality
        logger.info("Extracting features...")
        features = extract_features([call_data])

        # Step 6: Load and use the ML model
        logger.info("Loading the machine learning model...")
        model = VoIPQualityModel()
        model.load_model(Config.MODEL_PATH)
        quality_prediction = model.predict(features)

        # Output comprehensive analysis results
        logger.info("\n=== VoIP Call Analysis Report ===")
        
        logger.info("\nBasic Call Statistics:")
        logger.info(f"Duration: {call_data['duration']:.2f} seconds")
        logger.info(f"Total Packets: {call_data['packet_count']}")
        logger.info(f"SIP/RTP Ratio: {call_data['sip_count']}/{call_data['rtp_count']}")
        
        logger.info("\nQuality Metrics:")
        logger.info(f"MOS Score: {qos_report['quality_metrics']['mos']:.2f}")
        logger.info(f"Jitter: {qos_report['quality_metrics']['jitter']:.2f} ms")
        logger.info(f"Packet Loss Rate: {qos_report['quality_metrics']['packet_loss_rate']*100:.2f}%")
        logger.info(f"Call Setup Time: {qos_report['quality_metrics']['setup_time']:.3f} seconds")
        
        if qos_report['anomalies']:
            logger.info("\nDetected Anomalies:")
            for anomaly in qos_report['anomalies']:
                logger.info(f"- {anomaly}")
        
        logger.info("\nTraffic Pattern Analysis:")
        if traffic_behavior['burst_statistics']:
            logger.info(f"Burst Count: {traffic_behavior['burst_statistics']['count']}")
            logger.info(f"Average Burst Duration: {traffic_behavior['burst_statistics']['avg_duration']:.3f} seconds")
        logger.info(f"Protocol Distribution: {traffic_behavior['protocol_distribution']['protocol_counts']}")
        
        logger.info("\nML Model Prediction:")
        logger.info(f"Predicted Call Quality: {'Good' if quality_prediction[0] == 1 else 'Poor'}")
        
        # Detailed anomaly analysis
        if anomalies:
            logger.info("\nDetailed Anomaly Analysis:")
            for i, anomaly in enumerate(anomalies, 1):
                logger.info(f"\nAnomaly {i}:")
                logger.info(f"Timestamp: {anomaly['timestamp']:.3f}")
                logger.info(f"Protocol: {anomaly['protocol']}")
                logger.info(f"Packet Size: {anomaly['packet_size']} bytes")
                if anomaly['inter_arrival']:
                    logger.info(f"Inter-arrival Time: {anomaly['inter_arrival']*1000:.2f} ms")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py /path/to/yourfile.pcap")
    else:
        main(sys.argv[1])
