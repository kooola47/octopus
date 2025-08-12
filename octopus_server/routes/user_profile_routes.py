#!/usr/bin/env python3
"""
👤 USER PROFILE ROUTES
====================

Flask routes for managing user profile parameters.
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
import time
import logging
from user_parameters import UserParametersManager, DEFAULT_CATEGORIES, EXAMPLE_PARAMETERS
from dbhelper import get_db_connection

logger = logging.getLogger(__name__)

# Create blueprint
user_profile_bp = Blueprint('user_profile', __name__)

def get_current_user():
    """Get current logged-in user from session"""
    return session.get('username')

# Initialize user parameters manager
def get_user_params_manager():
    """Get user parameters manager instance"""
    class DBHelper:
        def get_connection(self):
            return get_db_connection()
    
    return UserParametersManager(DBHelper())

def get_cache_manager():
    """Get cache manager instance"""
    try:
        from cache import CacheManager
        return CacheManager()
    except ImportError:
        # Create a simple in-memory cache if cache module not available
        class SimpleCacheManager:
            def __init__(self):
                self.cache = {}
            
            def get(self, key):
                return self.cache.get(key)
            
            def set(self, key, value, ttl=None):
                self.cache[key] = value
                return True
        
        return SimpleCacheManager()

@user_profile_bp.route('/profile')
def profile():
    """User profile management page"""
    username = get_current_user()
    if not username:
        return redirect(url_for('login'))
    
    try:
        params_manager = get_user_params_manager()
        
        # Get user parameters organized by category
        parameters = params_manager.get_user_parameters(username)
        categories = params_manager.get_categories(username)
        
        # Initialize default categories if none exist
        if not categories:
            for cat_name, cat_info in DEFAULT_CATEGORIES.items():
                params_manager.set_category(
                    username, cat_name, cat_info['display_name'],
                    cat_info['description'], cat_info['icon'], cat_info['sort_order']
                )
            categories = params_manager.get_categories(username)
        
        # Calculate stats
        total_parameters = sum(len(params) for params in parameters.values()) if parameters else 0
        sensitive_count = 0
        for category_params in parameters.values():
            for param_info in category_params.values():
                if param_info.get('is_sensitive', False):
                    sensitive_count += 1
        
        return render_template('user_profile.html', 
                             parameters=parameters, 
                             categories=categories,
                             total_parameters=total_parameters,
                             sensitive_count=sensitive_count,
                             cache_status="Active",
                             example_params=EXAMPLE_PARAMETERS)
    
    except Exception as e:
        logger.error(f"Error loading profile for {username}: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash(f"Error loading profile: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@user_profile_bp.route('/api/profile/parameters', methods=['GET'])
def get_parameters():
    """API endpoint to get user parameters"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        params_manager = get_user_params_manager()
        category = request.args.get('category')
        
        parameters = params_manager.get_user_parameters(username, category)
        return jsonify({"success": True, "parameters": parameters})
    
    except Exception as e:
        logger.error(f"Error getting parameters for {username}: {e}")
        return jsonify({"error": str(e)}), 500

@user_profile_bp.route('/api/profile/parameters', methods=['POST'])
def set_parameter():
    """API endpoint to set a user parameter"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        
        category = data.get('category')
        param_name = data.get('param_name')
        value = data.get('value')
        param_type = data.get('param_type', 'string')
        is_sensitive = data.get('is_sensitive', False)
        description = data.get('description', '')
        
        if not category or not param_name:
            return jsonify({"error": "Category and parameter name required"}), 400
        
        params_manager = get_user_params_manager()
        success = params_manager.set_parameter(
            username, category, param_name, value, 
            param_type, is_sensitive, description
        )
        
        if success:
            # Cache the updated parameters
            cache_manager = get_cache_manager()
            params_manager.cache_user_parameters(username, cache_manager)
            
            return jsonify({"success": True, "message": "Parameter saved successfully"})
        else:
            return jsonify({"error": "Failed to save parameter"}), 500
    
    except Exception as e:
        logger.error(f"Error setting parameter for {username}: {e}")
        return jsonify({"error": str(e)}), 500

@user_profile_bp.route('/api/profile/parameters/<category>/<param_name>', methods=['DELETE'])
def delete_parameter(category, param_name):
    """API endpoint to delete a user parameter"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        params_manager = get_user_params_manager()
        success = params_manager.delete_parameter(username, category, param_name)
        
        if success:
            # Update cache
            cache_manager = get_cache_manager()
            params_manager.cache_user_parameters(username, cache_manager)
            
            return jsonify({"success": True, "message": "Parameter deleted successfully"})
        else:
            return jsonify({"error": "Parameter not found"}), 404
    
    except Exception as e:
        logger.error(f"Error deleting parameter for {username}: {e}")
        return jsonify({"error": str(e)}), 500

@user_profile_bp.route('/api/profile/categories', methods=['GET'])
def get_categories():
    """API endpoint to get parameter categories"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        params_manager = get_user_params_manager()
        categories = params_manager.get_categories(username)
        return jsonify({"success": True, "categories": categories})
    
    except Exception as e:
        logger.error(f"Error getting categories for {username}: {e}")
        return jsonify({"error": str(e)}), 500

@user_profile_bp.route('/api/profile/categories', methods=['POST'])
def create_category():
    """API endpoint to create a new parameter category"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        data = request.get_json()
        
        category_name = data.get('category_name')
        display_name = data.get('display_name')
        description = data.get('description', '')
        icon = data.get('icon', 'fa-cog')
        sort_order = data.get('sort_order', 0)
        
        if not category_name or not display_name:
            return jsonify({"error": "Category name and display name required"}), 400
        
        params_manager = get_user_params_manager()
        success = params_manager.set_category(
            username, category_name, display_name, description, icon, sort_order
        )
        
        if success:
            return jsonify({"success": True, "message": "Category created successfully"})
        else:
            return jsonify({"error": "Failed to create category"}), 500
    
    except Exception as e:
        logger.error(f"Error creating category for {username}: {e}")
        return jsonify({"error": str(e)}), 500

@user_profile_bp.route('/api/profile/cache-refresh', methods=['POST'])
def refresh_cache():
    """API endpoint to refresh parameter cache"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        params_manager = get_user_params_manager()
        
        # Cache all parameters
        cache_manager = get_cache_manager()
        success = params_manager.cache_user_parameters(username, cache_manager)
        
        if success:
            return jsonify({"success": True, "message": "Cache refreshed successfully"})
        else:
            return jsonify({"error": "Failed to refresh cache"}), 500
    
    except Exception as e:
        logger.error(f"Error refreshing cache for {username}: {e}")
        return jsonify({"error": str(e)}), 500

@user_profile_bp.route('/api/profile/export', methods=['GET'])
def export_parameters():
    """API endpoint to export user parameters"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        params_manager = get_user_params_manager()
        parameters = params_manager.get_user_parameters(username)
        categories = params_manager.get_categories(username)
        
        export_data = {
            "username": username,
            "exported_at": time.time(),
            "categories": categories,
            "parameters": parameters
        }
        
        return jsonify({"success": True, "data": export_data})
    
    except Exception as e:
        logger.error(f"Error exporting parameters for {username}: {e}")
        return jsonify({"error": str(e)}), 500

# Plugin helper functions for accessing user parameters
def get_user_parameter(username: str, category: str, param_name: str, default_value=None):
    """Helper function for plugins to get user parameters from cache"""
    try:
        cache_manager = get_cache_manager()
        
        # Try to get from cache first
        cache_key = f"user_params_{username}_{category}"
        cached_params = cache_manager.get(cache_key)
        
        if cached_params and param_name in cached_params:
            return cached_params[param_name]['value']
        
        # Fall back to database
        params_manager = get_user_params_manager()
        return params_manager.get_parameter(username, category, param_name, default_value)
    
    except Exception as e:
        logger.error(f"Error getting user parameter {category}.{param_name} for {username}: {e}")
        return default_value

def get_user_category_parameters(username: str, category: str):
    """Helper function for plugins to get all parameters in a category"""
    try:
        cache_manager = get_cache_manager()
        
        # Try to get from cache first
        cache_key = f"user_params_{username}_{category}"
        cached_params = cache_manager.get(cache_key)
        
        if cached_params:
            return {name: info['value'] for name, info in cached_params.items()}
        
        # Fall back to database
        params_manager = get_user_params_manager()
        all_params = params_manager.get_user_parameters(username, category)
        
        if category in all_params:
            return {name: info['value'] for name, info in all_params[category].items()}
        
        return {}
    
    except Exception as e:
        logger.error(f"Error getting user category {category} for {username}: {e}")
        return {}


@user_profile_bp.route('/profile/guide')
def profile_guide():
    """Show visual guide on how to access profile settings"""
    return render_template('profile_guide.html')
