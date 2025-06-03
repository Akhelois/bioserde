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
    if not model_package:
        logger.error("ML model not loaded")
        return {"anomaly_probability": 0.0, "cause": "Unknown"}
    
    try:
        now = datetime.now()
        # Create input data matching expected feature columns
        feature_data = {
            'ph': ph,
            'biogas_production': biogas_production,
            'hour': now.hour,
            'day': now.day,
            'month': now.month,
            'day_of_week': now.weekday()
        }
        
        feature_columns = model_package['feature_columns']
        
        input_data = np.array([feature_data.get(feature, 0) for feature in feature_columns]).reshape(1, -1)
        
        scaled_data = model_package['scaler'].transform(input_data)
        
        if 'feature_selector' in model_package:
            scaled_data = model_package['feature_selector'].transform(scaled_data)
        
        prediction = model_package['model'].predict(scaled_data)
        
        anomaly_probability = float(prediction[0][0])
        
        cause_id = int(np.round(prediction[0][1]))
        cause = model_package['cause_encoder'].inverse_transform([cause_id])[0]
        
        logger.info(f"Prediction result: anomaly_prob={anomaly_probability}, cause={cause}")
        return {
            "anomaly_probability": anomaly_probability,
            "cause": str(cause) if anomaly_probability > 0.5 else "None"
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {"anomaly_probability": 0.0, "cause": "Error in prediction"}

def generate_sample_historical_data():
    global historical_data
    base_time = datetime.now()
    for i in range(20):
        time_offset = i * 15 * 60
        sample_time = base_time - pd.Timedelta(seconds=time_offset)
        
        ph = 7.0 + np.sin(i/3) * 0.5
        biogas = 50.0 + np.cos(i/2) * 15
        
        anomaly_prob = 0.1
        anomaly_detected = False
        cause = "None"
        
        if i == 5 or i == 15:
            anomaly_prob = 0.85
            anomaly_detected = True
            cause = "High methane concentration" if i == 5 else "Low digestion rate"
        
        entry = {
            'ph': ph,
            'biogas_production': biogas,
            'timestamp': sample_time.isoformat(),
            'anomaly_detected': anomaly_detected,
            'anomaly_probability': anomaly_prob,
            'system_status': 'Warning' if anomaly_detected else 'Normal',
            'anomaly_cause': cause
        }
        historical_data.append(entry)

generate_sample_historical_data()

@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    arduino_data = read_arduino_data()
    
    if arduino_data and 'ph' in arduino_data and 'biogas' in arduino_data:
        current_sensor_data['ph'] = arduino_data['ph']
        current_sensor_data['biogas_production'] = arduino_data['biogas']
    else:
        current_sensor_data['ph'] = current_sensor_data.get('ph', 7.0) + (np.random.random() - 0.5) * 0.1
        current_sensor_data['biogas_production'] = current_sensor_data.get('biogas_production', 50.0) + (np.random.random() - 0.5) * 2
    
    current_sensor_data['timestamp'] = datetime.now().isoformat()
    
    prediction = predict_anomaly(current_sensor_data['ph'], current_sensor_data['biogas_production'])
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
    try:
        data = request.json
        if not data or 'ph' not in data or 'biogas_production' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        ph = float(data['ph'])
        biogas_production = float(data['biogas_production'])
        
        prediction = predict_anomaly(ph, biogas_production)
        
        # Create response matching what the client expects
        result = {
            "prediction": prediction,
            "input": {
                "ph": ph,
                "biogas_production": biogas_production
            }
        }
        
        return jsonify(result)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error during prediction: {error_msg}")
        return jsonify({"error": error_msg}), 500
       
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

@app.route('/api/reset-alarm', methods=['POST'])
def reset_alarm():
    current_sensor_data['anomaly_detected'] = False
    current_sensor_data['system_status'] = 'Normal'
    return jsonify({"success": True, "message": "Alarm reset successfully"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)