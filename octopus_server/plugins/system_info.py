#!/usr/bin/env python3
"""
System Info Plugin
==================
Plugin for gathering system information and running system commands
"""

import platform
import psutil
import subprocess
import time
from typing import Optional

def get_system_info():
    """
    Get basic system information.
    
    Returns:
        str: Formatted system information
    """
    try:
        info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Architecture": platform.architecture()[0],
            "Processor": platform.processor(),
            "Hostname": platform.node(),
            "Python Version": platform.python_version(),
        }
        
        result = "System Information:\n"
        for key, value in info.items():
            result += f"  {key}: {value}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting system info: {str(e)}"

def get_cpu_usage(interval: float = 1.0):
    """
    Get current CPU usage percentage.
    
    Args:
        interval: Measurement interval in seconds (default: 1.0)
    
    Returns:
        str: CPU usage information
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=interval)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        result = f"CPU Usage: {cpu_percent}%\n"
        result += f"CPU Cores: {cpu_count}\n"
        
        if cpu_freq:
            result += f"CPU Frequency: {cpu_freq.current:.2f} MHz\n"
        
        return result
        
    except Exception as e:
        return f"Error getting CPU usage: {str(e)}"

def get_memory_usage():
    """
    Get current memory usage information.
    
    Returns:
        str: Memory usage details
    """
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        result = "Memory Usage:\n"
        result += f"  Total: {memory.total / (1024**3):.2f} GB\n"
        result += f"  Available: {memory.available / (1024**3):.2f} GB\n"
        result += f"  Used: {memory.used / (1024**3):.2f} GB ({memory.percent}%)\n"
        result += f"  Free: {memory.free / (1024**3):.2f} GB\n"
        
        result += "\nSwap Usage:\n"
        result += f"  Total: {swap.total / (1024**3):.2f} GB\n"
        result += f"  Used: {swap.used / (1024**3):.2f} GB ({swap.percent}%)\n"
        result += f"  Free: {swap.free / (1024**3):.2f} GB\n"
        
        return result
        
    except Exception as e:
        return f"Error getting memory usage: {str(e)}"

def run_command(command: str, timeout: int = 30, shell: bool = True):
    """
    Execute a system command and return the output.
    
    Args:
        command: Command to execute
        timeout: Command timeout in seconds (default: 30)
        shell: Whether to run in shell mode (default: True)
    
    Returns:
        str: Command output or error message
    """
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = f"Command: {command}\n"
        output += f"Return Code: {result.returncode}\n"
        
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def get_disk_usage(path: str = "/"):
    """
    Get disk usage information for a given path.
    
    Args:
        path: Path to check disk usage (default: root)
    
    Returns:
        str: Disk usage information
    """
    try:
        disk_usage = psutil.disk_usage(path)
        
        result = f"Disk Usage for '{path}':\n"
        result += f"  Total: {disk_usage.total / (1024**3):.2f} GB\n"
        result += f"  Used: {disk_usage.used / (1024**3):.2f} GB\n"
        result += f"  Free: {disk_usage.free / (1024**3):.2f} GB\n"
        result += f"  Usage: {(disk_usage.used / disk_usage.total * 100):.1f}%\n"
        
        return result
        
    except Exception as e:
        return f"Error getting disk usage: {str(e)}"

def get_network_info():
    """
    Get network interface information.
    
    Returns:
        str: Network interface details
    """
    try:
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        result = "Network Interfaces:\n"
        
        for interface, addresses in interfaces.items():
            result += f"\n{interface}:\n"
            
            # Get interface stats
            if interface in stats:
                stat = stats[interface]
                result += f"  Status: {'Up' if stat.isup else 'Down'}\n"
                result += f"  Speed: {stat.speed} Mbps\n" if stat.speed > 0 else "  Speed: Unknown\n"
            
            # Get addresses
            for addr in addresses:
                if addr.family.name == 'AF_INET':  # IPv4
                    result += f"  IPv4: {addr.address}\n"
                    if addr.netmask:
                        result += f"  Netmask: {addr.netmask}\n"
                elif addr.family.name == 'AF_INET6':  # IPv6
                    result += f"  IPv6: {addr.address}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting network info: {str(e)}"

def ping_host(hostname: str, count: int = 4, timeout: int = 10):
    """
    Ping a host and return the results.
    
    Args:
        hostname: Hostname or IP address to ping
        count: Number of ping packets to send (default: 4)
        timeout: Timeout for ping command in seconds (default: 10)
    
    Returns:
        str: Ping results
    """
    try:
        # Determine ping command based on OS
        if platform.system().lower() == "windows":
            cmd = f"ping -n {count} {hostname}"
        else:
            cmd = f"ping -c {count} {hostname}"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = f"Ping results for {hostname}:\n"
        output += f"Return Code: {result.returncode}\n"
        
        if result.stdout:
            output += f"{result.stdout}\n"
        
        if result.stderr:
            output += f"Error: {result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"Error: Ping to {hostname} timed out after {timeout} seconds"
    except Exception as e:
        return f"Error pinging host: {str(e)}"
