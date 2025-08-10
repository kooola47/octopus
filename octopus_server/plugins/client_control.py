"""
🔄 CLIENT RESTART PLUGIN
=======================

Plugin to handle client restart commands from the server.
"""

import os
import sys
import time
import subprocess
import logging

logger = logging.getLogger(__name__)

def restart_client():
    """
    Restart the current client process.
    
    This will:
    1. Log the restart request
    2. Create a restart script
    3. Execute the restart with a delay
    4. Exit the current process
    """
    try:
        logger.info("🔄 Client restart requested by server")
        
        # Get current script path and arguments
        script_path = sys.argv[0]
        script_args = sys.argv[1:]
        
        # Create restart command
        python_executable = sys.executable
        restart_cmd = [python_executable, script_path] + script_args
        
        logger.info(f"Restart command: {' '.join(restart_cmd)}")
        
        # Schedule restart in 2 seconds to allow response to be sent
        def delayed_restart():
            time.sleep(2)
            logger.info("💀 Terminating current process for restart...")
            
            # Start new process
            subprocess.Popen(restart_cmd, 
                           cwd=os.getcwd(),
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            # Exit current process
            os._exit(0)
        
        # Start restart in background thread
        import threading
        restart_thread = threading.Thread(target=delayed_restart, daemon=True)
        restart_thread.start()
        
        logger.info("🔄 Restart scheduled successfully")
        return {"status": "success", "message": "Client restart initiated"}
        
    except Exception as e:
        error_msg = f"Failed to restart client: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

def shutdown_client():
    """
    Gracefully shutdown the client.
    """
    try:
        logger.info("⛔ Client shutdown requested by server")
        
        def delayed_shutdown():
            time.sleep(2)
            logger.info("💀 Shutting down client...")
            os._exit(0)
        
        # Start shutdown in background thread
        import threading
        shutdown_thread = threading.Thread(target=delayed_shutdown, daemon=True)
        shutdown_thread.start()
        
        logger.info("⛔ Shutdown scheduled successfully")
        return {"status": "success", "message": "Client shutdown initiated"}
        
    except Exception as e:
        error_msg = f"Failed to shutdown client: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

def get_client_info():
    """
    Get detailed client information for diagnostics.
    """
    try:
        import platform
        
        info = {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "process_id": os.getpid(),
            "working_directory": os.getcwd(),
            "script_path": sys.argv[0],
        }
        
        # Try to get psutil info if available
        try:
            import psutil
            info.update({
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('.').percent,
                "uptime": time.time() - psutil.Process().create_time()
            })
        except ImportError:
            info.update({
                "cpu_percent": "N/A (psutil not available)",
                "memory_percent": "N/A (psutil not available)",
                "disk_usage": "N/A (psutil not available)",
                "uptime": "N/A (psutil not available)"
            })
        
        logger.info("📊 Client info requested")
        return {"status": "success", "data": info}
        
    except Exception as e:
        error_msg = f"Failed to get client info: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}
