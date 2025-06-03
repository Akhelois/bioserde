import os
import json
import time
import logging
import random
import socket
import requests
from datetime import datetime
from azure.iot.device import IoTHubDeviceClient, Message

# Configuration
DATA_FILE = "arduino_data.json"
RESULT_FILE = "ml_results.txt" 
POLL_INTERVAL = 5  # seconds
ML_INTERVAL = 60  # seconds
MAX_RETRIES = 3  # Maximum connection attempts

DEFAULT_API_KEY = "B4ZJoXXnCQdk5P1XArm69g7k4nYpfNmoH1XNE1faXZu2c8MinICIJQQJ99BFAAAAAAAAAAAAINFRAZMLraH3"

def read_api_key():
    """Try to read the API key from a file"""
    try:
        with open("api_key.txt", "r") as f:
            key = f.read().strip()
            if key and len(key) > 20:  # Simple validation
                return key
    except Exception:
        pass
    
    return DEFAULT_API_KEY

# Azure configuration
CONNECTION_STRING = "HostName=318Hub.azure-devices.net;DeviceId=bioserde;SharedAccessKey=ml0XIrouzxoP/zmDGex1lHNjcCj76+cD/aRwKc+r9no="

ML_ENDPOINTS = [
    "https://biogas-model-endpoint.southeastasia.inference.ml.azure.com/score",  # From screenshot
    "https://biogas-anomaly-model-1.southeastasia.inference.ml.azure.com/score", # Alternative from code
    "https://model-bioserde.southeastasia.inference.ml.azure.com/score",  # Common naming pattern
    "https://biogas-model.southeastasia.inference.ml.azure.com/score"    # Simplified name
]

AZURE_ML_ENDPOINT = ML_ENDPOINTS[0]
API_KEY = read_api_key()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='biogas_monitoring.log',
    filemode='a'
)

def check_network_connectivity():
    """Check internet and endpoint connectivity"""
    print("\n==== Network Diagnostics ====")
    
    # Check internet connection
    try:
        print("Testing internet connectivity...", end=" ")
        requests.get("https://www.microsoft.com", timeout=5)
        print("✓ Connected to internet")
    except Exception as e:
        print(f"✗ Internet connection error: {str(e)}")
        
    # Check DNS resolution
    endpoint_host = AZURE_ML_ENDPOINT.split("//")[1].split("/")[0]
    print(f"Testing DNS resolution for {endpoint_host}...", end=" ")
    try:
        ip = socket.gethostbyname(endpoint_host)
        print(f"✓ Resolved to IP: {ip}")
    except socket.gaierror as e:
        print(f"✗ DNS resolution failed: {str(e)}")
        print("  This suggests the endpoint URL might be incorrect")
        
        # Try alternate endpoint
        alt_endpoint = "biogas-anomaly-model-1.southeastasia.inference.ml.azure.com"
        print(f"  Trying alternate endpoint {alt_endpoint}...", end=" ")
        try:
            ip = socket.gethostbyname(alt_endpoint)
            print(f"✓ Alternate endpoint resolved to IP: {ip}")
            print(f"  Consider updating your AZURE_ML_ENDPOINT to use this host")
        except socket.gaierror as e:
            print(f"✗ Alternate endpoint also failed: {str(e)}")
            
    # Check Azure ML base domain
    print(f"Testing Azure ML base domain...", end=" ")
    try:
        ip = socket.gethostbyname("ml.azure.com")
        print(f"✓ Azure ML base domain resolved: {ip}")
    except socket.gaierror as e:
        print(f"✗ Azure ML base domain resolution failed: {str(e)}")
        
    print("==== Diagnostics Complete ====\n")

def setup_iot_hub():
    """Connect to Azure IoT Hub"""
    retries = 0
    while retries < MAX_RETRIES:
        try:
            client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
            client.connect()
            print("✓ Connected to Azure IoT Hub")
            logging.info("Connected to Azure IoT Hub")
            return client
        except Exception as e:
            retries += 1
            print(f"! Failed to connect to IoT Hub (attempt {retries}/{MAX_RETRIES}): {str(e)}")
            logging.error(f"Failed to connect to IoT Hub (attempt {retries}/{MAX_RETRIES}): {str(e)}")
            if retries < MAX_RETRIES:
                wait_time = 2 ** retries  # Exponential backoff
                print(f"  Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print("! Could not connect to IoT Hub after multiple attempts")
                logging.error("Could not connect to IoT Hub after multiple attempts")
                return None

def read_sensor_data():
    """Read data from Serial port or data file"""
    # Try multiple possible COM ports
    try:
        import serial
        for com_port in ['COM3', 'COM4', 'COM5', 'COM6']:
            try:
                ser = serial.Serial(com_port, 9600, timeout=1)
                time.sleep(1)  # Give some time for connection
                
                # Read a few lines to find valid JSON
                for _ in range(5):
                    line = ser.readline().decode('utf-8', errors='replace').strip()
                    if line and line.startswith('{') and line.endswith('}'):
                        try:
                            data = json.loads(line)
                            ser.close()
                            print(f"← Read data from {com_port}: pH={data.get('ph')}, biogas={data.get('biogas_production')}, gas={data.get('gas_level')}")
                            
                            # Ensure all required fields exist
                            if 'ph' not in data: data['ph'] = 7.0
                            if 'biogas_production' not in data: data['biogas_production'] = 60.0
                            if 'gas_level' not in data: data['gas_level'] = 200
                            
                            return data
                        except json.JSONDecodeError:
                            print(f"! Invalid JSON from serial: {line}")
                
                # Close if no valid data found
                ser.close()
                print(f"! No valid JSON data from {com_port}")
            except Exception as e:
                print(f"! Error reading from {com_port}: {str(e)}")
    except ImportError:
        print("! Serial library not available")
    except Exception as e:
        print(f"! Error with serial communication: {str(e)}")
    
    # Fall back to file-based reading if serial fails
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as file:
                try:
                    data = json.loads(file.read())
                    print(f"← Read data from file: pH={data.get('ph')}, biogas={data.get('biogas_production')}, gas={data.get('gas_level')}")
                    
                    # Ensure all required fields exist
                    if 'ph' not in data: data['ph'] = 7.0
                    if 'biogas_production' not in data: data['biogas_production'] = 60.0
                    if 'gas_level' not in data: data['gas_level'] = 200
                    
                    return data
                except json.JSONDecodeError:
                    print(f"! Invalid JSON in file")
        else:
            print(f"! Data file not found: {DATA_FILE}")
            # Create a default file if it doesn't exist
            create_default_data_file()
            
    except Exception as e:
        print(f"! Error reading file: {str(e)}")
    
    # If all else fails, generate simulated data
    return generate_simulated_data()

def create_default_data_file():
    """Create a default data file for testing"""
    try:
        data = {
           "ph": 7.2,
           "biogas_production": 65.5,
            "gas_level": 200  # Make sure this field is included
        }

        file_path = DATA_FILE
        with open(file_path, "w") as f:
            json.dump(data, f)

        print(f"✓ Created default data file: {os.path.abspath(file_path)}")
    except Exception as e:
        print(f"! Error creating data file: {str(e)}")

def generate_simulated_data():
    """Generate simulated sensor data"""
    print("→ Generating simulated sensor data")
    return {
        "ph": round(random.uniform(6.5, 8.0), 1),
        "biogas_production": round(random.uniform(50.0, 80.0), 1),
        "gas_level": random.randint(150, 300)
    }

def write_prediction_result(prediction):
    """Write ML prediction result to file for Arduino"""
    try:
        # Extract relevant info
        prediction_data = prediction.get("predictions", [{}])[0]
        anomaly_detected = prediction_data.get("anomaly_detected", False)
        
        # Get cause directly if available, otherwise determine from details
        if "anomaly_cause" in prediction_data and prediction_data["anomaly_cause"]:
            cause = prediction_data["anomaly_cause"]
        else:
            # Determine cause (simplified for demonstration)
            if anomaly_detected:
                anomaly_prob = prediction_data.get("anomaly_probability", 0)
                # Simple logic for cause
                if anomaly_prob > 0.8:
                    cause = "Gas Level"
                elif anomaly_prob > 0.6:
                    cause = "pH Level"
                else:
                    cause = "Biogas"
            else:
                cause = "Normal"
        
        # Write result in format Arduino expects: RESULT:1,pH Level
        result_str = f"RESULT:{1 if anomaly_detected else 0},{cause}"
        with open(RESULT_FILE, "w") as f:
            f.write(result_str)
        
        print(f"→ Writing to result file: {result_str}")
        
    except Exception as e:
        print(f"! Error writing prediction result: {str(e)}")
        logging.error(f"Error writing prediction result: {str(e)}")

def send_to_azure_ml(sensor_data):
    """Send data to Azure ML for anomaly detection"""
    global AZURE_ML_ENDPOINT
    
    # Ensure gas_level exists
    if 'gas_level' not in sensor_data:
        sensor_data['gas_level'] = 200
        print("! Warning: Missing gas_level, using default value")
    
    # Try the main endpoint
    retries = 0
    while retries < MAX_RETRIES:
        try:
            print(f"→ Sending data to ML (attempt {retries + 1}/{MAX_RETRIES})...")
            
            # Prepare data in the format expected by the model
            # This format matches what we found in the azure_ml_bridge.py file
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # First try the format from the notebook
            input_data = {
                "data": [
                    {
                        "ph": sensor_data["ph"],
                        "biogas_production": sensor_data["biogas_production"],
                        "gas_level": sensor_data["gas_level"]
                    }
                ]
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
                "Accept": "application/json"
            }
            
            # Send request with timeouts
            response = requests.post(
                url=AZURE_ML_ENDPOINT,
                json=input_data,
                headers=headers,
                timeout=(5, 30)
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Azure ML prediction received")
                logging.info(f"Azure ML connection successful")
                
                # Save this successful endpoint
                with open("successful_endpoint.txt", "w") as f:
                    f.write(AZURE_ML_ENDPOINT)
                
                return result
            else:
                print(f"! Failed with status {response.status_code}: {response.text[:100]}")
                
        except ConnectionResetError:
            print("! Connection was reset by the server, running diagnostics...")
            diagnose_connection_reset(AZURE_ML_ENDPOINT)
        except Exception as e:
            print(f"! Error: {str(e)}")
            
        retries += 1
        if retries < MAX_RETRIES:
            wait_time = 2 ** retries  # Exponential backoff
            print(f"  Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    print("! Azure ML endpoint failed, using local simulation")
    logging.error("Azure ML endpoint failed")
    
    # Fall back to simulation
    return simulate_ml_prediction(sensor_data)

def simulate_ml_prediction(sensor_data):
    """Generate simulated ML prediction when Azure ML is unavailable"""
    print("→ Generating local ML prediction simulation")
    
    # Simple anomaly detection logic
    ph = sensor_data.get('ph', 7.0)
    biogas = sensor_data.get('biogas_production', 60.0)
    gas = sensor_data.get('gas_level', 200)
    
    # Define normal ranges
    normal_ph_range = (6.5, 7.5)
    normal_biogas_range = (50, 80)
    normal_gas_range = (100, 400)
    
    # Check for anomalies
    ph_anomaly = ph < normal_ph_range[0] or ph > normal_ph_range[1]
    biogas_anomaly = biogas < normal_biogas_range[0] or biogas > normal_biogas_range[1]
    gas_anomaly = gas < normal_gas_range[0] or gas > normal_gas_range[1]
    
    # Generate anomaly probability based on how far values are from normal ranges
    prob_ph = abs(ph - 7.0) / 1.5  # pH should be around 7.0
    prob_biogas = 0 if normal_biogas_range[0] <= biogas <= normal_biogas_range[1] else abs(biogas - 65) / 30
    prob_gas = 0 if normal_gas_range[0] <= gas <= normal_gas_range[1] else abs(gas - 250) / 300
    
    # Overall probability - weighted sum
    anomaly_prob = prob_ph * 0.3 + prob_biogas * 0.3 + prob_gas * 0.4
    
    # Add a small random factor to make it more realistic
    anomaly_prob = min(max(anomaly_prob + random.uniform(-0.1, 0.1), 0.0), 1.0)
    
    # Determine if anomaly detected and what caused it
    anomaly_detected = anomaly_prob > 0.5
    
    # Create detailed simulation response
    details = {
        "simulated": True,
        "normal_ranges": {
            "ph": normal_ph_range,
            "biogas": normal_biogas_range,
            "gas": normal_gas_range
        },
        "anomaly_details": {
            "ph_anomaly": ph_anomaly,
            "ph_value": ph,
            "ph_contribution": prob_ph,
            
            "biogas_anomaly": biogas_anomaly,
            "biogas_value": biogas,
            "biogas_contribution": prob_biogas,
            
            "gas_anomaly": gas_anomaly,
            "gas_value": gas,
            "gas_contribution": prob_gas
        }
    }
    
    # Determine primary cause of anomaly
    if anomaly_detected:
        contributions = [
            ("pH Level", prob_ph),
            ("Biogas", prob_biogas),
            ("Gas Level", prob_gas)
        ]
        # Sort by contribution (highest first)
        contributions.sort(key=lambda x: x[1], reverse=True)
        primary_cause = contributions[0][0]
        details["primary_cause"] = primary_cause
    else:
        details["primary_cause"] = None
    
    # Create response in same format as Azure ML would
    return {
        "predictions": [{
            "anomaly_detected": anomaly_detected,
            "anomaly_probability": anomaly_prob,
            "anomaly_cause": details["primary_cause"] if anomaly_detected else None,
            "details": details
        }]
    }

def discover_valid_endpoint():
    """Attempt to discover a valid ML endpoint based on common patterns"""
    print("\n==== Attempting ML Endpoint Discovery ====")

    # First, check for previously successful endpoint
    try:
        with open("successful_endpoint.txt", "r") as f:
            endpoint_url = f.read().strip()
            if endpoint_url:
                print(f"Found previously successful endpoint: {endpoint_url}")
                try:
                    # Quick health check 
                    base_url = endpoint_url.split('/score')[0]
                    response = requests.head(base_url, timeout=2)
                    print(f"✓ Previous endpoint is responding with HTTP {response.status_code}")
                    return endpoint_url
                except Exception as e:
                    print(f"✗ Previous endpoint not responding: {str(e)}")
    except Exception:
        pass  # File doesn't exist or is invalid

    # Second, check for a local mock endpoint
    try:
        with open("endpoint_url.txt", "r") as f:
            endpoint_url = f.read().strip()
            if endpoint_url and "localhost" in endpoint_url:
                print(f"Found local mock endpoint: {endpoint_url}")
                try:
                    # Quick test
                    response = requests.get(endpoint_url.replace("/score", "/"), timeout=2)
                    print(f"✓ Local endpoint is running")
                    # Start the mock server if not already running
                    try:
                        import subprocess
                        subprocess.Popen(["python", "hh.py"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
                    except Exception:
                        pass  # Silently continue if server is already running
                    return endpoint_url
                except Exception as e:
                    print(f"✗ Local endpoint not responding: {str(e)}")
                    print("  Starting mock endpoint with: python hh.py")
                    try:
                        import subprocess
                        subprocess.Popen(["python", "hh.py"], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
                        print("  Mock endpoint started, waiting 2 seconds...")
                        time.sleep(2)
                        return endpoint_url  # Return it anyway and hope it started
                    except Exception as e:
                        print(f"  Failed to start mock endpoint: {e}")
    except Exception:
        pass  # File doesn't exist or is invalid

    # From the notebook, try the correct endpoint name
    candidate_endpoints = [
        "https://biogas-endpoint.southeastasia.inference.ml.azure.com/score",
        "https://biogas-anomaly.southeastasia.inference.ml.azure.com/score"  
    ]
    
    # Add our existing endpoints
    for endpoint in ML_ENDPOINTS:
        if endpoint not in candidate_endpoints:
            candidate_endpoints.append(endpoint)
    
    # Try each candidate
    for endpoint in candidate_endpoints:
        print(f"Checking endpoint: {endpoint}")
        try:
            # Try a basic connection to the endpoint's base URL
            base_url = endpoint.split('/score')[0]
            response = requests.head(
                base_url,
                timeout=5,
                headers={"Authorization": f"Bearer {API_KEY}"}
            )
            print(f"  Response: HTTP {response.status_code}")
            
            if response.status_code < 500:
                print(f"✓ Found working endpoint: {endpoint}")
                return endpoint
        except Exception as e:
            print(f"  Failed: {str(e)}")
    
    # As a last resort, check if we can start a local mock server
    if os.path.exists("hh.py"):
        try:
            print("Attempting to start local mock server...")
            import subprocess
            process = subprocess.Popen(["python", "hh.py"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            print("Mock endpoint started at http://localhost:8000/score")
            time.sleep(2)  # Give it time to start
            return "http://localhost:8000/score"
        except Exception as e:
            print(f"Failed to start mock server: {e}")
    
    print("✗ No working endpoints found")
    return None

def check_endpoint_health(url):
    """Test if an endpoint is accepting connections"""
    try:
        # Try a simple HEAD request to see if the server responds
        base_url = url.split('/score')[0]
        response = requests.head(base_url, timeout=5)
        print(f"Endpoint health check: HTTP {response.status_code}")
        return True
    except Exception as e:
        print(f"Endpoint health check failed: {e}")
        return False

def test_connection():
    """Test connections to Azure services"""
    print("\n==== Testing Azure Connections ====\n")
    
    # Test IoT Hub
    print("Testing IoT Hub connection...")
    iot_success = False
    
    try:
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        client.connect()
        print("✓ Connected to Azure IoT Hub")
        
        # Send test message
        test_message = Message(json.dumps({"test": True, "time": str(datetime.now())}))
        client.send_message(test_message)
        print("✓ IoT Hub connection successful!")
        print("✓ Test message sent to IoT Hub")
        
        client.disconnect()
        iot_success = True
    except Exception as e:
        print(f"! IoT Hub connection failed: {str(e)}")
        logging.error(f"IoT Hub connection test failed: {str(e)}")
    
    # Test Azure ML
    print("\nTesting Azure ML connection...")
    ml_success = False
    
    test_data = {"ph": 7.0, "biogas_production": 65.0, "gas_level": 200}
    result = send_to_azure_ml(test_data)
    
    if result and not result.get("predictions", [{}])[0].get("details", {}).get("simulated", True):
        print("✓ Azure ML connection successful!")
        ml_success = True
    else:
        print("✗ Azure ML connection failed, falling back to simulation")
        logging.error("Azure ML connection test failed")
    
    print()  # Extra space
    return iot_success, ml_success

def diagnose_connection_reset(endpoint):
    """Diagnose why a connection is being reset after successful DNS resolution"""
    print("\n==== Connection Reset Diagnostics ====")
    print(f"Endpoint can be resolved but resets connection: {endpoint}")
    
    # Check API key format
    print(f"Checking API key format...")
    if len(API_KEY) < 30:
        print("✗ API key seems too short - should be a longer string")
    elif not API_KEY.strip():
        print("✗ API key is empty")
    else:
        print("✓ API key has expected length format")
        # Check for common API key format issues
        if API_KEY.startswith("Bearer "):
            print("✗ API key contains 'Bearer ' prefix which should be in the header, not the key")
        elif ' ' in API_KEY:
            print("✗ API key contains spaces which is unusual")
        elif '\n' in API_KEY:
            print("✗ API key contains newline characters - check your file reading")
    
    # Try to read API key from notebook
    try:
        with open("model.ipynb", "r") as f:
            notebook_content = f.read()
            if "get_keys(\"biogas-endpoint\")" in notebook_content:
                print("! Found API key reference in notebook - check 'model.ipynb' for the latest key")
    except Exception:
        pass
        
    # Extract hostname from endpoint
    hostname = endpoint.split("//")[1].split("/")[0]
        
    # 1. Check if port is open with a socket connection
    print(f"Checking if port 443 is open on {hostname}...")
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((hostname, 443))
        if result == 0:
            print("✓ Port 443 is open")
        else:
            print(f"✗ Port 443 is closed or filtered (code: {result})")
        sock.close()
    except Exception as e:
        print(f"✗ Socket error: {e}")
    
    # 2. Try a plain HTTPS request without authentication
    print(f"Trying a simple HTTPS request to {hostname}...")
    try:
        response = requests.get(f"https://{hostname}", timeout=5, 
                               verify=True)  # With certificate verification
        print(f"✓ Server responded with status code {response.status_code}")
        print(f"  Response: {response.text[:100]}...")
    except requests.exceptions.SSLError as e:
        print(f"✗ SSL certificate error: {e}")
        # Try without verification
        try:
            print("  Retrying without certificate verification...")
            response = requests.get(f"https://{hostname}", timeout=5, 
                                   verify=False)
            print(f"✓ Server responded with status code {response.status_code}")
            print(f"  Response: {response.text[:100]}...")
        except Exception as e2:
            print(f"✗ Still failed: {e2}")
    except Exception as e:
        print(f"✗ HTTPS request failed: {e}")
    
    # 3. Try different API versions in header
    api_versions = ["2019-06-01", "2020-06-01", "2021-03-01", "2021-10-01"]
    for version in api_versions:
        print(f"Trying API version: {version}...")
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}",
                "Accept": "application/json",
                "azureml-model-deployment": "production",
                "Api-Version": version
            }
            response = requests.options(
                url=endpoint,
                headers=headers,
                timeout=5
            )
            print(f"  Response: {response.status_code}")
            if response.status_code < 500:  # Any non-server error might give us a clue
                print(f"  Headers: {dict(response.headers)}")
        except Exception as e:
            print(f"  Failed: {e}")
    
    print("\nPossible issues:")
    print("1. Your API key may be expired or invalid")
    print("2. The endpoint might have been deleted or moved")
    print("3. There might be network restrictions (firewall, proxy)")
    print("4. The service might be temporarily unavailable")
    print("\nSuggested actions:")
    print("1. Check in the Azure portal if the endpoint still exists")
    print("2. Generate a new API key")
    print("3. Try from a different network")
    print("4. Try direct connection with curl or Postman\n")

def main():
    # Check for development mode
    import sys
    dev_mode = "--dev" in sys.argv or "-d" in sys.argv
    
    print("\n===== BIOSERDE ML-IoT BRIDGE (FILE MODE) =====")
    print("This script connects to Azure IoT Hub and ML services")
    print("Using file-based communication with Arduino")
    if dev_mode:
        print("Running in DEVELOPMENT mode with local mock ML server")
    print("==============================================\n")
    
    # Run network diagnostics (skip in dev mode)
    if not dev_mode:
        check_network_connectivity()
    
    # In dev mode, force local endpoint
    global AZURE_ML_ENDPOINT
    if dev_mode:
        # Start the mock server
        try:
            import subprocess
            subprocess.Popen(["python", "hh.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Starting local mock ML server...")
            time.sleep(1)
            AZURE_ML_ENDPOINT = "http://localhost:8000/score"
        except Exception as e:
            print(f"Failed to start mock server: {e}")
    else:
        # Normal endpoint discovery
        discovered_endpoint = discover_valid_endpoint()
        if discovered_endpoint:
            print(f"Using discovered endpoint: {discovered_endpoint}")
            AZURE_ML_ENDPOINT = discovered_endpoint
            if not check_endpoint_health(AZURE_ML_ENDPOINT):
                diagnose_connection_reset(AZURE_ML_ENDPOINT)
        else:
            print("Using default endpoint (may not work)")
    
        
    # Try a direct endpoint health check
    check_endpoint_health(AZURE_ML_ENDPOINT)
    
    # Test connections
    test_connection()
    
    # Explain system operation
    print(f"Arduino should write sensor data to: {os.path.abspath(DATA_FILE)}")
    print(f"This script will write ML results to: {os.path.abspath(RESULT_FILE)}")
    print("\nFile format examples:")
    print('{"ph":7.2,"biogas_production":65.5,"gas_level":200}  <- Arduino writes this')
    print('RESULT:1,pH Level  <- This script writes this')
    print("\nNo direct serial connection required!")
    
    # Set up IoT Hub client
    iot_client = setup_iot_hub()
    if not iot_client:
        print("! Will continue without IoT Hub functionality")
    else:
        print("✓ Connected to Azure IoT Hub")
    
    print("\nMonitoring biogas system...")
    print("Press Ctrl+C to exit\n")
    
    last_ml_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Process ML prediction on interval
            if current_time - last_ml_time >= ML_INTERVAL:
                print("\n----- Processing ML Prediction Cycle -----")
                
                try:
                    # Get sensor data
                    sensor_data = read_sensor_data()
                    
                    if sensor_data:
                        # Ensure gas_level exists
                        if 'gas_level' not in sensor_data:
                            print("! Adding missing gas_level field with default value")
                            sensor_data['gas_level'] = 200
                        
                        # Send to IoT Hub
                        if iot_client:
                            try:
                                message_json = json.dumps(sensor_data)
                                msg = Message(message_json)
                                iot_client.send_message(msg)
                                print("✓ Data sent to IoT Hub")
                            except Exception as e:
                                print(f"! IoT Hub message error: {str(e)}")
                                # Re-establish connection if needed
                                try:
                                    iot_client.disconnect()
                                    iot_client = setup_iot_hub()
                                except:
                                    pass
                        
                        # Get ML prediction
                        prediction = send_to_azure_ml(sensor_data)
                        if prediction:
                            # Display results
                            anomaly_prob = prediction.get("predictions", [{}])[0].get("anomaly_probability", 0)
                            anomaly_detected = prediction.get("predictions", [{}])[0].get("anomaly_detected", False)
                            simulated = prediction.get("predictions", [{}])[0].get("details", {}).get("simulated", False)
                            
                            print("\n----- Biogas System Status -----")
                            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                            print(f"pH Level: {sensor_data.get('ph', 'N/A')}")
                            print(f"Biogas Production: {sensor_data.get('biogas_production', 'N/A')}")
                            print(f"Gas Level: {sensor_data.get('gas_level', 'N/A')}")
                            print(f"Anomaly Probability: {anomaly_prob:.2f}")
                            print(f"Status: {'⚠️ ANOMALY DETECTED!' if anomaly_detected else '✓ Normal'}")
                            if simulated:
                                print("Note: Using simulated ML prediction (Azure ML unavailable)")
                            
                            # Write results to file for Arduino
                            write_prediction_result(prediction)
                    else:
                        print("! No sensor data available")
                
                except Exception as e:
                    print(f"! Unexpected error in ML cycle: {str(e)}")
                    logging.error(f"Unexpected error in ML cycle: {str(e)}")
                
                last_ml_time = current_time
                print("----- ML Cycle Complete -----\n")
                
            # Wait before polling again
            time.sleep(POLL_INTERVAL)
                
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user")
    except Exception as e:
        print(f"! Unexpected error: {str(e)}")
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        if iot_client:
            try:
                iot_client.disconnect()
            except:
                pass
        print("\nConnections closed")

if __name__ == "__main__":
    main()