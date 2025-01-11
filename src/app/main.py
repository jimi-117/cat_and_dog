from flask import Flask
from logging.config import dictConfig
from src.config.logging_config import LOGGING
from src.monitoring.metrics import MetricsCollector
import logging

def create_app(test_config=None):
    # Initialize logging
    dictConfig(LOGGING)
    logger = logging.getLogger('app')
    
    # Create Flask app
    app = Flask(__name__, 
                static_folder='../../static',
                template_folder='../../templates')
    
    if test_config is None:
        app.config.from_object('src.config.base_config.Config')
    else:
        app.config.update(test_config)
    
    # Initialize monitoring
    MetricsCollector.initialize(app.config['PROMETHEUS_PORT'])
    logger.info("Monitoring initialized")
    
    # Register blueprints
    from src.app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Register error handlers
    from src.app.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)