import pytest
from src.app.main import create_app
from PIL import Image
import numpy as np
import io
import base64

@pytest.fixture
def app():
    """app for testing"""
    app = create_app({
        'TESTING': True,
        'PROMETHEUS_PORT': 8001  # Use a different port for testing
    })
    return app

@pytest.fixture
def client(app):
    """client for testing"""
    return app.test_client()

@pytest.fixture
def test_image():
    """create a simple test image"""
    # Create a simple test image
    img = Image.new('RGB', (128, 128), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

@pytest.fixture
def test_image_base64(test_image):
    """Base64 encode image"""
    return base64.b64encode(test_image.getvalue()).decode('utf-8')