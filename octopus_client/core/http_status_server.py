"""
🌐 HTTP STATUS SERVER
=====================

Simple HTTP server for displaying client status information.
"""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from core.status_manager import StatusManager

class StatusHandler(BaseHTTPRequestHandler):
    """HTTP handler to show latest scheduled task info"""
    
    def __init__(self, status_manager: StatusManager, *args, **kwargs):
        self.status_manager = status_manager
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = self.status_manager.get_status_html()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

class HTTPStatusServer:
    """Manages the HTTP status server"""
    
    def __init__(self, host: str, port: int, status_manager: StatusManager, logger):
        self.host = host
        self.port = port
        self.status_manager = status_manager
        self.logger = logger
        self.server = None
    
    def start(self):
        """Start the status server in a background thread"""
        def handler_factory(*args, **kwargs):
            return StatusHandler(self.status_manager, *args, **kwargs)
        
        try:
            self.server = HTTPServer((self.host, self.port), handler_factory)
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
            self.logger.info(f"Status page available at http://{self.host}:{self.port}/status")
        except Exception as e:
            self.logger.error(f"Failed to start status server: {e}")
    
    def stop(self):
        """Stop the status server"""
        if self.server:
            self.server.shutdown()
            self.server = None
            self.logger.info("Status server stopped")
