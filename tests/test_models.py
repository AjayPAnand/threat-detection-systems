import unittest
import numpy as np
from app.models.threat_detector import ThreatDetector

class TestThreatDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ThreatDetector()
    
    def test_extract_features(self):
        """Test feature extraction"""
        test_data = {
            'packet_size': 1024,
            'frequency': 50,
            'port': 80,
            'protocol': 'TCP',
            'duration': 0.5
        }
        
        features = self.detector.extract_features(test_data)
        self.assertEqual(features.shape, (1, 5))
        self.assertIsInstance(features, np.ndarray)
    
    def test_simple_threat_detection(self):
        """Test simple threat detection logic"""
        # Test suspicious port
        suspicious_data = {
            'port': 1433,
            'packet_size': 512,
            'frequency': 10
        }
        
        result = self.detector._simple_threat_detection(suspicious_data)
        self.assertTrue(result['is_threat'])
        self.assertEqual(result['threat_level'], 'high')
    
    def test_normal_traffic_detection(self):
        """Test normal traffic detection"""
        normal_data = {
            'port': 80,
            'packet_size': 512,
            'frequency': 10
        }
        
        result = self.detector._simple_threat_detection(normal_data)
        self.assertFalse(result['is_threat'])
    
    def test_protocol_encoding(self):
        """Test protocol encoding"""
        self.assertEqual(self.detector._encode_protocol('TCP'), 1)
        self.assertEqual(self.detector._encode_protocol('UDP'), 2)
        self.assertEqual(self.detector._encode_protocol('UNKNOWN'), 0)
    
    def test_threat_level_calculation(self):
        """Test threat level calculation"""
        self.assertEqual(self.detector._calculate_threat_level(0.8), 'high')
        self.assertEqual(self.detector._calculate_threat_level(0.5), 'medium')
        self.assertEqual(self.detector._calculate_threat_level(0.2), 'low')

if __name__ == '__main__':
    unittest.main()
