import numpy as np
from keras.models import load_model
from PIL import Image
import base64
from io import BytesIO
import os
import logging
from src.config.base_config import Config
from src.monitoring.metrics import monitor_prediction

logger = logging.getLogger('app')

class ModelPredictor:
    def __init__(self):
        self.model = load_model(Config.MODEL_PATH)
        self.model.make_predict_function()
        logger.info("Model loaded successfully")

    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """preprocess image for prediction"""
        try:
            image = image.resize(Config.IMAGE_SIZE)
            x = np.array(image)
            x = np.expand_dims(x, axis=0)
            x = x / 255.0
            return x
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise

    @monitor_prediction
    def predict(self, img_data) -> tuple[str, float]:
        """exec model prediction"""
        try:
            # load image and preprocess
            if isinstance(img_data, BytesIO):
                image = Image.open(img_data)
            else:
                image = img_data

            # prediction
            processed_image = self.preprocess_image(image)
            predictions = self.model.predict(processed_image)
            confidence = float(predictions[0][0])
            
            # result
            result = "Chien" if confidence < Config.CONFIDENCE_THRESHOLD else "Chat"
            
            return result, confidence

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise

    def get_prediction_with_image(self, file) -> tuple[str, str, float]:
        """return pred and encoded image"""
        try:
            # load image
            buffered = BytesIO(file.read())
            image = Image.open(buffered)
            
            # prediction
            result, confidence = self.predict(image)
            
            # encode image
            buffered.seek(0)
            image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return result, image_base64, confidence
            
        except Exception as e:
            logger.error(f"Error processing prediction request: {str(e)}")
            raise

# instantiate singleton model predictor
model_predictor = ModelPredictor()