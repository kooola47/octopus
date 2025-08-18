#!/usr/bin/env python3
"""
🔐 AUTHENTICATION ROUTES
========================

Flask routes for user authentication and session management.
"""

import json
import time
from flask import request, render_template, redirect, url_for, session, flash, jsonify
from dbhelper import authenticate_user, create_user
from functools import wraps

def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Debug: Print session content
        print(f"DEBUG: Session content: {dict(session)}")
        print(f"DEBUG: 'user_id' in session: {'user_id' in session}")
        
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def register_auth_routes(app, cache, logger):
    """Register authentication routes with the Flask app"""
    
    # Set secret key for sessions
    app.secret_key = 'octopus-secret-key-change-in-production'
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login page and authentication"""
        if request.method == "GET":
            # Show login form
            return render_template('login.html')
        
        elif request.method == "POST":
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Username and password are required', 'error')
                return render_template('login.html')
            
            # Authenticate user
            user = authenticate_user(username, password)
            
            if user:
                # Make session permanent and store user info
                session.permanent = True
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['login_time'] = time.time()
                
                # Force session to be saved
                session.modified = True
                
                # Debug: Check session after setting
                print(f"DEBUG: Session after login: {dict(session)}")
                
                logger.info(f"User {username} logged in successfully")
                
                # Redirect to dashboard
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                flash('Invalid username or password', 'error')
                return render_template('login.html')
    
    @app.route("/logout")
    def logout():
        """Logout and clear session"""
        username = session.get('username', 'Unknown')
        session.clear()
        logger.info(f"User {username} logged out")
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))
    
    @app.route("/")
    def index():
        """Root route - redirect to dashboard if logged in, otherwise login"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))
    
    # API endpoint for checking authentication status
    @app.route("/api/auth/status")
    def auth_status():
        """Check authentication status"""
        if 'user_id' in session:
            return jsonify({
                'authenticated': True,
                'username': session.get('username'),
                'role': session.get('role'),
                'login_time': session.get('login_time')
            })
        else:
            return jsonify({'authenticated': False})