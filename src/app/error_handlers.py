from flask import render_template
import logging
from src.monitoring.metrics import MetricsCollector

logger = logging.getLogger('error')

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        logger.error(f"404 error: {error}")
        MetricsCollector.track_error("404_NotFound")
        return render_template('error.html', error="Page not found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {error}")
        MetricsCollector.track_error("500_InternalServer")
        return render_template('error.html', error="Internal server error"), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        MetricsCollector.track_error(error.__class__.__name__)
        return render_template('error.html', 
                             error="An unexpected error occurred"), 500