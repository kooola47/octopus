#!/usr/bin/env python3
"""
🐙 OCTOPUS SERVER - Template Helpers
===================================

Template helper functions for status management and UI consistency.
"""

from constants import TaskStatus, ExecutionStatus, UserStatus, ClientStatus, UserRole

def register_template_helpers(app):
    """Register template helper functions with Flask app"""
    
    @app.template_filter('task_status_badge')
    def task_status_badge(status):
        """Get Bootstrap badge class for task status"""
        return TaskStatus.get_badge_class(status)
    
    @app.template_filter('task_status_icon')
    def task_status_icon(status):
        """Get Bootstrap icon for task status"""
        return TaskStatus.get_icon(status)
    
    @app.template_filter('task_status_normalize')
    def task_status_normalize(status):
        """Normalize task status"""
        return TaskStatus.normalize(status)
    
    @app.template_filter('execution_status_badge')
    def execution_status_badge(status):
        """Get Bootstrap badge class for execution status"""
        return ExecutionStatus.get_badge_class(status)
    
    @app.template_filter('execution_status_icon')
    def execution_status_icon(status):
        """Get Bootstrap icon for execution status"""
        return ExecutionStatus.get_icon(status)
    
    @app.template_filter('user_status_badge')
    def user_status_badge(status):
        """Get Bootstrap badge class for user status"""
        return UserStatus.get_badge_class(status)
    
    @app.template_filter('user_status_icon')
    def user_status_icon(status):
        """Get Bootstrap icon for user status"""
        return UserStatus.get_icon(status)
    
    @app.template_filter('client_status_badge')
    def client_status_badge(status):
        """Get Bootstrap badge class for client status"""
        return ClientStatus.get_badge_class(status)
    
    @app.template_filter('client_status_icon')
    def client_status_icon(status):
        """Get Bootstrap icon for client status"""
        return ClientStatus.get_icon(status)
    
    @app.template_filter('user_role_badge')
    def user_role_badge(role):
        """Get Bootstrap badge class for user role"""
        return UserRole.get_badge_class(role)
    
    @app.template_filter('user_role_icon')
    def user_role_icon(role):
        """Get Bootstrap icon for user role"""
        return UserRole.get_icon(role)
    
    # Context processors to make constants available in templates
    @app.context_processor
    def inject_status_constants():
        """Inject status constants into template context"""
        return {
            'TaskStatus': TaskStatus,
            'ExecutionStatus': ExecutionStatus,
            'UserStatus': UserStatus,
            'ClientStatus': ClientStatus,
            'UserRole': UserRole
        }
