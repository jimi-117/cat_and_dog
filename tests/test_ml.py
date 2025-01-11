import pytest
from src.ml.predict import model_predictor
from src.ml.feedback import feedback_processor
from PIL import Image
import numpy as np

def test_image_preprocessing():
    """test image preprocessing"""
    # Create a simple test image
    test_image = Image.new('RGB', (256, 256), color='red')
    
    # Preprocess the image
    processed = model_predictor.preprocess_image(test_image)
    
    # Validation
    assert processed.shape == (1, 128, 128, 3)  # Check the shape
    assert np.max(processed) <= 1.0  #  Check the range
    assert np.min(processed) >= 0.0

def test_prediction_format():
    """test prediction format"""
    # Create a simple test image
    test_image = Image.new('RGB', (128, 128), color='red')
    
    # Get the prediction
    result, confidence = model_predictor.predict(test_image)
    
    # Validation
    assert result in ['Chat', 'Chien']
    assert 0 <= confidence <= 1

def test_feedback_processing():
    """test feedback processing"""
    feedback_data = {
        'prediction': 'Chat',
        'feedback_type': 'accept',
        'image': 'base64_encoded_image_data',
        'confidence': 0.95
    }
    
    result = feedback_processor.process_feedback(feedback_data)
    
    assert 'feedback_type' in result
    assert 'prediction_class' in result
    assert 'is_correct' in result

@pytest.mark.parametrize("feedback_type,prediction,expected_correct", [
    ('accept', 'Chat', True),
    ('reject', 'Chat', False),
    ('accept', 'Chien', True),
    ('reject', 'Chien', False),
])
def test_feedback_evaluation(feedback_type, prediction, expected_correct):
    """test feedback evaluation"""
    feedback_data = {
        'prediction': prediction,
        'feedback_type': feedback_type,
        'image': 'base64_encoded_image_data',
        'confidence': 0.95
    }
    
    result = feedback_processor.process_feedback(feedback_data)
    assert result['is_correct'] == expected_correct