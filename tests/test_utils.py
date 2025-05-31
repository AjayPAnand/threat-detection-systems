import unittest
from app.utils.data_processor import NetworkDataProcessor

class TestNetworkDataProcessor(unittest.TestCase):
    def test_validate_ip_address(self):
        """Test IP address validation"""
        self.assertTrue(NetworkDataProcessor.validate_ip_address('192.168.1.1'))
        self.assertTrue(NetworkDataProcessor.validate_ip_address('10.0.0.1'))
        self.assertFalse(NetworkDataProcessor.validate_ip_address('256.1.1.1'))
        self.assertFalse(NetworkDataProcessor.validate_ip_address('invalid'))
    
    def test_validate_port(self):
        """Test port validation"""
        self.assertTrue(NetworkDataProcessor.validate_port(80))
        self.assertTrue(NetworkDataProcessor.validate_port('443'))
        self.assertFalse(NetworkDataProcessor.validate_port(0))
        self.assertFalse(NetworkDataProcessor.validate_port(70000))
        self.assertFalse(NetworkDataProcessor.validate_port('invalid'))
    
    def test_normalize_protocol(self):
        """Test protocol normalization"""
        self.assertEqual(NetworkDataProcessor.normalize_protocol('tcp'), 'TCP')
        self.assertEqual(NetworkDataProcessor.normalize_protocol(' HTTP '), 'HTTP')
        self.assertEqual(NetworkDataProcessor.normalize_protocol(''), 'UNKNOWN')
        self.assertEqual(NetworkDataProcessor.normalize_protocol(None), 'UNKNOWN')
    
    def test_process_network_log(self):
        """Test network log processing"""
        log_data = {
            'source_ip': '192.168.1.1',
            'destination_ip': '10.0.0.1',
            'port': '80',
            'protocol': 'tcp',
            'packet_size': '1024',
            'frequency': '5'
        }
        
        processed = NetworkDataProcessor.process_network_log(log_data)
        
        self.assertEqual(processed['port'], 80)
        self.assertEqual(processed['protocol'], 'TCP')
        self.assertEqual(processed['packet_size'], 1024)
    
    def test_generate_sample_data(self):
        """Test sample data generation"""
        sample_data = NetworkDataProcessor.generate_sample_data(10)
        self.assertEqual(len(sample_data), 10)
        
        for data in sample_data:
            self.assertIn('source_ip', data)
            self.assertIn('port', data)
            self.assertIn('protocol', data)

if __name__ == '__main__':
    unittest.main()
