from flask import Flask
import logging
from datetime import datetime
from config import *

class FlaskAppModel():

    def config_flask_app(self, logger: logging.Logger) -> Flask:
        app = Flask(
            __name__,
            template_folder=PAGES_DIR,  # Use pages directory for modern templates
            static_folder=STATIC_DIR
        )

        """Configure the Flask app with necessary settings"""
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        app.config['JSON_SORT_KEYS'] = False
        # Add other configurations as needed
        
        # Custom template filter for datetime formatting
        @app.template_filter('datetimeformat')
        def datetimeformat(value):
            if value is None:
                return 'Unknown'
            try:
                # If it's a timestamp (float), convert to datetime
                if isinstance(value, (int, float)):
                    dt = datetime.fromtimestamp(value)
                    return dt.strftime('%m/%d/%Y %H:%M:%S')
                else:
                    return str(value)
            except:
                return str(value)

        @app.template_filter('seconds_to_human')
        def seconds_to_human_filter(seconds):
            try:
                seconds = int(seconds)
                if seconds < 60:
                    return f"{seconds}s"
                elif seconds < 3600:
                    return f"{seconds//60}m {seconds%60}s"
                elif seconds < 86400:
                    return f"{seconds//3600}h {(seconds%3600)//60}m"
                else:
                    days = seconds // 86400
                    hours = (seconds % 86400) // 3600
                    return f"{days}d {hours}h"
            except Exception:
                return str(seconds)

        @app.template_filter('dateformat')
        def dateformat(value):
            if value is None:
                return 'Unknown'
            try:
                # If it's a timestamp (float), convert to datetime
                if isinstance(value, (int, float)):
                    dt = datetime.fromtimestamp(value)
                    return dt.strftime('%m/%d/%Y')
                else:
                    return str(value)
            except:
                return str(value)        
        
        # Create custom HTTP request logger
        http_logger = logging.getLogger("octopus_server.http")
        # Custom middleware to log HTTP requests in standardized format
        #@app.before_request
        def log_request_info():
            """Log HTTP request in standardized format"""
            from flask import request
            http_logger.info(f"{request.remote_addr} {request.method} {request.path} {request.environ.get('SERVER_PROTOCOL', 'HTTP/1.1')}")

        # Register the after_request handler
        @app.after_request
        def after_request(response):
            # Log the request with response status in standardized format
            from flask import request
            http_logger.info(f"{request.remote_addr} {request.method} {request.path} -> {response.status_code} {response.status}")
            return response


        # Configure Flask secret key for sessions (required for authentication)
        app.secret_key = 'octopus-secret-key-change-in-production'
        # Configure session settings for proper persistence
        app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

        return app
    