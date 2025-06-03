
import json
import numpy as np
import pandas as pd
import joblib
from azureml.core.model import Model

def init():
    global model_package
    model_path = Model.get_model_path('model_biogas')
    model_package = joblib.load(model_path)
    print("Model loaded successfully!")

def run(raw_data):
    try:
        # Parse input data
        data = json.loads(raw_data)
        input_df = pd.DataFrame(data["data"])
        
        # Extract model components
        model = model_package['model']
        scaler = model_package['scaler']
        cause_encoder = model_package['cause_encoder']
        feature_columns = model_package['feature_columns']
        
        # Ensure all expected features are present
        for col in feature_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        
        # Scale input data
        input_scaled = scaler.transform(input_df[feature_columns])
        
        # Make prediction
        raw_prediction = model.predict(input_scaled)
        
        # Process predictions
        anomaly_prob = raw_prediction[:, 0]
        anomaly_detected = (anomaly_prob >= 0.5).astype(int)
        cause_id = np.clip(np.round(raw_prediction[:, 1]), 0, len(cause_encoder.classes_) - 1).astype(int)
        cause_label = cause_encoder.inverse_transform(cause_id)
        
        # Return results
        results = []
        for i in range(len(input_df)):
            results.append({
                "anomaly_detected": bool(anomaly_detected[i]),
                "anomaly_probability": float(anomaly_prob[i]),
                "cause": cause_label[i]
            })
        return {"predictions": results}
    except Exception as e:
        return {"error": str(e)}
