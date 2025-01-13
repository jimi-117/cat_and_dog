from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import numpy as np
from keras.models import load_model
import os
from io import BytesIO
from PIL import Image
import base64
import keras
import mlflow
import mlflow.keras
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics
import time
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Initialize MLflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("image-classification-monitoring")

def create_app():
    app = Flask(__name__)
    
    # Initialize Prometheus metrics
    metrics = GunicornInternalPrometheusMetrics(app)
    
    # Define custom metrics
    prediction_request_count = metrics.counter(
        'prediction_request_count', 'Number of prediction requests'
    )
    prediction_latency = metrics.histogram(
        'prediction_latency_seconds',
        'Time spent processing prediction'
    )
    prediction_confidence = metrics.histogram(
        'prediction_confidence',
        'Model prediction confidence'
    )
    prediction_class_count = metrics.counter(
        'prediction_class_count',
        'Number of predictions per class',
        labels={'class': ['cat', 'dog']}
    )
    
    # Load model
    MODEL_PATH = os.path.join("models", "model.keras")
    model = load_model(MODEL_PATH)
    model.make_predict_function()
    
    def log_prediction_metrics(true_label, predicted_label, confidence, latency):
        """Log metrics to MLflow"""
        with mlflow.start_run(run_name=f"prediction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            mlflow.log_metrics({
                "prediction_latency": latency,
                "confidence": confidence,
                "correct_prediction": 1 if true_label == predicted_label else 0
            })
            mlflow.log_param("predicted_class", predicted_label)
    
    def model_predict(img, model):
        start_time = time.time()
        
        x = keras.utils.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = x / 255.0
        
        preds = model.predict(x)
        confidence = float(abs(0.5 - preds[0][0]) * 2)  # Convert to 0-1 scale
        predicted_class = "dog" if preds[0][0] < 0.5 else "cat"
        
        # Record metrics
        latency = time.time() - start_time
        prediction_latency.observe(latency)
        prediction_confidence.observe(confidence)
        prediction_class_count.labels(predicted_class=predicted_class).inc()
        
        return predicted_class, confidence, latency, preds[0][0]
    
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')
    
    @app.route('/', methods=['GET'])
    def home():
        return render_template('index.html')
    
    @app.route('/result', methods=['GET', 'POST'])
    @prediction_request_count.count_exceptions()
    def upload():
        if request.method == 'POST':
            f = request.files['file']
            true_label = request.form.get('true_label', None)  # Optional feedback
            
            buffered_img = BytesIO(f.read())
            img = Image.open(buffered_img)
            img = img.resize((128, 128))
            
            buffered_img.seek(0)
            buffered_img.truncate(0)
            img.save(buffered_img, format="JPEG")
            base64_img = base64.b64encode(buffered_img.getvalue()).decode("utf-8")
            
            predicted_class, confidence, latency, raw_pred = model_predict(img, model)
            
            # Log to MLflow if true label is provided
            if true_label:
                log_prediction_metrics(true_label, predicted_class, confidence, latency)
            
            return render_template('result.html',
                                result=predicted_class,
                                confidence=f"{confidence*100:.2f}%",
                                image_base64_front=base64_img)
        
        return redirect('/')
    
    # Endpoint for model performance metrics
    @app.route('/metrics/performance', methods=['GET'])
    def model_performance():
        # Get MLflow metrics for recent predictions
        client = mlflow.tracking.MlflowClient()
        runs = client.search_runs(
            experiment_ids=[mlflow.get_experiment_by_name("image-classification-monitoring").experiment_id],
            max_results=1000
        )
        
        # Calculate aggregate metrics
        correct_predictions = sum(run.data.metrics["correct_prediction"] for run in runs)
        total_predictions = len(runs)
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        avg_latency = sum(run.data.metrics["prediction_latency"] for run in runs) / total_predictions if total_predictions > 0 else 0
        avg_confidence = sum(run.data.metrics["confidence"] for run in runs) / total_predictions if total_predictions > 0 else 0
        
        return {
            "accuracy": accuracy,
            "average_latency": avg_latency,
            "average_confidence": avg_confidence,
            "total_predictions": total_predictions
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)