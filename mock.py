from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

print("Loading model...")
model_package = joblib.load('biogas_anomaly_model.pkl')
print("Model loaded successfully!")

@app.route('/', methods=['GET'])
def home():
    return "Biogas Anomaly Detection API is running. Send POST requests to /predict"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from request
        data = request.json
        print(f"Received request with data: {data}")
        
        # Get the feature names from the model package
        feature_columns = model_package['feature_columns']
        
        # Ensure the input has all required features
        input_data = np.array([data.get(feature, 0) for feature in feature_columns]).reshape(1, -1)
        
        # Scale the input data using the scaler from model_package
        scaled_data = model_package['scaler'].transform(input_data)
        
        # Apply feature selection if it was used during training
        if 'feature_selector' in model_package:
            scaled_data = model_package['feature_selector'].transform(scaled_data)
        
        # Make prediction
        prediction = model_package['model'].predict(scaled_data)
        
        # Extract anomaly prediction (first column of prediction)
        anomaly_score = float(prediction[0][0])  # Convert to float for JSON serialization
        anomaly_result = int(anomaly_score >= 0.5)
        
        # Extract cause prediction (second column of prediction)
        cause_id = int(np.round(prediction[0][1]))
        cause = model_package['cause_encoder'].inverse_transform([cause_id])[0]
        
        # Create response
        result = {
            'anomaly_detected': bool(anomaly_result),
            'anomaly_score': anomaly_score,
            'cause': str(cause),
            'cause_id': cause_id
        }
        
        print(f"Prediction result: {result}")
        return jsonify(result)
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error during prediction: {error_msg}")
        return jsonify({"error": error_msg})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting local model server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)