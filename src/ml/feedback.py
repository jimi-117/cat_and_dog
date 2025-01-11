import os
import json
from datetime import datetime
import logging
from src.config.base_config import Config
from src.monitoring.metrics import log_feedback
import base64

logger = logging.getLogger('app')

class FeedbackProcessor:
    def __init__(self):
        self.feedback_dir = Config.FEEDBACK_FOLDER
        os.makedirs(os.path.join(self.feedback_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(self.feedback_dir, 'metadata'), exist_ok=True)

    def save_feedback_image(self, image_data: str, feedback_id: str) -> str:
        """save feedback image"""
        try:
            image_bytes = base64.b64decode(image_data)
            image_path = os.path.join(self.feedback_dir, 'images', f'{feedback_id}.png')
            
            with open(image_path, 'wb') as f:
                f.write(image_bytes)
            
            return image_path
        except Exception as e:
            logger.error(f"Error saving feedback image: {str(e)}")
            raise

    def save_feedback_metadata(self, feedback_data: dict, image_path: str, feedback_id: str):
        """save feedback metadata"""
        try:
            metadata = {
                'id': feedback_id,
                'timestamp': datetime.now().isoformat(),
                'prediction': feedback_data['prediction'],
                'feedback_type': feedback_data['feedback_type'],
                'image_path': image_path,
                'confidence': feedback_data.get('confidence', None)
            }
            
            metadata_path = os.path.join(self.feedback_dir, 'metadata', f'{feedback_id}.json')
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving feedback metadata: {str(e)}")
            raise

    @log_feedback
    def process_feedback(self, feedback_data: dict) -> dict:
        """process user feedback"""
        try:
            feedback_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            
            # save image
            image_path = self.save_feedback_image(
                feedback_data['image'],
                feedback_id
            )
            
            # save metadata
            self.save_feedback_metadata(
                feedback_data,
                image_path,
                feedback_id
            )
            
            # evaluate feedback
            is_correct = (
                feedback_data['feedback_type'] == 'accept' and
                feedback_data['prediction'] in Config.CLASS_NAMES
            )
            
            return {
                'feedback_type': feedback_data['feedback_type'],
                'prediction_class': feedback_data['prediction'],
                'is_correct': is_correct
            }
            
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            raise

# instantiate singleton feedback processor
feedback_processor = FeedbackProcessor()