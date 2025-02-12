import os
from data_processing.pcap_processor import extract_packets, filter_voip_packets
from data_processing.xplico_interface import run_xplico
from data_processing.voipshark_interface import run_voipshark
from ml_models.feature_extraction import extract_features
from ml_models.model import VoIPQualityModel
from utils.logger import setup_logger
from utils.config import Config
import logging

setup_logger()
logger = logging.getLogger(__name__)

def main(pcap_file):
    packets = extract_packets(pcap_file)
    voip_packets = filter_voip_packets(packets)

    xplico_output = os.path.join(Config.OUTPUT_DIR, 'xplico')
    run_xplico(pcap_file, xplico_output)


::contentReference[oaicite:0]{index=0}
 
