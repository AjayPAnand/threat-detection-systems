import unittest
import json
import requests
import time
from threading import Thread
from app.main import create_app

class TestAPIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start the Flask app for integration testing"""
        cls.app = create_app()
        cls.server_thread = Thread(target=cls.run_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Give the server time to start
    
    @classmethod
    def run_server(cls):
        cls.app.run(port=5001, debug=False, use_reloader=False)
    
    def test_full_threat_analysis_workflow(self):
        """Test complete threat analysis workflow"""
        base_url = 'http://localhost:5001'
        
        # Test health check
        response = requests.get(f'{base_url}/health')
        self.assertEqual(response.status_code, 200)
        
        # Test status
        response = requests.get(f'{base_url}/api/status')
        self.assertEqual(response.status_code, 200)
        
        # Test threat analysis
        threat_data = {
            'packet_size': 2000,
            'port': 1433,  # Suspicious port
            'protocol': 'TCP',
            'frequency': 100
        }
        
        response = requests.post(f'{base_url}/api/analyze',
                               json=threat_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['analysis']['is_threat'])
    
    def test_metrics_collection(self):
        """Test metrics endpoint"""
        base_url = 'http://localhost:5001'
        response = requests.get(f'{base_url}/metrics')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('requests_total', data)

if __name__ == '__main__':
    unittest.main()
