"""
Performance Monitoring System
Real-time system metrics and performance tracking
"""

import time
import psutil
import threading
from collections import deque
from typing import Dict, List, Any
from datetime import datetime


class PerformanceMonitor:
    """Real-time performance monitoring and metrics collection"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.system_metrics = deque(maxlen=max_history)
        self.processing_history = []
        self.is_monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self, interval: float = 1.0):
        """Start real-time system monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, 
            args=(interval,), 
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time system monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self, interval: float):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self._collect_system_metrics()
                self.system_metrics.append(metrics)
                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': time.time(),
                'datetime': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'cpu_count': psutil.cpu_count(),
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024**3),
                'disk_total_gb': disk.total / (1024**3)
            }
        except Exception as e:
            print(f"Error collecting metrics: {e}")
            return {
                'timestamp': time.time(),
                'datetime': datetime.now().isoformat(),
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0
            }
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        return self._collect_system_metrics()
    
    def get_metrics_history(self) -> List[Dict[str, Any]]:
        """Get historical system metrics"""
        return list(self.system_metrics)
    
    def record_processing_result(self, result: Dict[str, Any]):
        """Record a processing result for history"""
        result['timestamp'] = time.time()
        result['datetime'] = datetime.now().isoformat()
        self.processing_history.append(result)
    
    def get_processing_history(self) -> List[Dict[str, Any]]:
        """Get processing history"""
        return self.processing_history
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.processing_history:
            return {
                'total_runs': 0,
                'average_speedup': 0,
                'best_speedup': 0,
                'total_time_saved': 0
            }
        
        speedups = [r.get('speedup', 0) for r in self.processing_history]
        time_saved = [r.get('time_saved', 0) for r in self.processing_history]
        
        return {
            'total_runs': len(self.processing_history),
            'average_speedup': sum(speedups) / len(speedups) if speedups else 0,
            'best_speedup': max(speedups) if speedups else 0,
            'worst_speedup': min(speedups) if speedups else 0,
            'total_time_saved': sum(time_saved),
            'average_time_saved': sum(time_saved) / len(time_saved) if time_saved else 0,
            'last_run': self.processing_history[-1] if self.processing_history else None
        }
    
    def get_system_health_score(self) -> Dict[str, Any]:
        """Calculate system health score"""
        if not self.system_metrics:
            return {'score': 50, 'status': 'Unknown', 'recommendations': []}
        
        latest = self.system_metrics[-1]
        cpu_score = max(0, 100 - latest['cpu_percent'])
        memory_score = max(0, 100 - latest['memory_percent'])
        disk_score = max(0, 100 - latest['disk_percent'])
        
        overall_score = (cpu_score + memory_score + disk_score) / 3
        
        if overall_score >= 80:
            status = "Excellent"
        elif overall_score >= 60:
            status = "Good"
        elif overall_score >= 40:
            status = "Fair"
        else:
            status = "Poor"
        
        recommendations = []
        if latest['cpu_percent'] > 80:
            recommendations.append("High CPU usage - consider reducing workload")
        if latest['memory_percent'] > 85:
            recommendations.append("High memory usage - close unnecessary applications")
        if latest['disk_percent'] > 90:
            recommendations.append("Low disk space - free up storage")
        
        return {
            'score': overall_score,
            'status': status,
            'cpu_score': cpu_score,
            'memory_score': memory_score,
            'disk_score': disk_score,
            'recommendations': recommendations
        }
    
    def export_metrics(self, filename: str = None) -> str:
        """Export metrics to JSON file"""
        if not filename:
            filename = f"performance_metrics_{int(time.time())}.json"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'system_metrics': list(self.system_metrics),
            'processing_history': self.processing_history,
            'performance_summary': self.get_performance_summary(),
            'system_health': self.get_system_health_score()
        }
        
        import json
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename