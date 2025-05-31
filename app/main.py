from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from app.api.routes import api_bp
from app.models.threat_detector import ThreatDetector

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'threat-detection-api'}), 200
    
    # Metrics endpoint for monitoring
    @app.route('/metrics')
    def metrics():
        # Simple metrics - in production, use proper metrics library
        return jsonify({
            'requests_total': 1000,
            'threats_detected': 42,
            'false_positives': 3,
            'uptime_seconds': 86400
        }), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
