from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import logging
from functools import wraps

# Prometheus metrics
PREDICTION_COUNTER = Counter(
    'model_predictions_total',
    'Total number of predictions made',
    ['class_name']
)

PREDICTION_LATENCY = Histogram(
    'model_prediction_latency_seconds',
    'Time spent processing prediction',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

MODEL_CONFIDENCE = Histogram(
    'model_prediction_confidence',
    'Confidence scores of predictions',
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9]
)

ERROR_COUNTER = Counter(
    'application_errors_total',
    'Total number of application errors',
    ['error_type']
)

FEEDBACK_COUNTER = Counter(
    'user_feedback_total',
    'Total number of user feedback received',
    ['feedback_type', 'prediction_class']
)

MODEL_ACCURACY = Gauge(
    'model_accuracy',
    'Model accuracy based on user feedback'
)

class MetricsCollector:
    @staticmethod
    def initialize(port=8000):
        """Initialize Prometheus metrics server"""
        start_http_server(port)
        logger = logging.getLogger('app')
        logger.info(f"Metrics server started on port {port}")

    @staticmethod
    def track_prediction(class_name: str, confidence: float, duration: float):
        """Track prediction metrics"""
        PREDICTION_COUNTER.labels(class_name=class_name).inc()
        PREDICTION_LATENCY.observe(duration)
        MODEL_CONFIDENCE.observe(confidence)

    @staticmethod
    def track_error(error_type: str):
        """Track error metrics"""
        ERROR_COUNTER.labels(error_type=error_type).inc()

    @staticmethod
    def track_feedback(feedback_type: str, prediction_class: str, is_correct: bool):
        """Track user feedback metrics"""
        FEEDBACK_COUNTER.labels(
            feedback_type=feedback_type,
            prediction_class=prediction_class
        ).inc()
        
        if is_correct:
            current = MODEL_ACCURACY._value.get()
            if current is None:
                current = 0
            MODEL_ACCURACY.set(current + 1)

def monitor_prediction(func):
    """decolator: monitor prediction metrics"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if isinstance(result, tuple):
                prediction, confidence = result
            else:
                prediction, confidence = result, None
                
            MetricsCollector.track_prediction(
                class_name=prediction,
                confidence=confidence if confidence else 0.0,
                duration=duration
            )
            return result
            
        except Exception as e:
            MetricsCollector.track_error(error_type=e.__class__.__name__)
            raise
            
    return wrapper

def log_feedback(func):
    """decolator: log user feedback"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            feedback_data = func(*args, **kwargs)
            MetricsCollector.track_feedback(
                feedback_type=feedback_data.get('feedback_type'),
                prediction_class=feedback_data.get('prediction_class'),
                is_correct=feedback_data.get('is_correct', False)
            )
            return feedback_data
        except Exception as e:
            MetricsCollector.track_error(error_type=e.__class__.__name__)
            raise
            
    return wrapper