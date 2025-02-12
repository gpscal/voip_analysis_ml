import subprocess
import logging
from scapy.all import rdpcap

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

def filter_voip_packets(packets):
    """Filter VoIP-related packets (e.g., SIP, RTP) from the packet list."""
    voip_packets = [pkt for pkt in packets if 'SIP' in pkt or 'RTP' in pkt]
    logger.info(f"Filtered {len(voip_packets)} VoIP packets")
    return voip_packets
