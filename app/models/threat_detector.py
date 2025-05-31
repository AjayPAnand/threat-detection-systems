import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import logging

class ThreatDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.logger = logging.getLogger(__name__)
    
    def extract_features(self, network_data):
        """Extract features from network traffic data"""
        try:
            features = {
                'packet_size': network_data.get('packet_size', 0),
                'frequency': network_data.get('frequency', 0),
                'port_number': network_data.get('port', 80),
                'protocol_type': self._encode_protocol(network_data.get('protocol', 'TCP')),
                'connection_duration': network_data.get('duration', 0)
            }
            return np.array(list(features.values())).reshape(1, -1)
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            raise
    
    def _encode_protocol(self, protocol):
        """Simple protocol encoding"""
        protocol_map = {'TCP': 1, 'UDP': 2, 'ICMP': 3, 'HTTP': 4, 'HTTPS': 5}
        return protocol_map.get(protocol.upper(), 0)
    
    def train(self, training_data):
        """Train the threat detection model"""
        try:
            X = np.array(training_data)
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            self.is_trained = True
            self.logger.info("Model training completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            return False
    
    def predict_threat(self, network_data):
        """Predict if network data contains threats"""
        if not self.is_trained:
            # For demo purposes, use a simple rule-based approach
            return self._simple_threat_detection(network_data)
        
        try:
            features = self.extract_features(network_data)
            features_scaled = self.scaler.transform(features)
            prediction = self.model.predict(features_scaled)
            confidence = self.model.decision_function(features_scaled)[0]
            
            is_threat = prediction[0] == -1
            threat_level = self._calculate_threat_level(confidence)
            
            return {
                'is_threat': is_threat,
                'confidence': abs(confidence),
                'threat_level': threat_level,
                'recommendation': self._get_recommendation(is_threat, threat_level)
            }
        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return {'error': 'Prediction failed', 'is_threat': False}
    
    def _simple_threat_detection(self, network_data):
        """Simple rule-based threat detection for demo"""
        suspicious_ports = [1433, 3389, 22, 23, 135, 139, 445]
        large_packet_threshold = 1500
        
        port = network_data.get('port', 80)
        packet_size = network_data.get('packet_size', 0)
        
        is_threat = (port in suspicious_ports or 
                    packet_size > large_packet_threshold or
                    network_data.get('frequency', 0) > 1000)
        
        threat_level = 'high' if port in suspicious_ports else ('medium' if packet_size > large_packet_threshold else 'low')
        
        return {
            'is_threat': is_threat,
            'confidence': 0.75 if is_threat else 0.25,
            'threat_level': threat_level,
            'recommendation': self._get_recommendation(is_threat, threat_level)
        }
    
    def _calculate_threat_level(self, confidence):
        """Calculate threat level based on confidence"""
        abs_confidence = abs(confidence)
        if abs_confidence > 0.7:
            return 'high'
        elif abs_confidence > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _get_recommendation(self, is_threat, threat_level):
        """Get security recommendation"""
        if not is_threat:
            return "Traffic appears normal. Continue monitoring."
        
        recommendations = {
            'low': "Monitor closely. Consider additional verification.",
            'medium': "Investigate immediately. Check source and destination.",
            'high': "ALERT: Block traffic immediately. Conduct security audit."
        }
        return recommendations.get(threat_level, "Unknown threat level")
    
    def save_model(self, filepath):
        """Save trained model"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, filepath)
            self.logger.info(f"Model saved to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            return False
    
    def load_model(self, filepath):
        """Load trained model"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.is_trained = model_data['is_trained']
            self.logger.info(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False
