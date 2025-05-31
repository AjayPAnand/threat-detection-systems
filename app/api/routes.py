from flask import Blueprint, request, jsonify
from app.models.threat_detector import ThreatDetector
import logging

api_bp = Blueprint('api', __name__)
threat_detector = ThreatDetector()

@api_bp.route('/analyze', methods=['POST'])
def analyze_traffic():
    """Analyze network traffic for threats"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['packet_size', 'port', 'protocol']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Analyze for threats
        result = threat_detector.predict_threat(data)
        
        # Log the analysis
        logging.info(f"Threat analysis: {result}")
        
        return jsonify({
            'success': True,
            'analysis': result,
            'input_data': data
        }), 200
        
    except Exception as e:
        logging.error(f"Analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@api_bp.route('/train', methods=['POST'])
def train_model():
    """Train the threat detection model"""
    try:
        data = request.get_json()
        
        if not data or 'training_data' not in data:
            return jsonify({'error': 'No training data provided'}), 400
        
        success = threat_detector.train(data['training_data'])
        
        if success:
            return jsonify({'success': True, 'message': 'Model trained successfully'}), 200
        else:
            return jsonify({'error': 'Training failed'}), 500
            
    except Exception as e:
        logging.error(f"Training error: {e}")
        return jsonify({'error': 'Training failed'}), 500

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        'status': 'operational',
        'model_trained': threat_detector.is_trained,
        'version': '1.0.0'
    }), 200

@api_bp.route('/threats/history', methods=['GET'])
def get_threat_history():
    """Get threat detection history (mock data for demo)"""
    mock_history = [
        {
            'timestamp': '2024-01-01T10:00:00Z',
            'threat_level': 'high',
            'source_ip': '192.168.1.100',
            'destination_port': 1433,
            'action_taken': 'blocked'
        },
        {
            'timestamp': '2024-01-01T10:15:00Z',
            'threat_level': 'medium',
            'source_ip': '10.0.0.50',
            'destination_port': 3389,
            'action_taken': 'monitored'
        }
    ]
    
    return jsonify({
        'success': True,
        'threats': mock_history,
        'total_count': len(mock_history)
    }), 200
