import numpy as np
from sklearn.ensemble import IsolationForest
from collections import defaultdict

class VoIPTrafficAnalyzer:
    def __init__(self):
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
    
    def extract_traffic_patterns(self, packets):
        """Extract traffic patterns from packet sequence"""
        patterns = {
            'time_series': [],
            'packet_sizes': [],
            'inter_arrival_times': [],
            'protocol_sequence': [],
            'burst_patterns': []
        }
        
        last_time = None
        current_burst = []
        burst_threshold = 0.05  # 50ms
        
        for proto, pkt in packets:
            current_time = float(pkt.time)
            packet_size = len(pkt)
            
            patterns['time_series'].append(current_time)
            patterns['packet_sizes'].append(packet_size)
            patterns['protocol_sequence'].append(proto)
            
            if last_time is not None:
                inter_arrival = current_time - last_time
                patterns['inter_arrival_times'].append(inter_arrival)
                
                # Burst detection
                if inter_arrival <= burst_threshold:
                    current_burst.append((current_time, packet_size))
                else:
                    if len(current_burst) > 5:  # Minimum burst size
                        patterns['burst_patterns'].append(current_burst)
                    current_burst = [(current_time, packet_size)]
            
            last_time = current_time
            
        # Handle last burst
        if len(current_burst) > 5:
            patterns['burst_patterns'].append(current_burst)
            
        return patterns
    
    def analyze_traffic_behavior(self, patterns):
        """Analyze traffic behavior and identify patterns"""
        behavior = {
            'burst_statistics': self._analyze_bursts(patterns['burst_patterns']),
            'protocol_distribution': self._analyze_protocol_distribution(patterns['protocol_sequence']),
            'size_distribution': self._analyze_size_distribution(patterns['packet_sizes']),
            'timing_analysis': self._analyze_timing(patterns['inter_arrival_times'])
        }
        return behavior
    
    def _analyze_bursts(self, bursts):
        """Analyze burst patterns"""
        if not bursts:
            return None
            
        burst_stats = {
            'count': len(bursts),
            'avg_duration': np.mean([b[-1][0] - b[0][0] for b in bursts]),
            'avg_size': np.mean([len(b) for b in bursts]),
            'avg_packet_size': np.mean([p[1] for b in bursts for p in b])
        }
        return burst_stats
    
    def _analyze_protocol_distribution(self, protocol_sequence):
        """Analyze protocol distribution and transitions"""
        counts = defaultdict(int)
        transitions = defaultdict(int)
        
        for i, proto in enumerate(protocol_sequence):
            counts[proto] += 1
            if i > 0:
                transition = f"{protocol_sequence[i-1]}->{proto}"
                transitions[transition] += 1
        
        return {
            'protocol_counts': dict(counts),
            'protocol_transitions': dict(transitions)
        }
    
    def _analyze_size_distribution(self, packet_sizes):
        """Analyze packet size distribution"""
        if not packet_sizes:
            return None
            
        return {
            'mean': np.mean(packet_sizes),
            'std': np.std(packet_sizes),
            'percentiles': {
                '25': np.percentile(packet_sizes, 25),
                '50': np.percentile(packet_sizes, 50),
                '75': np.percentile(packet_sizes, 75)
            }
        }
    
    def _analyze_timing(self, inter_arrival_times):
        """Analyze packet timing patterns"""
        if not inter_arrival_times:
            return None
            
        return {
            'mean_inter_arrival': np.mean(inter_arrival_times),
            'jitter': np.std(inter_arrival_times),
            'timing_percentiles': {
                '25': np.percentile(inter_arrival_times, 25),
                '50': np.percentile(inter_arrival_times, 50),
                '75': np.percentile(inter_arrival_times, 75)
            }
        }
    
    def detect_anomalies(self, patterns):
        """Detect anomalies in traffic patterns"""
        # Check if we have enough data
        if (len(patterns['packet_sizes']) < 2 or 
            len(patterns['inter_arrival_times']) < 1 or 
            len(patterns['protocol_sequence']) < 2):
            return []

        # Get the minimum length to ensure all arrays match
        min_length = min(
            len(patterns['packet_sizes']),
            len(patterns['inter_arrival_times']),
            len(patterns['protocol_sequence'])
        )

        # Prepare features for anomaly detection with matching lengths
        features = np.column_stack([
            patterns['packet_sizes'][:min_length],
            patterns['inter_arrival_times'][:min_length],
            [int(p == 'RTP') for p in patterns['protocol_sequence'][:min_length]]
        ])
        
        # Fit and predict anomalies
        predictions = self.anomaly_detector.fit_predict(features)
        anomaly_indices = np.where(predictions == -1)[0]
        
        # Analyze anomalies
        anomalies = []
        for idx in anomaly_indices:
            if idx < min_length:  # Ensure we don't exceed array bounds
                anomaly = {
                    'timestamp': patterns['time_series'][idx],
                    'packet_size': patterns['packet_sizes'][idx],
                    'protocol': patterns['protocol_sequence'][idx],
                    'inter_arrival': patterns['inter_arrival_times'][idx] if idx < len(patterns['inter_arrival_times']) else None
                }
                anomalies.append(anomaly)
        
        return anomalies
