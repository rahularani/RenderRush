"""
Video Processing Module
Handles video segmentation, processing, and merging operations
"""

import cv2
import numpy as np
import os
import time
from multiprocessing import Pool, freeze_support
from typing import List, Tuple, Dict, Any


class VideoProcessor:
    """Core video processing engine using OpenCV"""
    
    def __init__(self, segment_duration: float = 10.0):
        self.segment_duration = segment_duration
        self.temp_dir = "temp_processing"
        self.output_dir = "output"
        
        # Ensure directories exist
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata using OpenCV"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'fps': fps,
            'frame_count': frame_count,
            'width': width,
            'height': height,
            'duration': duration,
            'file_size': os.path.getsize(video_path) if os.path.exists(video_path) else 0
        }
    
    def split_video(self, video_path: str) -> Tuple[List[str], float]:
        """Split video into segments for parallel processing - optimized for speed"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        
        print(f"Video info: {duration:.1f}s, {total_frames} frames, {fps:.1f} FPS")
        
        segments = []
        segment_count = int(np.ceil(duration / self.segment_duration))
        frames_per_segment = int(fps * self.segment_duration)
        
        # Use mp4v codec for better compatibility
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        for i in range(segment_count):
            start_frame = i * frames_per_segment
            end_frame = min((i + 1) * frames_per_segment, total_frames)
            
            segment_file = os.path.join(self.temp_dir, f"segment_{i:03d}.mp4")
            
            # Create video writer for this segment
            out = cv2.VideoWriter(
                segment_file, fourcc, fps, 
                (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                 int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            )
            
            if not out.isOpened():
                print(f"Error: Cannot create segment file {segment_file}")
                continue
            
            # Set to start frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            # Write frames for this segment
            frames_written = 0
            for frame_idx in range(start_frame, end_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                
                out.write(frame)
                frames_written += 1
                
                # Break if we've written enough frames
                if frames_written >= frames_per_segment:
                    break
            
            out.release()
            
            # Verify segment was created successfully
            if os.path.exists(segment_file) and os.path.getsize(segment_file) > 1000:
                segments.append(segment_file)
                print(f"Created segment {i}: {frames_written} frames")
            else:
                print(f"Failed to create segment {i}")
        
        cap.release()
        print(f"Successfully created {len(segments)} segments")
        return segments, duration
    
    def apply_filter(self, frame: np.ndarray, filter_type: str) -> np.ndarray:
        """Apply video filter to a single frame - optimized for speed"""
        if filter_type == "grayscale":
            # Fast grayscale conversion
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        elif filter_type == "blur":
            # Light blur for speed
            return cv2.GaussianBlur(frame, (5, 5), 0)
        elif filter_type == "brightness":
            # Fast brightness adjustment
            return cv2.convertScaleAbs(frame, alpha=1.3, beta=20)
        elif filter_type == "contrast":
            # Fast contrast adjustment
            return cv2.convertScaleAbs(frame, alpha=1.5, beta=0)
        else:
            return frame
    
    def process_segment(self, args: Tuple) -> str:
        """Process a single video segment with specified filter - optimized"""
        segment_id, input_file, output_file, filter_type = args
        
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            cap = cv2.VideoCapture(input_file)
            if not cap.isOpened():
                print(f"Error: Cannot open input file {input_file}")
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if fps <= 0 or width <= 0 or height <= 0:
                print(f"Error: Invalid video properties for segment {segment_id}")
                cap.release()
                return None
            
            # Use mp4v codec for better compatibility
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
            
            if not out.isOpened():
                print(f"Error: Cannot create output file {output_file}")
                cap.release()
                return None
            
            frame_count = 0
            processed_frames = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply filter - simplified for reliability
                if filter_type == "grayscale":
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    processed_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                elif filter_type == "blur":
                    processed_frame = cv2.GaussianBlur(frame, (5, 5), 0)
                elif filter_type == "brightness":
                    processed_frame = cv2.convertScaleAbs(frame, alpha=1.3, beta=20)
                elif filter_type == "contrast":
                    processed_frame = cv2.convertScaleAbs(frame, alpha=1.5, beta=0)
                else:
                    processed_frame = frame
                
                out.write(processed_frame)
                frame_count += 1
                processed_frames += 1
            
            cap.release()
            out.release()
            
            # Verify the output file was created and has content
            if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:  # At least 1KB
                print(f"Successfully processed segment {segment_id}: {processed_frames} frames")
                return output_file
            else:
                print(f"Error: Output file {output_file} is invalid or too small")
                return None
            
        except Exception as e:
            print(f"Error processing segment {segment_id}: {e}")
            return None
    
    def process_sequential(self, segments: List[str], filter_type: str) -> Tuple[List[str], float]:
        """Process segments sequentially"""
        start_time = time.time()
        processed_segments = []
        
        for i, segment in enumerate(segments):
            output_file = os.path.join(self.output_dir, f"seq_{i:03d}.mp4")
            result = self.process_segment((i, segment, output_file, filter_type))
            processed_segments.append(result)
        
        processing_time = time.time() - start_time
        return processed_segments, processing_time
    
    def process_parallel(self, segments: List[str], filter_type: str, workers: int) -> Tuple[List[str], float]:
        """Process segments in parallel"""
        start_time = time.time()
        
        # Prepare tasks
        tasks = []
        for i, segment in enumerate(segments):
            output_file = os.path.join(self.output_dir, f"par_{i:03d}.mp4")
            tasks.append((i, segment, output_file, filter_type))
        
        # Process in parallel
        freeze_support()
        with Pool(workers) as pool:
            processed_segments = pool.map(self.process_segment, tasks)
        
        processing_time = time.time() - start_time
        return processed_segments, processing_time
    
    def merge_segments(self, segments: List[str], output_path: str) -> str:
        """Merge processed segments into final video - optimized"""
        valid_segments = [s for s in segments if s and os.path.exists(s)]
        
        if not valid_segments:
            raise ValueError("No valid segments to merge")
        
        # Get video properties from first segment
        cap = cv2.VideoCapture(valid_segments[0])
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        # Use mp4v for final output
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for segment in valid_segments:
            cap = cv2.VideoCapture(segment)
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                frame_count += 1
            cap.release()
        
        out.release()
        return output_path
    
    def cleanup_temp_files(self, files: List[str]):
        """Clean up temporary files"""
        for file_path in files:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Warning: Could not remove temp file {file_path}: {e}")