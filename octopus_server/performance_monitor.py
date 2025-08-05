#!/usr/bin/env python3
"""
🐙 OCTOPUS PERFORMANCE MONITOR
=============================

Real-time performance monitoring for concurrent client handling
"""

import time
import threading
import psutil
import logging
from functools import wraps
from collections import defaultdict, deque
from typing import Dict, List

logger = logging.getLogger("octopus_performance")

class PerformanceMonitor:
    """Thread-safe performance monitoring"""
    
    def __init__(self):
        self.request_times = defaultdict(deque)  # endpoint -> deque of response times
        self.request_counts = defaultdict(int)   # endpoint -> count
        self.active_requests = defaultdict(int)  # endpoint -> active count
        self.db_operations = deque()             # database operation times
        self.lock = threading.RLock()
        
        # Keep only last 1000 measurements per endpoint
        self.max_measurements = 1000
        
    def record_request(self, endpoint: str, duration: float):
        """Record request duration"""
        with self.lock:
            self.request_times[endpoint].append(duration)
            if len(self.request_times[endpoint]) > self.max_measurements:
                self.request_times[endpoint].popleft()
            self.request_counts[endpoint] += 1
    
    def record_db_operation(self, duration: float):
        """Record database operation duration"""
        with self.lock:
            self.db_operations.append(duration)
            if len(self.db_operations) > self.max_measurements:
                self.db_operations.popleft()
    
    def start_request(self, endpoint: str):
        """Mark request as started"""
        with self.lock:
            self.active_requests[endpoint] += 1
    
    def end_request(self, endpoint: str):
        """Mark request as completed"""
        with self.lock:
            if self.active_requests[endpoint] > 0:
                self.active_requests[endpoint] -= 1
    
    def get_stats(self) -> Dict:
        """Get current performance statistics"""
        with self.lock:
            stats = {
                "system": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "active_connections": sum(self.active_requests.values())
                },
                "endpoints": {},
                "database": {
                    "operations_count": len(self.db_operations),
                    "avg_duration": sum(self.db_operations) / len(self.db_operations) if self.db_operations else 0,
                    "max_duration": max(self.db_operations) if self.db_operations else 0
                }
            }
            
            for endpoint, times in self.request_times.items():
                if times:
                    stats["endpoints"][endpoint] = {
                        "total_requests": self.request_counts[endpoint],
                        "active_requests": self.active_requests[endpoint],
                        "avg_response_time": sum(times) / len(times),
                        "max_response_time": max(times),
                        "min_response_time": min(times),
                        "recent_avg": sum(list(times)[-10:]) / min(10, len(times))  # Last 10 requests
                    }
            
            return stats
    
    def get_performance_alerts(self) -> List[str]:
        """Get performance alerts and warnings"""
        alerts = []
        stats = self.get_stats()
        
        # System alerts
        if stats["system"]["cpu_percent"] > 80:
            alerts.append(f"🚨 HIGH CPU: {stats['system']['cpu_percent']:.1f}%")
        
        if stats["system"]["memory_percent"] > 80:
            alerts.append(f"🚨 HIGH MEMORY: {stats['system']['memory_percent']:.1f}%")
        
        if stats["system"]["active_connections"] > 15:
            alerts.append(f"⚠️ HIGH LOAD: {stats['system']['active_connections']} active requests")
        
        # Database alerts
        if stats["database"]["avg_duration"] > 1.0:
            alerts.append(f"🐌 SLOW DB: {stats['database']['avg_duration']:.2f}s average")
        
        if stats["database"]["max_duration"] > 5.0:
            alerts.append(f"🚨 DB TIMEOUT RISK: {stats['database']['max_duration']:.2f}s max")
        
        # Endpoint alerts
        for endpoint, data in stats["endpoints"].items():
            if data["avg_response_time"] > 2.0:
                alerts.append(f"🐌 SLOW ENDPOINT {endpoint}: {data['avg_response_time']:.2f}s")
            
            if data["active_requests"] > 5:
                alerts.append(f"⚠️ CONGESTED {endpoint}: {data['active_requests']} active")
        
        return alerts

# Global monitor instance
monitor = PerformanceMonitor()

def time_request(endpoint: str):
    """Decorator to time request duration"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            monitor.start_request(endpoint)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                monitor.end_request(endpoint)
                monitor.record_request(endpoint, duration)
                
                # Log slow requests
                if duration > 2.0:
                    logger.warning(f"Slow request {endpoint}: {duration:.2f}s")
        return wrapper
    return decorator

def time_db_operation():
    """Decorator to time database operations"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                monitor.record_db_operation(duration)
                
                # Log slow DB operations
                if duration > 1.0:
                    logger.warning(f"Slow DB operation {func.__name__}: {duration:.2f}s")
        return wrapper
    return decorator

def get_performance_report() -> str:
    """Generate a human-readable performance report"""
    stats = monitor.get_stats()
    alerts = monitor.get_performance_alerts()
    
    report = "📊 OCTOPUS PERFORMANCE REPORT\n"
    report += "=" * 40 + "\n"
    
    # System stats
    report += f"🖥️  CPU: {stats['system']['cpu_percent']:.1f}%\n"
    report += f"💾 Memory: {stats['system']['memory_percent']:.1f}%\n"
    report += f"🔗 Active Requests: {stats['system']['active_connections']}\n\n"
    
    # Database stats
    report += "💾 DATABASE PERFORMANCE:\n"
    report += f"   Operations: {stats['database']['operations_count']}\n"
    report += f"   Avg Duration: {stats['database']['avg_duration']:.3f}s\n"
    report += f"   Max Duration: {stats['database']['max_duration']:.3f}s\n\n"
    
    # Endpoint stats
    report += "🌐 ENDPOINT PERFORMANCE:\n"
    for endpoint, data in stats['endpoints'].items():
        report += f"   {endpoint}:\n"
        report += f"     Total: {data['total_requests']}, Active: {data['active_requests']}\n"
        report += f"     Avg: {data['avg_response_time']:.3f}s, Max: {data['max_response_time']:.3f}s\n"
    
    # Alerts
    if alerts:
        report += "\n🚨 ALERTS:\n"
        for alert in alerts:
            report += f"   {alert}\n"
    else:
        report += "\n✅ No performance issues detected\n"
    
    return report
