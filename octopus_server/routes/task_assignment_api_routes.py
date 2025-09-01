"""
🔧 TASK ASSIGNMENT API
======================

API endpoints for manual task assignment and debugging.
"""

from flask import jsonify, request
from services.task_assignment_service import get_assignment_service
from dbhelper import get_tasks, get_active_clients
import time


def register_task_assignment_api_routes(app, global_cache, logger):
    """Register task assignment API routes"""
    
    @app.route("/api/tasks/assign", methods=["POST"])
    def api_assign_tasks():
        """Manually trigger task assignment"""
        try:
            assignment_service = get_assignment_service(global_cache)
            force = request.json.get('force', False) if request.is_json and request.json else False
            
            result = assignment_service.assign_pending_tasks(force=force)
            
            return jsonify({
                "success": True,
                "assignment_result": result
            })
            
        except Exception as e:
            logger.error(f"Manual task assignment failed: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route("/api/tasks/assignment-status", methods=["GET"])
    def api_assignment_status():
        """Get task assignment service status"""
        try:
            assignment_service = get_assignment_service(global_cache)
            status = assignment_service.get_assignment_status()
            
            # Add current task and client info
            tasks = get_tasks()
            clients = global_cache.all()
            active_clients = get_active_clients(clients, now=time.time(), timeout=60)
            
            unassigned_tasks = [
                {
                    "id": tid,
                    "owner": task.get("owner"),
                    "executor": task.get("executor"),
                    "status": task.get("status"),
                    "plugin": task.get("plugin"),
                    "created_at": task.get("created_at")
                }
                for tid, task in tasks.items()
                if not task.get("executor") and task.get("status") not in ("success", "failed", "Done")
            ]
            
            return jsonify({
                "assignment_service": status,
                "current_state": {
                    "total_tasks": len(tasks),
                    "unassigned_tasks": len(unassigned_tasks),
                    "active_clients": len(active_clients),
                    "active_client_usernames": [client.get('username') for client in active_clients.values()]
                },
                "unassigned_task_details": unassigned_tasks
            })
            
        except Exception as e:
            logger.error(f"Failed to get assignment status: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
