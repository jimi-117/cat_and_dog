from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import numpy as np
from keras.models import load_model
import os
from io import BytesIO
from PIL import Image
import base64
import keras

from app import create_app

# logging
from flask import Blueprint
import logging
access_logger = logging.getLogger('access')
error_logger = logging.getLogger('error')

# mlflow
import mlflow
import mlflow.keras

mlflow.set_tracking_uri("file:.mlruns")

# monotoring
from .monitoring import prediction_requests, prediction_errors, prediction_latency


#--------------------------------------------------------------------------------#
# app settings
#--------------------------------------------------------------------------------#

app = create_app()

def headers_to_string(headers):
    return ", ".join(f"{key}: {value}" for key, value in headers.items())

@app.before_request
def log_request_info():
    request_info = (
        f"Request: method={request.method}, url={request.url}, "
        # f"headers=[{headers_to_string(request.headers)}], "
        # f"body={request.get_data(as_text=True)}"
    )
    access_logger.info(request_info)
    
@app.after_request
def log_response_info(response):
    response_info = f"Response: status={response.status}, headers=[{headers_to_string(response.headers)}]"
    access_logger.info(response_info)
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    error_logger.error(f"Exception occurred: {e}", exc_info=True)
    return "An error occurred", 500

index_bp = Blueprint("index", __name__, url_prefix="/")
logger = logging.getLogger('app')

@index_bp.route("/", methods=["GET", "POST"])
def index():
    logger.debug("Return to index page")
    return render_template("index.html", page_title="TOP")


#--------------------------------------------------------------------------------#

# loading model
MODEL_PATH = os.path.join("models", "model.keras")
model = None

try:
    model = load_model(MODEL_PATH)
    model.make_predict_function()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    

def model_predict(img, model):
    if model is None:
        raise FileNotFoundError("Model not loaded")
    x = keras.utils.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0
    
    # measure latency
    with prediction_latency.time():
        preds = model.predict(x)
    
    return preds


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # increasing req count
        prediction_requests.inc()
        
        f = request.files['file']
        buffered_img = BytesIO(f.read())
        img = Image.open(buffered_img)
        
        # Resize the image to 128x128
        img = img.resize((128, 128))
        # reset buffer and save image to buffer
        buffered_img.seek(0)
        buffered_img.truncate(0)
        img.save(buffered_img, format="JPEG")

        base64_img = base64.b64encode(buffered_img.getvalue()).decode("utf-8")
        
        try:
            preds = model_predict(img, model)
            result = "Chien" if preds[0][0] < 0.5 else "Chat"
        except Exception as e:
            prediction_errors.inc()
            logger.error(f"Prediction error: {e}")
            result = "Error"
        print(result)
        return render_template('result.html', result=result, image_base64_front=base64_img)
    
    return redirect('/')

# endpoint for feedback loop
@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_value = request.form.get("feedback")
    prediction = request.form.get("prediction")
    image_base64 = request.form.get("image")
    
    # decode and save temporarily base64 image
    import time
    timestamp = str(time.time())
    image_data = base64.b64decode(image_base64)
    tmp_filename = f"feedback_image_{timestamp}.jpg"
    with open(tmp_filename, "wb") as f:
        f.write(image_data)

    # logging mlflow
    with mlflow.start_run(run_name="feedback"):
        mlflow.log_param("prediction", prediction)
        mlflow.log_param("feedback", feedback_value)
        mlflow.log_artifact(tmp_filename)
          
    # remove tmp file
    if os.path.exists(tmp_filename):
        os.remove(tmp_filename)
    
    # returning on top when recive the feedback
    return redirect(url_for("home"))

@app.route('/metrics')
def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return generate_latest(), 200 , {'content-type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run()
