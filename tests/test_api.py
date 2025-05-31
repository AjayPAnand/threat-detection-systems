import unittest
import json
from app.main import create_app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('requests_total', data)
        self.assertIn('threats_detected', data)
    
    def test_analyze_endpoint(self):
        """Test threat analysis endpoint"""
        test_data = {
            'packet_size': 1024,
            'port': 80,
            'protocol': 'TCP',
            'frequency': 10,
            'duration': 0.5
        }
        
        response = self.client.post('/api/analyze',
                                   data=json.dumps(test_data),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('analysis', data)
    
    def test_analyze_endpoint_missing_data(self):
        """Test analysis endpoint with missing data"""
        response = self.client.post('/api/analyze',
                                   data=json.dumps({}),
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'operational')

if __name__ == '__main__':
    unittest.main()
