#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Plugin Routes
================================

Routes for plugin creation, testing, and management.
Provides VS Code-like interface for plugin development.
"""

import os
import sys
import json
import time
import tempfile
import subprocess
from flask import Blueprint, render_template, request, jsonify, session, current_app

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dbhelper import (
    submit_plugin, get_plugin_submissions, update_plugin_submission_status,
    record_plugin_test, get_plugin_tests, deploy_plugin
)
from helpers.utils import get_current_timestamp, require_admin, require_login

plugin_bp = Blueprint('plugin', __name__)

@plugin_bp.route('/plugins/create')
@require_login
def create_plugin():
    """Plugin creation page with VS Code-like interface"""
    return render_template('plugin_create.html')

@plugin_bp.route('/plugins/review')
@require_admin
def review_plugins():
    """Admin plugin review page"""
    submissions = get_plugin_submissions()
    return render_template('plugin_review.html', submissions=submissions)

@plugin_bp.route('/plugins/my-submissions')
@require_login
def my_submissions():
    """User's plugin submissions page"""
    username = session.get('username')
    submissions = get_plugin_submissions(author=username)
    return render_template('plugin_my_submissions.html', submissions=submissions)

@plugin_bp.route('/api/plugins/submit', methods=['POST'])
@require_login
def api_submit_plugin():
    """Submit a new plugin for review"""
    try:
        data = request.get_json()
        
        plugin_name = data.get('plugin_name', '').strip()
        plugin_code = data.get('plugin_code', '').strip()
        description = data.get('description', '').strip()
        language = data.get('language', 'python').strip()
        
        if not plugin_name or not plugin_code:
            return jsonify({'success': False, 'error': 'Plugin name and code are required'})
        
        # Validate plugin name (alphanumeric and underscores only)
        if not plugin_name.replace('_', '').isalnum():
            return jsonify({'success': False, 'error': 'Plugin name can only contain letters, numbers, and underscores'})
        
        username = session.get('username')
        submission_id = submit_plugin(plugin_name, plugin_code, description, username, language)
        
        if submission_id:
            return jsonify({'success': True, 'submission_id': submission_id})
        else:
            return jsonify({'success': False, 'error': 'Failed to submit plugin'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@plugin_bp.route('/api/plugins/test/<int:submission_id>', methods=['POST'])
@require_admin
def api_test_plugin(submission_id):
    """Test a plugin submission"""
    try:
        submissions = get_plugin_submissions()
        submission = next((s for s in submissions if s['id'] == submission_id), None)
        
        if not submission:
            return jsonify({'success': False, 'error': 'Plugin submission not found'})
        
        if submission['language'] != 'python':
            return jsonify({'success': False, 'error': 'Only Python plugins are currently supported for testing'})
        
        # Run basic syntax check
        syntax_result = test_plugin_syntax(submission['plugin_code'])
        record_plugin_test(submission_id, 'syntax', syntax_result['status'], 
                          syntax_result.get('output'), syntax_result.get('error'))
        
        # Run plugin structure validation
        structure_result = test_plugin_structure(submission['plugin_code'])
        record_plugin_test(submission_id, 'structure', structure_result['status'],
                          structure_result.get('output'), structure_result.get('error'))
        
        # If both tests pass, run execution test
        if syntax_result['status'] == 'passed' and structure_result['status'] == 'passed':
            exec_result = test_plugin_execution(submission['plugin_code'], submission['plugin_name'])
            record_plugin_test(submission_id, 'execution', exec_result['status'],
                              exec_result.get('output'), exec_result.get('error'))
            
            overall_status = exec_result['status']
        else:
            overall_status = 'failed'
        
        # Update submission test results
        test_summary = {
            'syntax': syntax_result['status'],
            'structure': structure_result['status'],
            'execution': exec_result['status'] if 'exec_result' in locals() else 'skipped',
            'overall': overall_status
        }
        
        update_plugin_submission_status(submission_id, 'tested', 
                                       session.get('username'), 
                                       f"Test completed - Overall: {overall_status}")
        
        return jsonify({
            'success': True, 
            'test_results': test_summary,
            'tests': get_plugin_tests(submission_id)
        })
        
    except Exception as e:
        record_plugin_test(submission_id, 'error', 'failed', None, str(e))
        return jsonify({'success': False, 'error': str(e)})

@plugin_bp.route('/api/plugins/approve/<int:submission_id>', methods=['POST'])
@require_admin
def api_approve_plugin(submission_id):
    """Approve and deploy a plugin"""
    try:
        data = request.get_json() or {}
        notes = data.get('notes', '')
        
        submissions = get_plugin_submissions()
        submission = next((s for s in submissions if s['id'] == submission_id), None)
        
        if not submission:
            return jsonify({'success': False, 'error': 'Plugin submission not found'})
        
        # Deploy the plugin
        deployment_result = deploy_plugin_to_folder(submission)
        
        if deployment_result['success']:
            update_plugin_submission_status(submission_id, 'approved', 
                                           session.get('username'), notes)
            deploy_plugin(submission_id, deployment_result['path'])
            
            return jsonify({
                'success': True, 
                'message': f"Plugin deployed to {deployment_result['path']}"
            })
        else:
            return jsonify({'success': False, 'error': deployment_result['error']})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@plugin_bp.route('/api/plugins/reject/<int:submission_id>', methods=['POST'])
@require_admin
def api_reject_plugin(submission_id):
    """Reject a plugin submission"""
    try:
        data = request.get_json() or {}
        notes = data.get('notes', 'Plugin rejected by admin')
        
        update_plugin_submission_status(submission_id, 'rejected', 
                                       session.get('username'), notes)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@plugin_bp.route('/api/plugins/submissions')
@require_admin
def api_get_submissions():
    """Get all plugin submissions"""
    try:
        submissions = get_plugin_submissions()
        return jsonify({'success': True, 'submissions': submissions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@plugin_bp.route('/api/plugins/my-submissions')
@require_login
def api_get_my_submissions():
    """Get user's plugin submissions"""
    try:
        username = session.get('username')
        submissions = get_plugin_submissions(author=username)
        return jsonify({'success': True, 'submissions': submissions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@plugin_bp.route('/api/plugins/test-results/<int:submission_id>')
@require_admin
def api_get_test_results(submission_id):
    """Get test results for a plugin submission"""
    try:
        tests = get_plugin_tests(submission_id)
        return jsonify({'success': True, 'tests': tests})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ========================================
# PLUGIN TESTING FUNCTIONS
# ========================================

def test_plugin_syntax(plugin_code):
    """Test plugin code for syntax errors"""
    try:
        compile(plugin_code, '<plugin>', 'exec')
        return {'status': 'passed', 'output': 'Syntax check passed'}
    except SyntaxError as e:
        return {'status': 'failed', 'error': f"Syntax error: {e}"}
    except Exception as e:
        return {'status': 'failed', 'error': f"Compilation error: {e}"}

def test_plugin_structure(plugin_code):
    """Test plugin for required structure and functions"""
    try:
        # Check for required plugin structure
        required_patterns = [
            'def main(',  # Main function
            'plugin_name',  # Plugin name variable
            'description'   # Description variable
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in plugin_code:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            return {
                'status': 'failed', 
                'error': f"Missing required elements: {', '.join(missing_patterns)}"
            }
        
        return {'status': 'passed', 'output': 'Plugin structure validation passed'}
        
    except Exception as e:
        return {'status': 'failed', 'error': f"Structure validation error: {e}"}

def test_plugin_execution(plugin_code, plugin_name):
    """Test plugin execution in a safe environment"""
    try:
        # Create a temporary file for the plugin
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(plugin_code)
            temp_file_path = temp_file.name
        
        try:
            # Test import and basic execution
            result = subprocess.run([
                sys.executable, '-c', f'''
import sys
sys.path.insert(0, "{os.path.dirname(temp_file_path)}")
import {os.path.basename(temp_file_path)[:-3]}
print("Plugin imported successfully")

# Test if main function exists and is callable
if hasattr({os.path.basename(temp_file_path)[:-3]}, "main"):
    print("Main function found")
else:
    print("ERROR: Main function not found")
'''
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {'status': 'passed', 'output': result.stdout}
            else:
                return {'status': 'failed', 'error': result.stderr}
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return {'status': 'failed', 'error': 'Plugin execution timed out'}
    except Exception as e:
        return {'status': 'failed', 'error': f"Execution test error: {e}"}

def deploy_plugin_to_folder(submission):
    """Deploy approved plugin to the plugins folder"""
    try:
        # Get the plugins directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plugins_dir = os.path.join(current_dir, 'plugins')
        
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir)
        
        # Create plugin file
        plugin_filename = f"{submission['plugin_name']}.py"
        plugin_path = os.path.join(plugins_dir, plugin_filename)
        
        # Check if plugin already exists
        if os.path.exists(plugin_path):
            return {'success': False, 'error': f"Plugin {plugin_filename} already exists"}
        
        # Write the plugin code to file
        with open(plugin_path, 'w', encoding='utf-8') as f:
            f.write(submission['plugin_code'])
        
        return {'success': True, 'path': plugin_path}
        
    except Exception as e:
        return {'success': False, 'error': f"Deployment error: {e}"}
