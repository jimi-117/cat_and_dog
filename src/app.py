from flask import Flask, request, render_template, redirect, url_for
import numpy as np
from keras.models import load_model
import os
from io import BytesIO
from PIL import Image
import base64
import keras
import time
import json
from datetime import datetime
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, start_http_server
import mlflow
import mlflow.keras
from pathlib import Path
# import logging
# from logging import Formatter, FileHandler, WARNING, ERROR, INFO
# from logging.handlers import SMTPHandler
# from dotenv import load_dotenv

# load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# # Mail handling
# mail_handler = SMTPHandler(
#     mailhost = os.getenv('HOST'),
#     fromaddr = os.getenv('FROM'), # Mail address from which to send mails
#     toaddrs = os.getenv('TO'), # Mail address to send mails
#     subject = 'Application Error'
# )
# mail_handler.setLevel(ERROR)
# app.logger.addHandler(mail_handler)

# Set MLflow tracking URI to a local directory
MLFLOW_TRACKING_DIR = "mlruns"
Path(MLFLOW_TRACKING_DIR).mkdir(exist_ok=True)
mlflow.set_tracking_uri(f"file://{os.path.abspath(MLFLOW_TRACKING_DIR)}")
mlflow.set_experiment("pet_classifier_monitoring")

# Start Prometheus metrics server　　、
try:
    start_http_server(9090)
except OSError as e:
    if "Address already in use" in str(e):
        print("Prometheus metrics server is already running.")
    else:
        raise

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Custom metrics
PREDICTION_REQUEST_COUNT = Counter('model_prediction_requests_total', 'Total number of prediction requests')
PREDICTION_LATENCY = Histogram('model_prediction_latency_seconds', 'Time spent processing prediction')
PREDICTION_CONFIDENCE = Histogram('model_prediction_confidence', 'Model prediction confidence scores', 
                                buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])

MODEL_PATH = 'src/models/model.keras' 
FEEDBACK_DIR = "feedback_data"
Path(FEEDBACK_DIR).mkdir(exist_ok=True)

# Load model
model = load_model(MODEL_PATH)
model.make_predict_function()

def save_feedback(prediction, feedback_value, confidence, image_data):
    """Save feedback data to local storage"""
    timestamp = datetime.now().isoformat()
    feedback_data = {
        "timestamp": timestamp,
        "prediction": prediction,
        "feedback": feedback_value,
        "confidence": float(confidence) if confidence is not None else 0.0,
        "image": image_data
    }
    
    feedback_file = os.path.join(FEEDBACK_DIR, f"feedback_{timestamp}.json")
    with open(feedback_file, 'w') as f:
        json.dump(feedback_data, f)

def model_predict(img, model):
    # Start MLflow run for this prediction
    with mlflow.start_run(nested=True):
        start_time = time.time()
        
        x = keras.utils.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0

        preds = model.predict(x)
        
        # Record metrics
        latency = time.time() - start_time
        confidence = float(abs(preds[0][0] - 0.5) + 0.5)
        print(f'Confidence score : {confidence}')
        # Log metrics to both Prometheus and MLflow
        PREDICTION_LATENCY.observe(latency)
        PREDICTION_CONFIDENCE.observe(confidence)
        
        mlflow.log_metric("prediction_latency", latency)
        mlflow.log_metric("prediction_confidence", confidence)
        
        return preds, confidence

@app.route('/', methods=['GET'])
@metrics.do_not_track()
def home():
    return render_template('index.html')

@app.route('/result', methods=['GET', 'POST'])
@metrics.counter('prediction_requests_total', 'Number of prediction requests')
def upload():
    if request.method == 'POST':
        PREDICTION_REQUEST_COUNT.inc()
        
        f = request.files['file']
        
        buffered_img = BytesIO(f.read())
        img = Image.open(buffered_img)
        img = img.resize((128, 128))
        buffered_img.seek(0)
        buffered_img.truncate(0)
        img.save(buffered_img, format="JPEG")
        base64_img = base64.b64encode(buffered_img.getvalue()).decode("utf-8")

        preds, confidence = model_predict(img, model)
        result = "Chien" if preds[0][0] < 0.5 else "Chat"
        
        # Store prediction info in session for feedback
        request.session = {
            'prediction': result,
            'confidence': confidence,
            'image': base64_img
        }
        
        return render_template('result.html', result=result, image_base64_front=base64_img)
    
    return redirect('/')

@app.route('/feedback', methods=['POST'])
@metrics.counter('feedback_requests_total', 'Number of feedback submissions')
def feedback():
    if request.method == 'POST':
        feedback_value = request.form.get('feedback')
        prediction = request.form.get('prediction')
        image_data = request.form.get('image')
        
        # Start MLflow run for feedback logging
        with mlflow.start_run(nested=True):
            mlflow.log_param("predicted_class", prediction)
            mlflow.log_param("feedback", feedback_value)
            
            # If we have stored confidence from the prediction
            if hasattr(request, 'session') and 'confidence' in request.session:
                confidence = request.session['confidence']
                mlflow.log_metric("prediction_confidence", confidence)
            else:
                confidence = None
            
            # Save feedback data
            save_feedback(prediction, feedback_value, confidence, image_data)
            
            print(f"Received feedback: {feedback_value} for prediction: {prediction}")
    
    return redirect(url_for("home"))

@app.route('/feedback/stats', methods=['GET'])
def feedback_stats():
    """Endpoint to view feedback statistics"""
    stats = {
        'total_feedback': 0,
        'accepted': 0,
        'rejected': 0,
        'accuracy': 0.0
    }
    
    # Calculate feedback statistics
    if os.path.exists(FEEDBACK_DIR):
        for feedback_file in os.listdir(FEEDBACK_DIR):
            if feedback_file.endswith('.json'):
                with open(os.path.join(FEEDBACK_DIR, feedback_file)) as f:
                    data = json.load(f)
                    stats['total_feedback'] += 1
                    if data['feedback'] == 'accept':
                        stats['accepted'] += 1
                    else:
                        stats['rejected'] += 1
    
    if stats['total_feedback'] > 0:
        stats['accuracy'] = (stats['accepted'] / stats['total_feedback']) * 100
    
    return render_template('feedback_stats.html', stats=stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)