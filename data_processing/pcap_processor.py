import logging
from scapy.all import rdpcap, UDP, Raw
from scapy.layers.inet import IP
import re

logger = logging.getLogger(__name__)

def extract_packets(pcap_file):
    """Extract packets from a PCAP file using Scapy."""
    try:
        packets = rdpcap(pcap_file)
        logger.info(f"Extracted {len(packets)} packets from {pcap_file}")
        return packets
    except Exception as e:
        logger.error(f"Error reading PCAP file: {e}")
        raise

def is_sip_packet(packet):
    """Check if a packet is a SIP packet."""
    if UDP in packet and Raw in packet:
        payload = str(packet[Raw].load)
        return any(method in payload for method in [
            'INVITE', 'ACK', 'BYE', 'CANCEL', 'OPTIONS', 'REGISTER',
            'PRACK', 'SUBSCRIBE', 'NOTIFY', 'PUBLISH', 'INFO', 'REFER',
            'MESSAGE', 'UPDATE'
        ]) or 'SIP/2.0' in payload
    return False

def is_rtp_packet(packet):
    """Check if a packet is an RTP packet."""
    if UDP in packet:
        # RTP typically uses even port numbers
        dst_port = packet[UDP].dport
        src_port = packet[UDP].sport
        
        # Check if either port is in the typical RTP range (10000-20000) and is even
        is_rtp_port = lambda p: 10000 <= p <= 20000 and p % 2 == 0
        
        if (is_rtp_port(dst_port) or is_rtp_port(src_port)) and Raw in packet:
            # Check RTP header pattern (first two bytes)
            raw_data = packet[Raw].load
            if len(raw_data) >= 12:  # Minimum RTP header size
                version = (raw_data[0] >> 6) & 0x03  # Extract version from first 2 bits
                return version == 2  # RTP version should be 2
    return False

def filter_voip_packets(packets):
    """Filter VoIP-related packets (SIP and RTP) from the packet list."""
    voip_packets = []
    
    for pkt in packets:
        if IP in pkt:  # Only process IP packets
            if is_sip_packet(pkt):
                voip_packets.append(('SIP', pkt))
            elif is_rtp_packet(pkt):
                voip_packets.append(('RTP', pkt))
    
    sip_count = sum(1 for p in voip_packets if p[0] == 'SIP')
    rtp_count = sum(1 for p in voip_packets if p[0] == 'RTP')
    
    logger.info(f"Filtered {len(voip_packets)} VoIP packets (SIP: {sip_count}, RTP: {rtp_count})")
    return voip_packets
