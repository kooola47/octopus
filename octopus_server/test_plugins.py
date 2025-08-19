#!/usr/bin/env python3
"""
Test plugin templates
"""
from main import app
from flask import render_template

with app.app_context():
    try:
        render_template('plugin_my_submissions.html', submissions=[])
        print('✅ plugin_my_submissions.html renders successfully')
    except Exception as e:
        print(f'❌ Error rendering plugin_my_submissions.html: {e}')
    
    try:
        render_template('plugin_create.html')
        print('✅ plugin_create.html renders successfully')
    except Exception as e:
        print(f'❌ Error rendering plugin_create.html: {e}')
    
    try:
        render_template('plugin_review.html', submissions=[])
        print('✅ plugin_review.html renders successfully')
    except Exception as e:
        print(f'❌ Error rendering plugin_review.html: {e}')
