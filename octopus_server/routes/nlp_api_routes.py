"""
🧠 NLP API ROUTES
================

Flask routes for natural language processing APIs.
"""

from flask import request, jsonify
from performance_monitor import time_request

def register_nlp_api_routes(app, cache, logger):
    """Register NLP API routes with the Flask app"""

    @app.route("/api/nlp-parse", methods=["POST"])
    @time_request("nlp-parse")
    def api_nlp_parse():
        """API endpoint to parse natural language and convert to task definition"""
        try:
            from nlp_processor import get_nlp_processor
            
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({"error": "Text parameter required"}), 400
            
            text = data['text'].strip()
            if not text:
                return jsonify({"error": "Text cannot be empty"}), 400
            
            # Get NLP processor instance
            nlp_processor = get_nlp_processor()
            
            if not nlp_processor.is_available():
                return jsonify({
                    "error": "NLP processor not available. Install spaCy with: pip install spacy && python -m spacy download en_core_web_sm"
                }), 503
            
            # Parse the natural language input
            result = nlp_processor.parse_natural_language(text)
            
            if not result.get("success"):
                return jsonify(result), 400
            
            logger.info(f"NLP parsed '{text}' with confidence {result.get('confidence', 0):.2f}")
            return jsonify(result)
            
        except ImportError:
            return jsonify({
                "error": "NLP processor module not found. Ensure nlp_processor.py is present."
            }), 500
        except Exception as e:
            logger.error(f"Error in NLP parsing: {e}")
            return jsonify({"error": "Internal server error"}), 500
