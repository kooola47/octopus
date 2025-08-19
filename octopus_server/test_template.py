#!/usr/bin/env python3
"""
Test template syntax
"""
from flask import Flask

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

with app.app_context():
    with open('pages/plugin_my_submissions.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Test template compilation
    app.jinja_env.from_string(template)
    print('Template syntax is valid!')
