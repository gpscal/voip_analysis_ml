import subprocess
import logging
from utils.config import Config

logger = logging.getLogger(__name__)

def run_voipshark(pcap_file, output_dir):
    """Run VoIPShark to analyze VoIP traffic in the PCAP file."""
    try:
        cmd = [Config.VOIPSHARK_PATH, '-r', pcap_file, '-o', output_dir]
        subprocess.run(cmd, check=True)
        logger.info(f"VoIPShark analysis completed. Output at {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"VoIPShark analysis failed: {e}")
        raise
