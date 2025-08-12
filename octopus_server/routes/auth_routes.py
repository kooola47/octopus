#!/usr/bin/env python3
"""
🔐 AUTHENTICATION ROUTES
========================

Flask routes for user authentication and session management.
"""

import json
import time
from flask import request, render_template, redirect, url_for, session, flash, jsonify, render_template_string
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
            return render_template_string(LOGIN_TEMPLATE)
        
        elif request.method == "POST":
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Username and password are required', 'error')
                return render_template_string(LOGIN_TEMPLATE)
            
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
                return render_template_string(LOGIN_TEMPLATE)
    
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

# Login page template
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐙 Octopus Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .octopus-icon {
            font-size: 3rem;
            color: #2a5298;
            margin-bottom: 10px;
        }
        .btn-login {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border: none;
            padding: 12px;
            font-weight: 500;
        }
        .form-control:focus {
            border-color: #2a5298;
            box-shadow: 0 0 0 0.2rem rgba(42, 82, 152, 0.25);
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <div class="octopus-icon">
                <i class="fas fa-search"></i>
            </div>
            <h2 class="h3 mb-0">Octopus System</h2>
            <p class="text-muted">Distributed Task Orchestration</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST">
            <div class="mb-3">
                <label for="username" class="form-label">
                    <i class="fas fa-user me-2"></i>Username
                </label>
                <input type="text" class="form-control" id="username" name="username" 
                       required autocomplete="username" placeholder="Enter username">
            </div>
            
            <div class="mb-4">
                <label for="password" class="form-label">
                    <i class="fas fa-lock me-2"></i>Password
                </label>
                <input type="password" class="form-control" id="password" name="password" 
                       required autocomplete="current-password" placeholder="Enter password">
            </div>
            
            <button type="submit" class="btn btn-login text-white w-100">
                <i class="fas fa-sign-in-alt me-2"></i>Login
            </button>
        </form>
        
        <div class="text-center mt-4">
            <small class="text-muted">
                Default: admin / admin123
            </small>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""