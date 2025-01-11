import pytest
from src.monitoring.metrics import MetricsCollector

def test_home_page(client):
    """test home page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Classification Chien ou Chat' in response.data

def test_prediction_endpoint(client, test_image):
    """test prediction endpoint"""
    response = client.post(
        '/result',
        data={'file': (test_image, 'test.png')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    assert b'Prediction' in response.data
    assert any(x in response.data for x in [b'Chat', b'Chien'])

def test_feedback_endpoint(client, test_image_base64):
    """test feedback endpoint"""
    response = client.post(
        '/feedback',
        data={
            'prediction': 'Chat',
            'feedback': 'accept',
            'image': test_image_base64,
            'confidence': 0.95
        }
    )
    assert response.status_code == 302  # redirect to home

def test_error_handling(client):
    """test error handling"""
    # 404 page
    response = client.get('/nonexistent')
    assert response.status_code == 404
    
    # 500 page
    response = client.post('/result', data={})
    assert response.status_code == 302  # redirect to home