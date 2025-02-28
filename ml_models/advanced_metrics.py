import numpy as np
from scipy import stats
from collections import defaultdict

class AdvancedVoIPMetrics:
    def __init__(self):
        self.metrics = {}
    
    def calculate_mos(self, latency, jitter, packet_loss):
        """
        Calculate Mean Opinion Score (MOS) using E-model
        Returns value between 1-5 (1=bad, 5=excellent)
        """
        R = 93.2 - (0.024 * latency) - (0.11 * jitter) - (30 * np.log(1 + 15 * packet_loss))
        mos = 1 + (0.035 * R) + (R * (R - 60) * (100 - R) * 7e-6)
        return min(max(1, mos), 5)

    def analyze_call_flow(self, packets):
        """Analyze call flow patterns and detect anomalies"""
        flow_metrics = {
            'setup_time': 0,
            'teardown_time': 0,
            'rtp_streams': defaultdict(list),
            'packet_loss_windows': [],
            'burst_periods': []
        }
        
        # Track SIP transactions
        sip_transactions = {}
        current_window_packets = []
        window_size = 50  # packets
        
        for i, (proto, pkt) in enumerate(packets):
            if proto == 'SIP':
                if hasattr(pkt, 'Raw') and hasattr(pkt.Raw, 'load'):
                    if b'INVITE' in pkt.Raw.load:
                        flow_metrics['setup_time'] = float(pkt.time)
                    elif b'BYE' in pkt.Raw.load:
                        flow_metrics['teardown_time'] = float(pkt.time)
            
            elif proto == 'RTP':
                if hasattr(pkt, 'Raw') and hasattr(pkt.Raw, 'load') and len(pkt.Raw.load) >= 12:
                    # Track RTP streams by SSRC
                    ssrc = int.from_bytes(pkt.Raw.load[8:12], byteorder='big')
                    flow_metrics['rtp_streams'][ssrc].append(float(pkt.time))
                    
                    # Sliding window packet loss analysis
                    current_window_packets.append(pkt)
                    if len(current_window_packets) >= window_size:
                        loss_rate = self._calculate_window_loss(current_window_packets)
                        flow_metrics['packet_loss_windows'].append(loss_rate)
                        current_window_packets = current_window_packets[1:]
        
        return flow_metrics

    def _calculate_window_loss(self, window_packets):
        """Calculate packet loss rate in a window"""
        try:
            sequence_numbers = []
            for p in window_packets:
                if hasattr(p, 'Raw') and hasattr(p.Raw, 'load') and len(p.Raw.load) >= 4:
                    seq = int.from_bytes(p.Raw.load[2:4], byteorder='big')
                    sequence_numbers.append(seq)
            
            if sequence_numbers:
                expected = max(sequence_numbers) - min(sequence_numbers) + 1
                received = len(sequence_numbers)
                return (expected - received) / expected if expected > 0 else 0
            return 0
        except Exception:
            return 0

    def detect_anomalies(self, flow_metrics):
        """Detect anomalies in call flow"""
        anomalies = []
        
        # Check setup time
        if flow_metrics['setup_time'] > 1.0:  # More than 1 second
            anomalies.append('Long call setup time')
        
        # Analyze RTP stream consistency
        for ssrc, timestamps in flow_metrics['rtp_streams'].items():
            intervals = np.diff(timestamps)
            if len(intervals) > 0 and np.std(intervals) > 0.05:  # High jitter
                anomalies.append(f'High jitter in RTP stream {ssrc}')
        
        # Check packet loss patterns
        if any(loss > 0.05 for loss in flow_metrics['packet_loss_windows']):
            anomalies.append('Significant packet loss detected')
        
        return anomalies

    def generate_qos_report(self, call_data, flow_metrics):
        """Generate comprehensive QoS report"""
        report = {
            'call_duration': call_data['duration'],
            'packet_stats': {
                'total': call_data['packet_count'],
                'sip': call_data['sip_count'],
                'rtp': call_data['rtp_count']
            },
            'quality_metrics': {
                'jitter': call_data['jitter'],
                'packet_loss_rate': np.mean(flow_metrics['packet_loss_windows']) if flow_metrics['packet_loss_windows'] else 0,
                'setup_time': flow_metrics['setup_time'],
                'rtp_stream_count': len(flow_metrics['rtp_streams'])
            },
            'anomalies': self.detect_anomalies(flow_metrics)
        }
        
        # Calculate MOS
        avg_latency = 0  # Would need to be calculated from RTP timestamps
        report['quality_metrics']['mos'] = self.calculate_mos(
            avg_latency,
            report['quality_metrics']['jitter'],
            report['quality_metrics']['packet_loss_rate']
        )
        
        return report
