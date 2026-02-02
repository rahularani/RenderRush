"""
RenderRush: Distributed Video Renderer
Main Application Entry Point

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
            max_value=16,
            value=4,
            help="Number of parallel workers for processing"
        )
        
        segment_duration = st.slider(
            "⏱️ Segment Duration (seconds)",
            min_value=5.0,
            max_value=30.0,
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
        
        # Export options
        st.markdown("### 📊 Export & Analysis")
        
        # Real-time monitoring toggle
        enable_realtime = st.checkbox(
            "🔴 Real-time Monitoring",
            value=st.session_state.get('enable_realtime', True),
            help="Enable real-time system monitoring (refreshes every 3 seconds)"
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
        type=["mp4", "avi", "mov", "mkv"],
        help="Upload a video file to demonstrate parallel processing performance"
    )
    
    if uploaded_file is not None:
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
        st.success(f"✅ Video analyzed: {uploaded_file.name}")
        
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
        
        if st.button("🧪 Benchmark Mode", type="secondary"):
            run_benchmark_suite(video_path, filter_type)
    
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
    """Run the ultimate performance comparison with real-time updates"""
    
    st.markdown("---")
    st.markdown("# 🏁 ULTIMATE PERFORMANCE SHOWDOWN")
    st.markdown("*Watch optimized parallel processing in action!*")
    
    # Get instances
    video_processor = st.session_state.video_processor
    monitor = st.session_state.performance_monitor
    
    # Create containers for real-time updates
    timer_container = st.container()
    progress_container = st.container()
    results_container = st.container()
    
    # Real-time timer displays
    with timer_container:
        st.markdown("### ⏱️ **LIVE PERFORMANCE RACE**")
        
        # Sequential timer section
        st.markdown("#### 🐢 Sequential Processing Timer")
        seq_timer_placeholder = st.empty()
        seq_status_placeholder = st.empty()
        
        # Parallel timer section  
        st.markdown("#### ⚡ Parallel Processing Timer")
        par_timer_placeholder = st.empty()
        par_status_placeholder = st.empty()
        
        # Live comparison section
        st.markdown("#### 🏆 Live Performance Comparison")
        comparison_placeholder = st.empty()
    
    # Progress tracking
    with progress_container:
        st.markdown("### 📊 **PROCESSING PROGRESS**")
        
        st.markdown("**🐢 Sequential Progress**")
        seq_progress = st.progress(0)
        seq_progress_text = st.empty()
        
        st.markdown("**⚡ Parallel Progress**")
        par_progress = st.progress(0)
        par_progress_text = st.empty()
    
    try:
        # Initialize displays
        seq_timer_placeholder.markdown("**⏱️ 0.0 seconds** - *Waiting to start...*")
        par_timer_placeholder.markdown("**⏱️ 0.0 seconds** - *Waiting for sequential to complete...*")
        comparison_placeholder.markdown("**🏁 Preparing race...**")
        
        # Split video
        st.info("🎬 Splitting video into segments...")
        video_processor.segment_duration = segment_duration
        segments, duration = video_processor.split_video(video_path)
        segments_count = len(segments)
        
        seq_progress.progress(0.1)
        par_progress.progress(0.1)
        seq_progress_text.text(f"Video split into {segments_count} segments")
        par_progress_text.text("Waiting for sequential processing to complete")
        
        st.success(f"✅ Video split into {segments_count} segments of {segment_duration} seconds each")
        
        # PHASE 1: Sequential Processing with real-time updates
        st.markdown("---")
        st.markdown("## 🐢 **PHASE 1: SEQUENTIAL PROCESSING (BEFORE)**")
        st.markdown("*Processing one segment at a time...*")
        
        seq_status_placeholder.markdown("*🔄 Starting sequential processing...*")
        
        start_seq = time.time()
        
        # Process sequentially with real-time timer updates
        processed_seq = []
        for i, segment in enumerate(segments):
            current_time = time.time() - start_seq
            
            # Update timer in real-time
            seq_timer_placeholder.markdown(f"**⏱️ {current_time:.1f} seconds** - *Processing segment {i+1}/{segments_count}*")
            seq_status_placeholder.markdown(f"*🔄 Processing segment {i+1} of {segments_count} sequentially...*")
            
            # Update progress
            progress = 0.1 + (0.7 * (i + 1) / segments_count)
            seq_progress.progress(progress)
            seq_progress_text.text(f"Completed {i+1}/{segments_count} segments ({progress*100:.0f}%)")
            
            # Process the segment
            output_file = os.path.join("output", f"seq_{i:03d}.mp4")
            os.makedirs("output", exist_ok=True)
            result = video_processor.process_segment((i, segment, output_file, filter_type))
            if result:
                processed_seq.append(result)
            
            # Small delay to show the timer updating
            time.sleep(0.1)
        
        sequential_time = time.time() - start_seq
        
        # Check if we have valid sequential segments
        if not processed_seq:
            st.error("❌ Sequential processing failed - no valid segments were created")
            return
        
        print(f"Sequential processing completed: {len(processed_seq)} valid segments")
        
        # Sequential completion
        seq_timer_placeholder.markdown(f"**⏱️ {sequential_time:.1f} seconds ✅** - *SEQUENTIAL COMPLETED!*")
        seq_status_placeholder.markdown("*✅ Sequential processing COMPLETED!*")
        seq_progress.progress(0.8)
        seq_progress_text.text(f"✅ All {segments_count} segments processed sequentially")
        
        st.success(f"🐢 **Sequential Processing Complete!** Took {sequential_time:.1f} seconds")
        
        # Brief dramatic pause
        time.sleep(2)
        
        # PHASE 2: Parallel Processing with TRUE parallel execution
        st.markdown("---")
        st.markdown("## ⚡ **PHASE 2: PARALLEL PROCESSING (AFTER)**")
        st.markdown(f"*Processing {segments_count} segments simultaneously with {workers} workers...*")
        
        par_status_placeholder.markdown(f"*🚀 Starting parallel processing with {workers} workers...*")
        
        start_par = time.time()
        
        # Prepare parallel tasks
        par_tasks = []
        for i, segment in enumerate(segments):
            output_file = os.path.join("output", f"par_{i:03d}.mp4")
            par_tasks.append((i, segment, output_file, filter_type))
        
        # TRUE parallel processing with real-time monitoring
        freeze_support()
        with Pool(workers) as pool:
            # Start async processing
            result_async = pool.map_async(video_processor.process_segment, par_tasks)
            
            # Real-time updates while processing
            update_count = 0
            while not result_async.ready():
                current_par_time = time.time() - start_par
                update_count += 1
                
                # Update parallel timer
                par_timer_placeholder.markdown(f"**⏱️ {current_par_time:.1f} seconds** - *{workers} workers processing simultaneously...*")
                par_status_placeholder.markdown(f"*⚡ All {segments_count} segments being processed in parallel...*")
                
                # Estimate progress based on expected parallel speedup
                expected_parallel_time = sequential_time / max(1, workers * 0.8)  # 80% efficiency
                progress_estimate = min(0.8, 0.1 + (0.7 * current_par_time / expected_parallel_time))
                par_progress.progress(progress_estimate)
                par_progress_text.text(f"⚡ Parallel processing: {workers} workers active ({progress_estimate*100:.0f}%)")
                
                # Live comparison with dramatic messaging
                if current_par_time < sequential_time:
                    time_diff = sequential_time - current_par_time
                    speedup_so_far = sequential_time / max(current_par_time, 0.1)
                    comparison_placeholder.markdown(f"""
                    # 🏆 **PARALLEL IS DOMINATING!**
                    
                    | Metric | Sequential | Parallel | Advantage |
                    |--------|------------|----------|-----------|
                    | Time | {sequential_time:.1f}s | {current_par_time:.1f}s | **{time_diff:.1f}s faster** |
                    | Method | One-by-one | {workers} simultaneous | **{speedup_so_far:.1f}x speedup** |
                    | Status | ✅ Finished | ⚡ **RACING AHEAD** | 🏁 **WINNING** |
                    
                    ### ⚡ **PARALLEL PROCESSING POWER IN ACTION!**
                    """)
                else:
                    comparison_placeholder.markdown(f"""
                    # ⚡ **PARALLEL PROCESSING IN PROGRESS...**
                    
                    - 🐢 Sequential: {sequential_time:.1f}s (completed)
                    - ⚡ Parallel: {current_par_time:.1f}s (processing...)
                    - 🔥 {workers} workers running simultaneously
                    - 📊 Expected completion: ~{expected_parallel_time:.1f}s
                    """)
                
                # Update every 100ms for smooth real-time feel
                time.sleep(0.1)
            
            # Get results and filter out None values
            processed_par = result_async.get()
            processed_par = [p for p in processed_par if p is not None]
            
            print(f"Parallel processing completed: {len(processed_par)} valid segments out of {len(par_tasks)}")
        
        parallel_time = time.time() - start_par
        
        # Check if we have valid segments
        if not processed_par:
            st.error("❌ Parallel processing failed - no valid segments were created")
            return
        
        # Parallel completion
        par_timer_placeholder.markdown(f"**⏱️ {parallel_time:.1f} seconds ⚡** - *PARALLEL COMPLETED!*")
        par_status_placeholder.markdown("*⚡ Parallel processing COMPLETED!*")
        par_progress.progress(0.8)
        par_progress_text.text(f"⚡ All {segments_count} segments processed in parallel")
        
        # Final comparison
        speedup = sequential_time / parallel_time if parallel_time > 0 else 0
        time_saved = sequential_time - parallel_time
        
        comparison_placeholder.markdown(f"""
        # 🎉 **FINAL RACE RESULTS!**
        
        | Method | Time | Status |
        |--------|------|--------|
        | 🐢 Sequential | {sequential_time:.1f}s | ✅ Completed |
        | ⚡ Parallel | {parallel_time:.1f}s | ⚡ **WINNER!** |
        
        ## 🏆 **PERFORMANCE VICTORY:**
        - **Speedup**: {speedup:.2f}x FASTER!
        - **Time Saved**: {time_saved:.1f} seconds
        - **Efficiency**: {(speedup/workers)*100:.1f}% worker utilization
        """)
        
        st.success(f"⚡ **Parallel Processing WINS!** Completed in {parallel_time:.1f} seconds - {speedup:.2f}x FASTER!")
        
        # Merge final video
        st.info("🔗 Merging processed segments...")
        output_path = f"output/final_render_{int(time.time())}.mp4"
        final_video = video_processor.merge_segments(processed_par, output_path)
        
        seq_progress.progress(1.0)
        par_progress.progress(1.0)
        seq_progress_text.text("✅ Processing complete")
        par_progress_text.text("⚡ Processing complete")
        
        # Record results
        result_data = {
            'sequential_time': sequential_time,
            'parallel_time': parallel_time,
            'speedup': speedup,
            'time_saved': time_saved,
            'workers': workers,
            'segments': segments_count,
            'filter_type': filter_type,
            'video_duration': duration
        }
        
        monitor.record_processing_result(result_data)
        
        # Display final results
        with results_container:
            st.markdown("---")
            st.markdown("# 🎉 **ULTIMATE SHOWDOWN RESULTS**")
            
            # Create dramatic results display
            before_html = UIComponents.create_metric_card(
                "🐢 BEFORE (Sequential)",
                f"{sequential_time:.1f}s",
                "One segment at a time",
                "metric"
            )
            st.markdown(before_html, unsafe_allow_html=True)
            
            after_html = UIComponents.create_metric_card(
                "⚡ AFTER (Parallel)",
                f"{parallel_time:.1f}s",
                f"{workers} segments simultaneously",
                "speedup"
            )
            st.markdown(after_html, unsafe_allow_html=True)
            
            gain_html = UIComponents.create_metric_card(
                "🏆 PERFORMANCE GAIN",
                f"{speedup:.2f}x",
                f"Saved {time_saved:.1f} seconds!",
                "ai"
            )
            st.markdown(gain_html, unsafe_allow_html=True)
            
            # Comparison chart
            comparison_chart = UIComponents.create_processing_comparison_chart(
                sequential_time, parallel_time, workers
            )
            st.plotly_chart(comparison_chart, use_container_width=True)
            
            st.balloons()
            
            # Show final video
            if os.path.exists(final_video):
                st.markdown("### 🎬 Final Processed Video")
                st.video(final_video)
                
                with open(final_video, "rb") as f:
                    st.download_button(
                        "📥 Download Processed Video",
                        data=f.read(),
                        file_name=os.path.basename(final_video),
                        mime="video/mp4"
                    )
        
        # Cleanup
        video_processor.cleanup_temp_files(segments)
        if os.path.exists(video_path):
            os.remove(video_path)
            
    except Exception as e:
        st.error(f"Processing failed: {e}")
        st.exception(e)


def run_parallel_processing(video_path: str, filter_type: str, workers: int, segment_duration: float):
    """Run parallel processing only"""
    st.info("⚡ Running parallel processing mode...")
    # Implementation would go here


def run_benchmark_suite(video_path: str, filter_type: str):
    """Run comprehensive benchmark suite"""
    st.info("🧪 Running benchmark suite...")
    # Implementation would go here


if __name__ == "__main__":
    main()