import os
import json
import time
import logging
import random
import requests
from datetime import datetime
from azure.iot.device import IoTHubDeviceClient, Message

# Configuration
DATA_FILE = "arduino_data.json"
RESULT_FILE = "ml_results.txt" 
POLL_INTERVAL = 5
ML_INTERVAL = 60

# Azure configuration
CONNECTION_STRING = "HostName=318Hub.azure-devices.net;DeviceId=bioserde;SharedAccessKey=ml0XIrouzxoP/zmDGex1lHNjcCj76+cD/aRwKc+r9no="
AZURE_ML_ENDPOINT = "https://biogas-model-endpoint.southeastasia.inference.ml.azure.com/score"

def read_api_key():
    try:
        with open("api_key.txt", "r") as f:
            return f.read().strip()
    except:
        return None

API_KEY = read_api_key()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='biogas_monitoring.log',
    filemode='a'
)

def setup_iot_hub():
    try:
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        client.connect()
        print("✓ Connected to Azure IoT Hub")
        return client
    except Exception as e:
        print(f"! Failed to connect to IoT Hub: {str(e)}")
        return None

def read_sensor_data():
    # Try to read from file
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as file:
                data = json.loads(file.read())
                print(f"← Read data from file: pH={data.get('ph')}, biogas={data.get('biogas_production')}")
                return data
    except Exception as e:
        print(f"! Error reading file: {str(e)}")
    
    print("Generating simulated sensor data")
    return {
        "ph": round(random.uniform(6.5, 8.0), 1),
        "biogas_production": round(random.uniform(50.0, 80.0), 1),
        "gas_level": random.randint(150, 300)
    }

def write_prediction_result(prediction):
    try:
        prediction_data = prediction.get("predictions", [{}])[0]
        anomaly_detected = prediction_data.get("anomaly_detected", False)
        cause = prediction_data.get("anomaly_cause", "Normal")
        
        result_str = f"RESULT:{1 if anomaly_detected else 0},{cause}"
        with open(RESULT_FILE, "w") as f:
            f.write(result_str)
        
        print(f"→ Writing to result file: {result_str}")
    except Exception as e:
        print(f"! Error writing prediction result: {str(e)}")

def send_to_azure_ml(sensor_data):
    try:
        # Prepare data for the model
        input_data = {
            "data": [
                {
                    "ph": sensor_data["ph"],
                    "biogas_production": sensor_data["biogas_production"],
                    "gas_level": sensor_data.get("gas_level", 200)
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json"
        }
        
        # Send request
        response = requests.post(
            url=AZURE_ML_ENDPOINT,
            json=input_data,
            headers=headers,
            timeout=10
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("✓ Azure ML prediction received")
            return result
        else:
            print(f"! Failed with status {response.status_code}: {response.text[:100]}")
            
    except Exception as e:
        print(f"! ML API Error: {str(e)}")
    
    # Fall back to simulation
    return simulate_ml_prediction(sensor_data)

def simulate_ml_prediction(sensor_data):
    print("Generating local ML prediction simulation")
    
    # Simple anomaly detection
    ph = sensor_data.get('ph', 7.0)
    biogas = sensor_data.get('biogas_production', 60.0)
    
    # Generate anomaly probability
    anomaly_prob = max(0, min(1, abs(ph - 7.0) / 1.5 + abs(biogas - 60) / 30))
    anomaly_detected = anomaly_prob > 0.5
    
    # Determine cause
    if anomaly_detected:
        cause = "pH Level" if abs(ph - 7.0) > abs(biogas - 60) / 30 else "Biogas"
    else:
        cause = None
    
    # Create response
    return {
        "predictions": [{
            "anomaly_detected": anomaly_detected,
            "anomaly_probability": anomaly_prob,
            "anomaly_cause": cause
        }]
    }

def main():
    print("Connecting to Azure IoT Hub and ML services...")
    
    # Set up IoT Hub client
    iot_client = setup_iot_hub()
    
    print("Monitoring biogas system...")
    
    last_ml_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Process ML prediction on interval
            if current_time - last_ml_time >= ML_INTERVAL:
                
                # Get sensor data
                sensor_data = read_sensor_data()
                
                # Send to IoT Hub
                if iot_client:
                    try:
                        message_json = json.dumps(sensor_data)
                        msg = Message(message_json)
                        iot_client.send_message(msg)
                        print("✓ Data sent to IoT Hub")
                    except Exception as e:
                        print(f"! IoT Hub error: {str(e)}")
                
                # Get ML prediction
                prediction = send_to_azure_ml(sensor_data)
                
                # Display results
                anomaly_prob = prediction.get("predictions", [{}])[0].get("anomaly_probability", 0)
                anomaly_detected = prediction.get("predictions", [{}])[0].get("anomaly_detected", False)
                
                print("\n----- Biogas System Status -----")
                print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"pH Level: {sensor_data.get('ph', 'N/A')}")
                print(f"Biogas Production: {sensor_data.get('biogas_production', 'N/A')}")
                print(f"Anomaly Probability: {anomaly_prob:.2f}")
                print(f"Status: {'⚠️ ANOMALY DETECTED!' if anomaly_detected else '✓ Normal'}")
                
                # Write results to file for Arduino
                write_prediction_result(prediction)
                
                last_ml_time = current_time
                
            time.sleep(POLL_INTERVAL)
                
    except KeyboardInterrupt:
        print("Program terminated by user")
    except Exception as e:
        print(f"! Error: {str(e)}")
        logging.error(f"Error: {str(e)}")
    finally:
        if iot_client:
            try:
                iot_client.disconnect()
            except:
                pass
        print("Connections closed")

if __name__ == "__main__":
    main()