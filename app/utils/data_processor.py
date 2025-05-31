import pandas as pd
import numpy as np
from datetime import datetime
import re

class NetworkDataProcessor:
    """Process and validate network traffic data"""
    
    @staticmethod
    def validate_ip_address(ip):
        """Validate IP address format"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return re.match(pattern, ip) is not None
    
    @staticmethod
    def validate_port(port):
        """Validate port number"""
        try:
            port_num = int(port)
            return 1 <= port_num <= 65535
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def normalize_protocol(protocol):
        """Normalize protocol names"""
        if not protocol:
            return 'UNKNOWN'
        return protocol.upper().strip()
    
    @staticmethod
    def process_network_log(log_data):
        """Process raw network log data"""
        processed_data = {
            'timestamp': log_data.get('timestamp', datetime.now().isoformat()),
            'source_ip': log_data.get('source_ip', '0.0.0.0'),
            'destination_ip': log_data.get('destination_ip', '0.0.0.0'),
            'port': int(log_data.get('port', 80)),
            'protocol': NetworkDataProcessor.normalize_protocol(log_data.get('protocol')),
            'packet_size': int(log_data.get('packet_size', 0)),
            'frequency': int(log_data.get('frequency', 1)),
            'duration': float(log_data.get('duration', 0.0))
        }
        
        return processed_data
    
    @staticmethod
    def generate_sample_data(num_samples=100):
        """Generate sample network data for testing"""
        np.random.seed(42)
        
        protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'ICMP']
        ports = [80, 443, 22, 23, 53, 135, 139, 445, 1433, 3389]
        
        sample_data = []
        for _ in range(num_samples):
            data = {
                'source_ip': f"192.168.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
                'destination_ip': f"10.0.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}",
                'port': np.random.choice(ports),
                'protocol': np.random.choice(protocols),
                'packet_size': np.random.normal(512, 200),
                'frequency': np.random.poisson(10),
                'duration': np.random.exponential(0.5)
            }
            sample_data.append(NetworkDataProcessor.process_network_log(data))
        
        return sample_data
