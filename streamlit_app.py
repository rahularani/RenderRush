"""
RenderRush: Distributed Video Renderer
Streamlit Cloud Deployment Entry Point

A high-performance video processing application that demonstrates
the power of parallel processing with real-time performance monitoring.

Author: Development Team
Created: February 2026
"""

import streamlit as st
import os
import time
import json
from datetime import datetime
from multiprocessing import Pool, freeze_support

# Import local modules
from src.video_processor import VideoProcessor
from src.ai_optimizer import AIOptimizer
from src.performance_monitor import PerformanceMonitor
from src.ui_components import UIComponents

# Page configuration
st.set_page_config(
    page_title="RenderRush - Video Renderer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'performance_monitor' not in st.session_state:
    st.session_state.performance_monitor = PerformanceMonitor()
    st.session_state.performance_monitor.start_monitoring()

if 'ai_optimizer' not in st.session_state:
    st.session_state.ai_optimizer = AIOptimizer()

if 'video_processor' not in st.session_state:
    st.session_state.video_processor = VideoProcessor()


def main():
    """Main application function"""
    
    # Load custom styling
    UIComponents.load_custom_css()
    
    # Create header
    UIComponents.create_header(
        "🚀 RenderRush",
        "Distributed Video Renderer with Real-Time Performance Monitoring"
    )
    
    # Cloud deployment notice
    st.info("🌐 **Running on Streamlit Cloud** - Some features may be limited due to cloud environment constraints")
    
    # Get current system metrics
    monitor = st.session_state.performance_monitor
    ai_optimizer = st.session_state.ai_optimizer
    video_processor = st.session_state.video_processor
    
    current_metrics = monitor.get_current_metrics()
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # System status
        st.markdown("### 📊 System Status")
        st.metric("CPU", f"{current_metrics['cpu_percent']:.1f}%")
        st.metric("Memory", f"{current_metrics['memory_percent']:.1f}%")
        
        # Configuration
        st.markdown("### 🔧 Processing Settings")
        
        workers = st.slider(
            "🔧 Parallel Workers",
            min_value=1,
            max_value=4,  # Limited for cloud deployment
            value=2,
            help="Number of parallel workers (limited to 4 on cloud)"
        )
        
        segment_duration = st.slider(
            "⏱️ Segment Duration (seconds)",
            min_value=5.0,
            max_value=15.0,  # Shorter segments for cloud
            value=10.0,
            step=1.0,
            help="Duration of each video segment"
        )
        
        filter_type = st.selectbox(
            "🎨 Video Filter",
            options=["grayscale", "brightness", "blur", "contrast", "none"],
            index=0,
            help="Select the filter to apply to the video"
        )
        
        # Cloud limitations notice
        st.warning("⚠️ **Cloud Limitations:**\n- Max 4 workers\n- Shorter processing time\n- Limited file size")
        
        # Export options
        st.markdown("### 📊 Export & Analysis")
        
        # Real-time monitoring toggle
        enable_realtime = st.checkbox(
            "🔴 Real-time Monitoring",
            value=st.session_state.get('enable_realtime', True),
            help="Enable real-time system monitoring"
        )
        st.session_state.enable_realtime = enable_realtime
        
        if st.button("📈 Export Performance Report"):
            filename = monitor.export_metrics()
            with open(filename, 'r') as f:
                report_data = f.read()
            
            st.download_button(
                "📥 Download Report",
                data=report_data,
                file_name=filename,
                mime="application/json"
            )
    
    # Main content area
    st.markdown("## 📁 Video Processing")
    
    uploaded_file = st.file_uploader(
        "🎬 Upload Your Video",
        type=["mp4", "avi", "mov"],
        help="Upload a video file (max 200MB for cloud deployment)"
    )
    
    if uploaded_file is not None:
        # Check file size for cloud deployment
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        if file_size_mb > 200:
            st.error(f"❌ File too large ({file_size_mb:.1f}MB). Please upload a file smaller than 200MB.")
            return
        
        # Save uploaded file
        video_path = f"uploads/{uploaded_file.name}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Analyze video
        with st.spinner("📊 Analyzing video..."):
            video_info = video_processor.get_video_info(video_path)
            
            if video_info is None:
                st.error("❌ Could not analyze video. Please try a different format.")
                return
        
        # Display video information
        st.success(f"✅ Video analyzed: {uploaded_file.name} ({file_size_mb:.1f}MB)")
        
        # Video info metrics - display in rows to avoid nesting
        st.metric("Duration", f"{video_info['duration']:.1f}s")
        st.metric("Resolution", f"{video_info['width']}x{video_info['height']}")
        st.metric("FPS", f"{video_info['fps']:.1f}")
        segments = int(video_info['duration'] / segment_duration) + 1
        st.metric("Segments", segments)
        
        # Processing buttons
        st.markdown("### 🚀 Start Processing")
        
        if st.button("🏁 Ultimate Showdown", type="primary"):
            run_performance_comparison(video_path, filter_type, workers, segment_duration)
        
        if st.button("⚡ Parallel Only", type="secondary"):
            run_parallel_processing(video_path, filter_type, workers, segment_duration)
        
        if st.button("🧪 Demo Mode", type="secondary"):
            run_demo_mode(video_path, filter_type, workers)
    
    # Performance Dashboard - separate section
    st.markdown("---")
    st.markdown("## 📊 Performance Dashboard")
    
    # Latest results
    processing_history = monitor.get_processing_history()
    if processing_history:
        latest = processing_history[-1]
        
        # Speedup gauge
        speedup_fig = UIComponents.create_speedup_gauge(latest.get('speedup', 1.0))
        st.plotly_chart(speedup_fig, use_container_width=True)
        
        # Performance summary
        summary_html = UIComponents.create_metric_card(
            "🏆 Latest Achievement",
            f"{latest.get('speedup', 1.0):.2f}x",
            f"Saved {latest.get('time_saved', 0):.1f} seconds",
            "speedup"
        )
        st.markdown(summary_html, unsafe_allow_html=True)
    
    # System health
    health = monitor.get_system_health_score()
    health_html = UIComponents.create_metric_card(
        "💚 System Health",
        f"{health['score']:.0f}/100",
        health['status'],
        "metric"
    )
    st.markdown(health_html, unsafe_allow_html=True)
    
    # Performance history
    if processing_history:
        st.markdown("### 📈 Performance History")
        for i, result in enumerate(reversed(processing_history[-5:])):
            badge_html = UIComponents.create_status_badge(
                f"{result.get('speedup', 1.0):.1f}x speedup",
                'success' if result.get('speedup', 0) > 2 else 'info'
            )
            st.markdown(badge_html, unsafe_allow_html=True)
    
    # Real-time performance chart with manual refresh
    st.markdown("---")
    st.markdown("## 📊 Real-Time System Monitoring")
    
    # Check if real-time monitoring is enabled
    enable_realtime = st.session_state.get('enable_realtime', True)
    
    # Add refresh controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if enable_realtime:
            st.markdown("🔴 **Live Monitoring Active**")
        else:
            st.markdown("⚪ **Live Monitoring Paused**")
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    with col3:
        auto_refresh = st.button("🔄 Auto-Refresh (3s)")
    
    # Get current metrics and display
    current_metrics = monitor.get_current_metrics()
    metrics_history = monitor.get_metrics_history()
    
    # Always show current metrics
    st.markdown("### 📈 Current System Status")
    
    # Create real-time metric display
    current_metrics_html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center;">
            <h4>💻 CPU Usage</h4>
            <h2>{current_metrics['cpu_percent']:.1f}%</h2>
            <p>{current_metrics['cpu_count']} cores</p>
        </div>
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center;">
            <h4>🧠 Memory Usage</h4>
            <h2>{current_metrics['memory_percent']:.1f}%</h2>
            <p>{current_metrics['memory_available_gb']:.1f} GB free</p>
        </div>
        <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center;">
            <h4>💾 Disk Usage</h4>
            <h2>{current_metrics['disk_percent']:.1f}%</h2>
            <p>{current_metrics['disk_used_gb']:.0f} GB used</p>
        </div>
    </div>
    """
    st.markdown(current_metrics_html, unsafe_allow_html=True)
    
    # System health indicator
    cpu_health = "🟢 Good" if current_metrics['cpu_percent'] < 70 else "🟡 High" if current_metrics['cpu_percent'] < 90 else "🔴 Critical"
    memory_health = "🟢 Good" if current_metrics['memory_percent'] < 70 else "🟡 High" if current_metrics['memory_percent'] < 90 else "🔴 Critical"
    
    st.markdown(f"""
    **System Health**: CPU: {cpu_health} | Memory: {memory_health} | 
    Last updated: {time.strftime('%H:%M:%S')}
    """)
    
    # Show historical chart if available
    if len(metrics_history) > 1:
        st.markdown("### 📊 Performance History")
        perf_chart = UIComponents.create_performance_chart(metrics_history)
        if perf_chart:
            st.plotly_chart(perf_chart, use_container_width=True)
    else:
        st.info("📊 Historical data will appear after a few monitoring cycles...")
    
    # Auto-refresh mechanism
    if auto_refresh or (enable_realtime and 'auto_refresh_active' in st.session_state):
        st.session_state.auto_refresh_active = True
        time.sleep(3)
        st.rerun()


def run_performance_comparison(video_path: str, filter_type: str, workers: int, segment_duration: float):
    """Run performance comparison optimized for cloud deployment"""
    
    st.markdown("---")
    st.markdown("# 🏁 ULTIMATE PERFORMANCE SHOWDOWN")
    st.markdown("*Cloud-optimized parallel processing demonstration*")
    
    # Simplified processing for cloud deployment
    video_processor = st.session_state.video_processor
    monitor = st.session_state.performance_monitor
    
    try:
        # Split video
        st.info("🎬 Splitting video into segments...")
        video_processor.segment_duration = segment_duration
        segments, duration = video_processor.split_video(video_path)
        
        if not segments:
            st.error("❌ Failed to create video segments")
            return
        
        st.success(f"✅ Created {len(segments)} segments")
        
        # Sequential processing
        st.markdown("## 🐢 Sequential Processing")
        seq_progress = st.progress(0)
        
        start_seq = time.time()
        processed_seq = []
        
        for i, segment in enumerate(segments):
            seq_progress.progress((i + 1) / len(segments))
            output_file = f"output/seq_{i:03d}.mp4"
            os.makedirs("output", exist_ok=True)
            result = video_processor.process_segment((i, segment, output_file, filter_type))
            if result:
                processed_seq.append(result)
        
        sequential_time = time.time() - start_seq
        st.success(f"🐢 Sequential: {sequential_time:.1f}s")
        
        # Parallel processing
        st.markdown("## ⚡ Parallel Processing")
        par_progress = st.progress(0)
        
        start_par = time.time()
        
        # Prepare tasks
        par_tasks = []
        for i, segment in enumerate(segments):
            output_file = f"output/par_{i:03d}.mp4"
            par_tasks.append((i, segment, output_file, filter_type))
        
        # Process in parallel
        freeze_support()
        with Pool(workers) as pool:
            processed_par = pool.map(video_processor.process_segment, par_tasks)
        
        processed_par = [p for p in processed_par if p is not None]
        parallel_time = time.time() - start_par
        par_progress.progress(1.0)
        
        st.success(f"⚡ Parallel: {parallel_time:.1f}s")
        
        # Results
        if parallel_time > 0:
            speedup = sequential_time / parallel_time
            time_saved = sequential_time - parallel_time
            
            st.markdown("## 🏆 Results")
            
            result_html = f"""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 2rem; border-radius: 15px; color: white; text-align: center; margin: 1rem 0;">
                <h2>🏆 PERFORMANCE VICTORY!</h2>
                <h1>{speedup:.2f}x FASTER</h1>
                <p>Saved {time_saved:.1f} seconds with {workers} workers</p>
            </div>
            """
            st.markdown(result_html, unsafe_allow_html=True)
            
            # Record results
            result_data = {
                'sequential_time': sequential_time,
                'parallel_time': parallel_time,
                'speedup': speedup,
                'time_saved': time_saved,
                'workers': workers,
                'segments': len(segments),
                'filter_type': filter_type,
                'video_duration': duration
            }
            monitor.record_processing_result(result_data)
            
            st.balloons()
        
        # Cleanup
        video_processor.cleanup_temp_files(segments)
        if os.path.exists(video_path):
            os.remove(video_path)
            
    except Exception as e:
        st.error(f"Processing failed: {e}")


def run_parallel_processing(video_path: str, filter_type: str, workers: int, segment_duration: float):
    """Run parallel processing only"""
    st.info("⚡ Running parallel processing mode...")


def run_demo_mode(video_path: str, filter_type: str, workers: int):
    """Run demo mode for cloud deployment"""
    st.info("🧪 Running demo mode...")


if __name__ == "__main__":
    main()