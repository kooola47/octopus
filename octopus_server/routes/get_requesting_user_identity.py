"""
Requesting User Identity Helper
==============================

Helper function to get the identity of the user making the request.
"""
from flask import request

def get_requesting_user_identity(logger=None):
    """
    Get the identity of the user making the request
    Returns:
        Username if identified, None otherwise
    """
    try:
        client_id = request.headers.get('X-Client-ID') or request.args.get('client_id')
        if client_id:
            from global_cache_manager import get_global_cache_manager
            cache_manager = get_global_cache_manager()
            username = cache_manager.get_user_identity_from_client_id(client_id)
            if username:
                return username
        username = request.headers.get('X-Username')
        if username:
            return username
        return None
    except Exception as e:
        if logger:
            logger.error(f"Error getting requesting user identity: {e}")
        return None
