import subprocess
import logging
from utils.config import Config

logger = logging.getLogger(__name__)

def run_xplico(pcap_file, output_dir):
    """Run Xplico to analyze the PCAP file and extract application data."""
    try:
        cmd = [Config.XPLICO_PATH, '-m', 'r', '-p', pcap_file, '-o', output_dir]
        subprocess.run(cmd, check=True)
        logger.info(f"Xplico analysis completed. Output at {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Xplico analysis failed: {e}")
        raise
