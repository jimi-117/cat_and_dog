import pytest
from src.monitoring.metrics import MetricsCollector
import prometheus_client

def test_metrics_initialization():
    """test metrics initialization"""
    MetricsCollector.initialize(port=8001)
    
    # check that the metrics are registered
    metrics = prometheus_client.REGISTRY.collect()
    metric_names = [metric.name for metric in metrics]
    
    expected_metrics = [
        'model_predictions_total',
        'model_prediction_latency_seconds',
        'model_prediction_confidence',
        'application_errors_total',
        'user_feedback_total',
        'model_accuracy'
    ]
    
    for metric in expected_metrics:
        assert any(metric in name for name in metric_names)

def test_prediction_tracking():
    """test prediction metrics tracking"""
    # get initial prediction count
    initial_predictions = prometheus_client.REGISTRY.get_sample_value(
        'model_predictions_total_total',
        {'class_name': 'Chat'}
    ) or 0
    
    # track a new prediction
    MetricsCollector.track_prediction('Chat', 0.95, 0.1)
    
    # get the new prediction count
    new_predictions = prometheus_client.REGISTRY.get_sample_value(
        'model_predictions_total_total',
        {'class_name': 'Chat'}
    )
    
    # check metrics
    assert new_predictions == initial_predictions + 1

def test_error_tracking():
    """test error tracking"""
    # track an error
    MetricsCollector.track_error('TestError')
    
    # check the error count
    error_count = prometheus_client.REGISTRY.get_sample_value(
        'application_errors_total_total',
        {'error_type': 'TestError'}
    )
    
    assert error_count > 0

def test_feedback_tracking():
    """test feedback tracking"""
    MetricsCollector.track_feedback(
        feedback_type='accept',
        prediction_class='Chat',
        is_correct=True
    )
    
    # check the feedback counter
    feedback_count = prometheus_client.REGISTRY.get_sample_value(
        'user_feedback_total_total',
        {'feedback_type': 'accept', 'prediction_class': 'Chat'}
    )
    
    assert feedback_count > 0