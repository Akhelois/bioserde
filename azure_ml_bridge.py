import serial
import json
import requests
import time
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='biogas_monitoring.log',
    filemode='a'
)

SERIAL_PORT = 'COM3' 
BAUD_RATE = 9600

AZURE_ENDPOINT = "https://biogas-endpoint.southeastasia.inference.ml.azure.com/score"
API_KEY = "A9fEmlMO1EKMBhyNQaeKYgJ2WoCm74lV4RqFIijf2231pWBD8JRIJQQJ99BEAAAAAAAAAAAAINFRAZML1c7h" 

def setup_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        logging.info(f"Connected to Arduino on {SERIAL_PORT}")
        time.sleep(2)  
        return ser
    except Exception as e:
        logging.error(f"Failed to connect to serial port: {str(e)}")
        return None

def read_sensor_data(ser):
    try:
        ser.write(b"READ\n")
        time.sleep(1)
        
    
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            try:
                data = json.loads(line)
                return data
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON received: {line}")
                return None
        else:
            logging.warning("No data received from Arduino")
            return None
    except Exception as e:
        logging.error(f"Error reading from serial port: {str(e)}")
        return None

def send_to_azure_ml(sensor_data):
    if not sensor_data:
        return None
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    azure_data = {
        "data": [
            [current_time, sensor_data["ph"], sensor_data["biogas_production"]]
        ]
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        logging.info(f"Sending data to Azure ML: {azure_data}")
        response = requests.post(
            AZURE_ENDPOINT,
            json=azure_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            logging.info(f"Prediction received: {result}")
            return result
        else:
            logging.error(f"Azure ML API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error sending data to Azure ML: {str(e)}")
        return None

def process_prediction(prediction, sensor_data):
    if not prediction or "predictions" not in prediction:
        return
    
    try:
        anomaly_prob = prediction["predictions"][0]["anomaly_probability"]
        anomaly_detected = prediction["predictions"][0]["anomaly_detected"]
        
        print("\n--- Biogas System Status ---")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"pH Level: {sensor_data['ph']}")
        print(f"Biogas Production: {sensor_data['biogas_production']}")
        print(f"Anomaly Probability: {anomaly_prob:.2f}")
        print(f"Status: {'ANOMALY DETECTED!' if anomaly_detected else 'Normal'}")
        
        if anomaly_detected:
            logging.warning(f"ANOMALY DETECTED! pH={sensor_data['ph']}, " +
                           f"biogas={sensor_data['biogas_production']}, " +
                           f"probability={anomaly_prob:.2f}")
    except Exception as e:
        logging.error(f"Error processing prediction: {str(e)}")

def main():
    print("Connecting to Arduino...")
    
    ser = setup_serial()
    if not ser:
        print("Failed to connect to Arduino. Exiting.")
        return
    
    print("Connected successfully!")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            sensor_data = read_sensor_data(ser)
            
            if sensor_data:
                prediction = send_to_azure_ml(sensor_data)
                
                process_prediction(prediction, sensor_data)
            
            time.sleep(60)          
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial connection closed")

if __name__ == "__main__":
    main()