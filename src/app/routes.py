from flask import Blueprint, request, render_template, redirect, url_for
import logging
from src.ml.predict import model_predictor
from src.ml.feedback import feedback_processor

main_bp = Blueprint('main', __name__)
logger = logging.getLogger('app')

@main_bp.before_request
def log_request_info():
    """logging request information"""
    logger.info(f"Request: method={request.method}, url={request.url}")

@main_bp.route('/', methods=['GET'])
def home():
    """render home page"""
    return render_template('index.html')

@main_bp.route('/result', methods=['GET', 'POST'])
def upload():
    """upload image and get prediction"""
    if request.method == 'POST':
        try:
            # get file from request
            if 'file' not in request.files:
                logger.error("No file part in request")
                return redirect(url_for('main.home'))
                
            file = request.files['file']
            if not file:
                logger.error("No file selected")
                return redirect(url_for('main.home'))
            
            # process prediction
            result, image_base64, confidence = model_predictor.get_prediction_with_image(file)
            logger.info(f"Prediction completed: {result} with confidence {confidence}")
            
            return render_template('result.html',
                                 result=result,
                                 image_base64_front=image_base64,
                                 confidence=confidence)
                                 
        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            return render_template('error.html', error=str(e))
    
    return redirect(url_for('main.home'))

@main_bp.route('/feedback', methods=['POST'])
def feedback():
    """process user feedback"""
    try:
        feedback_data = {
            'prediction': request.form['prediction'],
            'feedback_type': request.form['feedback'],
            'image': request.form['image'],
            'confidence': float(request.form.get('confidence', 0))
        }
        
        feedback_processor.process_feedback(feedback_data)
        logger.info(f"Feedback processed: {feedback_data['feedback_type']} for prediction {feedback_data['prediction']}")
        
        return redirect(url_for('main.home'))
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return render_template('error.html', error=str(e))