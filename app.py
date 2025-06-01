from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import serial
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

current_sensor_data = {
    'ph': 7.0,
    'biogas_production': 50.0,
    'timestamp': datetime.now().isoformat(),
    'anomaly_detected': False,
    'anomaly_probability': 0.0,
    'system_status': 'Normal'
}

historical_data = []

try:
    model_package = joblib.load('biogas_anomaly_model.pkl')
    model = model_package['model']
    scaler = model_package['scaler']
    cause_encoder = model_package['cause_encoder']
    feature_columns = model_package['feature_columns']
    logger.info("ML model loaded successfully")
except Exception as e:
    logger.error(f"Error loading ML model: {e}")
    model = None
    scaler = None
    cause_encoder = None

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
ser = None

def setup_serial():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        logger.info(f"Connected to Arduino on {SERIAL_PORT}")
        return True
    except Exception as e:
        logger.error(f"Could not connect to Arduino: {e}")
        return False

def read_arduino_data():
    global ser
    if not ser:
        if not setup_serial():
            return None
    
    try:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            logger.info(f"Raw Arduino data: {line}")
            
            data_parts = line.split(',')
            data = {}
            for part in data_parts:
                key_value = part.split(':')
                if len(key_value) == 2:
                    data[key_value[0].strip()] = float(key_value[1].strip())
            
            return data
        return None
    except Exception as e:
        logger.error(f"Error reading from Arduino: {e}")
        return None

def predict_anomaly(ph, biogas_production):
    """Predict anomaly using ML model"""
    if not model or not scaler:
        logger.error("ML model not loaded")
        return {"anomaly_probability": 0.0, "cause": "Unknown"}
    
    try:
        now = datetime.now()
        sample = pd.DataFrame({
            'ph': [ph],
            'biogas_production': [biogas_production],
            'hour': [now.hour],
            'day': [now.day],
            'month': [now.month],
            'day_of_week': [now.weekday()]
        })
        
        sample_scaled = scaler.transform(sample)
        
        prediction = model.predict(sample_scaled)
        anomaly_probability = prediction[0][0]
        cause_id = int(np.round(np.clip(prediction[0][1], 0, len(cause_encoder.classes_) - 1)))
        cause = cause_encoder.inverse_transform([cause_id])[0]
        
        return {
            "anomaly_probability": float(anomaly_probability),
            "cause": str(cause) if anomaly_probability > 0.5 else "None"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"anomaly_probability": 0.0, "cause": "Error in prediction"}

@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    arduino_data = read_arduino_data()
    
    if arduino_data and 'ph' in arduino_data and 'biogas' in arduino_data:
        current_sensor_data['ph'] = arduino_data['ph']
        current_sensor_data['biogas_production'] = arduino_data['biogas']
        current_sensor_data['timestamp'] = datetime.now().isoformat()
        
        prediction = predict_anomaly(arduino_data['ph'], arduino_data['biogas'])
        current_sensor_data['anomaly_probability'] = prediction['anomaly_probability']
        current_sensor_data['anomaly_detected'] = prediction['anomaly_probability'] > 0.5
        current_sensor_data['anomaly_cause'] = prediction['cause']
        
        if current_sensor_data['anomaly_detected']:
            current_sensor_data['system_status'] = 'Warning'
        else:
            current_sensor_data['system_status'] = 'Normal'
        
        historical_data.append(dict(current_sensor_data))
        if len(historical_data) > 100:
            historical_data.pop(0)
    
    return jsonify(current_sensor_data)

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    if not data or 'ph' not in data or 'biogas_production' not in data:
        return jsonify({"error": "Missing required parameters"}), 400
    
    ph = float(data['ph'])
    biogas_production = float(data['biogas_production'])
    
    prediction = predict_anomaly(ph, biogas_production)
    return jsonify({
        "prediction": prediction,
        "input": {
            "ph": ph,
            "biogas_production": biogas_production
        }
    })

@app.route('/api/reset-alarm', methods=['POST'])
def reset_alarm():
    current_sensor_data['system_status'] = 'Normal'
    current_sensor_data['anomaly_detected'] = False
    return jsonify({"success": True, "message": "Alarm reset successfully"})

@app.route('/api/system-status', methods=['GET'])
def system_status():
    return jsonify({
        "status": current_sensor_data['system_status'],
        "last_updated": current_sensor_data['timestamp'],
        "anomaly_detected": current_sensor_data['anomaly_detected'],
        "anomaly_cause": current_sensor_data.get('anomaly_cause', 'Unknown')
    })

@app.route('/api/historical-data', methods=['GET'])
def get_historical_data():
    return jsonify(historical_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)