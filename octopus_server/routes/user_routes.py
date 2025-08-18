#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - User Management Routes
===========================================

User management routes for the Octopus orchestration syst    @app.route('/api/users/<int:user_id>/password', methods=['POST'])
    @login_required
    @admin_required
    def api_update_user_password(user_id):
Handles CRUD operations for users and role management.
"""

from flask import request, render_template, redirect, url_for, flash, jsonify, session
import logging
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dbhelper import (
    get_all_users, get_user_by_id, create_user, update_user, 
    update_user_password, delete_user, toggle_user_status
)
from routes.auth_routes import login_required, admin_required

def get_current_user():
    """Get current user from session"""
    if 'user_id' in session:
        return {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role', 'user')
        }
    return None

logger = logging.getLogger(__name__)

def register_user_routes(app):
    """Register user management routes with Flask app"""
    
    @app.route('/modern/users')
    @login_required
    @admin_required
    def modern_users():
        """User management page"""
        try:
            users = get_all_users()
            current_user = get_current_user()
            
            # Calculate statistics
            stats = {
                'total_users': len(users),
                'admin_users': len([u for u in users if u.get('role') == 'admin']),
                'active_users': len([u for u in users if u.get('is_active')]),
                'inactive_users': len([u for u in users if not u.get('is_active')])
            }
            
            return render_template('modern_users.html', 
                                 users=users, 
                                 stats=stats, 
                                 current_user=current_user, 
                                 current_timestamp=time.time())
        except Exception as e:
            logger.error(f"Error loading users page: {e}")
            flash('Error loading users page', 'error')
            return redirect(url_for('modern_dashboard'))
    
    @app.route('/api/users', methods=['GET'])
    @login_required
    @admin_required
    def api_get_users():
        """Get all users via API"""
        try:
            users = get_all_users()
            # Remove sensitive information
            for user in users:
                user.pop('password_hash', None)
            
            return jsonify({'users': users})
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return jsonify({'error': 'Error retrieving users'}), 500
    
    @app.route('/api/users/<int:user_id>', methods=['GET'])
    @login_required
    @admin_required
    def api_get_user(user_id):
        """Get specific user via API"""
        try:
            user = get_user_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Remove sensitive information
            user.pop('password_hash', None)
            return jsonify({'user': user})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return jsonify({'error': 'Error retrieving user'}), 500
    
    @app.route('/api/users', methods=['POST'])
    @login_required
    @admin_required
    def api_create_user():
        """Create new user via API"""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['username', 'password', 'role']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Validate role
            valid_roles = ['admin', 'user', 'operator', 'viewer']
            if data['role'] not in valid_roles:
                return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
            
            # Validate password length
            if len(data['password']) < 6:
                return jsonify({'error': 'Password must be at least 6 characters long'}), 400
            
            # Create user
            user_data = {
                'username': data['username'],
                'email': data.get('email', ''),
                'password': data['password'],
                'role': data['role'],
                'is_active': data.get('status', 'active') == 'active',
                'full_name': data.get('fullName', ''),
                'user_ident': data.get('userIdent', ''),
                'tags': data.get('tags', '')
            }
            
            user_id = create_user(**user_data)
            if user_id:
                logger.info(f"User {data['username']} created successfully by admin")
                return jsonify({'message': 'User created successfully', 'user_id': user_id})
            else:
                return jsonify({'error': 'Failed to create user. Username may already exist.'}), 400
                
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return jsonify({'error': 'Error creating user'}), 500
    
    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @login_required
    @admin_required
    def api_update_user(user_id):
        """Update user via API"""
        try:
            data = request.get_json()
            current_user = get_current_user()
            
            # Prevent self-demotion from admin
            if (current_user and current_user.get('id') == user_id and 
                current_user.get('role') == 'admin' and 
                data.get('role') != 'admin'):
                return jsonify({'error': 'Cannot demote yourself from admin role'}), 400
            
            # Validate role if provided
            if 'role' in data and data['role'] not in ['admin', 'operator', 'user', 'viewer']:
                return jsonify({'error': 'Invalid role. Must be admin, operator, user, or viewer'}), 400
            
            # Validate status if provided
            if 'status' in data and data['status'] not in ['active', 'inactive']:
                return jsonify({'error': 'Invalid status. Must be active or inactive'}), 400
            
            # Update user
            update_data = {}
            for field in ['username', 'email', 'role', 'status', 'user_ident', 'tags', 'full_name']:
                if field in data:
                    update_data[field] = data[field]
            
            # Handle password update if provided
            if 'password' in data and data['password']:
                update_data['password'] = data['password']
            
            success = update_user(user_id, **update_data)
            if success:
                logger.info(f"User {user_id} updated successfully by admin")
                return jsonify({'message': 'User updated successfully'})
            else:
                return jsonify({'error': 'Failed to update user'}), 400
                
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            return jsonify({'error': 'Error updating user'}), 500
    
    @app.route('/api/users/<int:user_id>/password', methods=['PUT'])
    @login_required
    @admin_required
    def api_update_user_password(user_id):
        """Update user password via API"""
        try:
            data = request.get_json()
            
            if 'new_password' not in data:
                return jsonify({'error': 'Missing new_password field'}), 400
            
            # Validate password length
            if len(data['new_password']) < 6:
                return jsonify({'error': 'Password must be at least 6 characters long'}), 400
            
            success = update_user_password(user_id, data['new_password'])
            if success:
                logger.info(f"Password updated for user {user_id} by admin")
                return jsonify({'message': 'Password updated successfully'})
            else:
                return jsonify({'error': 'Failed to update password'}), 400
                
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            return jsonify({'error': 'Error updating password'}), 500
    
    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    @login_required
    @admin_required
    def api_delete_user(user_id):
        """Delete user via API"""
        try:
            current_user = get_current_user()
            
            # Prevent self-deletion
            if current_user and current_user.get('id') == user_id:
                return jsonify({'error': 'Cannot delete your own account'}), 400
            
            # Get user info for logging
            user = get_user_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            success = delete_user(user_id)
            if success:
                logger.info(f"User {user.get('username')} (ID: {user_id}) deleted by admin")
                return jsonify({'message': 'User deleted successfully'})
            else:
                return jsonify({'error': 'Failed to delete user'}), 400
                
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return jsonify({'error': 'Error deleting user'}), 500

    @app.route('/api/users/<int:user_id>/toggle-status', methods=['PUT'])
    @login_required
    @admin_required
    def api_toggle_user_status(user_id):
        """Toggle user active/inactive status via API"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if 'status' not in data:
                return jsonify({'error': 'Missing required field: status'}), 400
            
            # Validate status value
            if data['status'] not in ['active', 'inactive']:
                return jsonify({'error': 'Invalid status. Must be active or inactive'}), 400
            
            # Prevent deactivating yourself
            current_user = get_current_user()
            if current_user and current_user.get('id') == user_id and data['status'] == 'inactive':
                return jsonify({'error': 'Cannot deactivate your own account'}), 400
            
            # Get user info for logging
            user = get_user_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            success = toggle_user_status(user_id, data['status'])
            if success:
                status_text = "activated" if data['status'] == 'active' else "deactivated"
                logger.info(f"User {user.get('username')} (ID: {user_id}) {status_text} by admin")
                return jsonify({'message': f'User {status_text} successfully'})
            else:
                return jsonify({'error': 'Failed to update user status'}), 400
                
        except Exception as e:
            logger.error(f"Error toggling user status {user_id}: {e}")
            return jsonify({'error': 'Error updating user status'}), 500
