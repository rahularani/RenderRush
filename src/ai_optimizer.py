"""
AI Performance Optimizer
Provides intelligent recommendations for optimal video processing
"""

import psutil
import numpy as np
from typing import Dict, List, Any


class AIOptimizer:
    """AI-powered performance optimization system"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory(),
            'disk': psutil.disk_usage('/') if psutil.disk_usage else None
        }
    
    def get_optimal_workers(self, video_info: Dict[str, Any] = None) -> int:
        """Calculate optimal number of workers based on system resources"""
        cpu_count = self.system_info['cpu_count']
        cpu_usage = self.system_info['cpu_percent']
        memory_percent = self.system_info['memory'].percent
        
        # Base recommendation on CPU cores
        optimal_workers = cpu_count
        
        # Adjust based on current system load
        if cpu_usage > 80:
            optimal_workers = max(2, cpu_count // 2)
        elif cpu_usage < 30:
            optimal_workers = min(8, cpu_count)
        
        # Adjust based on memory usage
        if memory_percent > 85:
            optimal_workers = max(2, optimal_workers // 2)
        
        # Adjust based on video characteristics
        if video_info:
            resolution = video_info.get('width', 0) * video_info.get('height', 0)
            if resolution > 2073600:  # 1920x1080
                optimal_workers = min(optimal_workers, 4)
        
        return max(1, min(optimal_workers, 8))
    
    def recommend_filter(self, video_info: Dict[str, Any]) -> str:
        """Recommend optimal filter based on video characteristics"""
        if not video_info:
            return "grayscale"
        
        resolution = video_info.get('width', 0) * video_info.get('height', 0)
        fps = video_info.get('fps', 30)
        duration = video_info.get('duration', 0)
        
        # High resolution videos - use lighter processing
        if resolution > 2073600:  # 1920x1080
            return "grayscale"
        
        # High FPS videos - use brightness adjustment
        if fps > 30:
            return "brightness"
        
        # Long videos - use efficient processing
        if duration > 120:
            return "grayscale"
        
        # Default for standard videos
        return "blur"
    
    def predict_performance(self, video_info: Dict[str, Any], workers: int, filter_type: str) -> Dict[str, float]:
        """Predict processing performance"""
        if not video_info:
            return {'estimated_time': 0, 'predicted_speedup': 1.0, 'confidence': 0.5}
        
        duration = video_info.get('duration', 60)
        resolution = video_info.get('width', 1920) * video_info.get('height', 1080)
        
        # Base processing time estimation (rough model)
        base_time = duration * 0.5  # Assume 0.5 seconds per second of video
        
        # Adjust for resolution
        resolution_factor = min(2.0, resolution / 2073600)  # 1080p baseline
        base_time *= resolution_factor
        
        # Adjust for filter complexity
        filter_factors = {
            'grayscale': 0.8,
            'brightness': 1.0,
            'blur': 1.3,
            'contrast': 1.1,
            'none': 0.7
        }
        base_time *= filter_factors.get(filter_type, 1.0)
        
        # Calculate parallel speedup (Amdahl's law approximation)
        parallel_fraction = 0.9  # Assume 90% of work is parallelizable
        predicted_speedup = 1 / ((1 - parallel_fraction) + (parallel_fraction / workers))
        
        # Adjust for system limitations
        system_efficiency = min(1.0, (100 - self.system_info['cpu_percent']) / 100)
        predicted_speedup *= (0.5 + 0.5 * system_efficiency)
        
        estimated_time = base_time / predicted_speedup
        
        # Confidence based on system stability
        confidence = 0.7 + 0.3 * system_efficiency
        
        return {
            'estimated_time': estimated_time,
            'predicted_speedup': predicted_speedup,
            'confidence': confidence,
            'base_time': base_time
        }
    
    def get_system_recommendations(self) -> List[Dict[str, str]]:
        """Get system-specific recommendations"""
        recommendations = []
        
        cpu_usage = self.system_info['cpu_percent']
        memory_percent = self.system_info['memory'].percent
        
        if cpu_usage > 80:
            recommendations.append({
                'type': 'warning',
                'title': 'High CPU Usage',
                'message': f'CPU usage is {cpu_usage:.1f}%. Consider reducing worker count.',
                'action': 'reduce_workers'
            })
        elif cpu_usage < 30:
            recommendations.append({
                'type': 'optimization',
                'title': 'CPU Underutilized',
                'message': f'CPU usage is only {cpu_usage:.1f}%. You can increase workers.',
                'action': 'increase_workers'
            })
        
        if memory_percent > 85:
            recommendations.append({
                'type': 'critical',
                'title': 'Memory Critical',
                'message': f'Memory usage is {memory_percent:.1f}%. Risk of system instability.',
                'action': 'reduce_segments'
            })
        elif memory_percent > 70:
            recommendations.append({
                'type': 'warning',
                'title': 'High Memory Usage',
                'message': f'Memory usage is {memory_percent:.1f}%. Monitor closely.',
                'action': 'monitor_memory'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'title': 'System Optimal',
                'message': 'System resources are well balanced for processing.',
                'action': 'continue'
            })
        
        return recommendations
    
    def calculate_efficiency_score(self, actual_speedup: float, workers: int) -> Dict[str, float]:
        """Calculate processing efficiency metrics"""
        theoretical_max = workers * 0.9  # 90% theoretical maximum
        efficiency = (actual_speedup / theoretical_max) * 100 if theoretical_max > 0 else 0
        
        # Performance rating
        if efficiency >= 80:
            rating = "Excellent"
        elif efficiency >= 60:
            rating = "Good"
        elif efficiency >= 40:
            rating = "Fair"
        else:
            rating = "Poor"
        
        return {
            'efficiency_percent': efficiency,
            'theoretical_max': theoretical_max,
            'rating': rating,
            'worker_utilization': (actual_speedup / workers) * 100 if workers > 0 else 0
        }