from logging.config import dictConfig
from flask import Flask

def create_app(test_config=None):
    # app configuration
    app = Flask(__name__, instance_relative_config=False)

    # load the instance config, if it exists, when not testing
    
    app.config.from_pyfile('config.py')

    # ensure the instance folder exists
    dictConfig(app.config["LOGGING"])
    
    return app