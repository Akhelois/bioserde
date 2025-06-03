import os
import joblib
import json
import numpy as np

def init():
    global model_package
    
    # Load the model from the artifacts
    model_path = os.path.join(os.getenv("AZUREML_MODEL_DIR"), "biogas_anomaly_model.pkl")
    model_package = joblib.load(model_path)
    
    print("Model initialized successfully!")

def run(raw_data):
    try:
        # Convert the input data to a numpy array
        data = json.loads(raw_data)
        
        # Get the feature names from the model package
        feature_columns = model_package['feature_columns']
        
        # Ensure the input has all required features
        input_data = np.array([data[feature] for feature in feature_columns]).reshape(1, -1)
        
        # Scale the input data
        scaled_data = model_package['scaler'].transform(input_data)
        
        # Make prediction
        prediction = model_package['model'].predict(scaled_data)
        
        # Extract anomaly prediction
        anomaly_score = prediction[0, 0]
        anomaly_result = int(anomaly_score >= 0.5)
        
        # Extract cause prediction
        cause_id = int(np.round(prediction[0, 1]))
        cause = model_package['cause_encoder'].inverse_transform([cause_id])[0]
        
        # Create response
        result = {
            'anomaly_detected': bool(anomaly_result),
            'anomaly_score': float(anomaly_score),
            'cause': cause,
            'cause_id': cause_id
        }
        
        return json.dumps(result)
    
    except Exception as e:
        error = str(e)
        return json.dumps({"error": error})