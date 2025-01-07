from flask import Flask, request, render_template, redirect, url_for
import numpy as np
from keras.models import load_model
import os
from io import BytesIO
from PIL import Image
import base64
import keras

from app import create_app

from flask import Blueprint
import logging
access_logger = logging.getLogger('access')
error_logger = logging.getLogger('error')

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


MODEL_PATH = os.path.join("models", "model.keras")

model = load_model(MODEL_PATH)
model.make_predict_function()

def model_predict(img, model):
    x = keras.utils.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0

    preds = model.predict(x)
    return preds


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/result', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
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

        preds = model_predict(img, model)
        result = "Chien" if preds[0][0] < 0.5 else "Chat"
        
        return render_template('result.html', result=result, image_base64_front=base64_img)
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
