from logging.config import dictConfig
from flask import Flask

def create_app(test_config=None):
    # app configuration
    app = Flask(__name__, instance_relative_config=False)
    
    app.config.from_pyfile('config.py')

    dictConfig(app.config["LOGGING"])
    
    return app