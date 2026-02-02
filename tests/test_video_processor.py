"""
Unit tests for VideoProcessor class
"""

import unittest
import numpy as np
import cv2
import os
import tempfile
from src.video_processor import VideoProcessor


class TestVideoProcessor(unittest.TestCase):
    """Test cases for VideoProcessor"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = VideoProcessor(segment_duration=5.0)
        self.test_video_path = self._create_test_video()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_video_path):
            os.remove(self.test_video_path)
    
    def _create_test_video(self):
        """Create a simple test video"""
        # Create temporary video file
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_path, fourcc, 30.0, (640, 480))
        
        # Write 150 frames (5 seconds at 30 FPS)
        for i in range(150):
            # Create a simple colored frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:, :] = [i % 255, (i * 2) % 255, (i * 3) % 255]
            out.write(frame)
        
        out.release()
        return temp_path
    
    def test_get_video_info(self):
        """Test video information extraction"""
        info = self.processor.get_video_info(self.test_video_path)
        
        self.assertIsNotNone(info)
        self.assertEqual(info['width'], 640)
        self.assertEqual(info['height'], 480)
        self.assertAlmostEqual(info['fps'], 30.0, places=1)
        self.assertAlmostEqual(info['duration'], 5.0, places=1)
    
    def test_split_video(self):
        """Test video splitting functionality"""
        segments, duration = self.processor.split_video(self.test_video_path)
        
        self.assertGreater(len(segments), 0)
        self.assertAlmostEqual(duration, 5.0, places=1)
        
        # Check that segment files exist
        for segment in segments:
            self.assertTrue(os.path.exists(segment))
    
    def test_apply_filter_grayscale(self):
        """Test grayscale filter application"""
        # Create test frame
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Apply grayscale filter
        filtered = self.processor.apply_filter(frame, "grayscale")
        
        self.assertEqual(filtered.shape, frame.shape)
        # Check that all channels are equal (grayscale property)
        self.assertTrue(np.allclose(filtered[:,:,0], filtered[:,:,1]))
        self.assertTrue(np.allclose(filtered[:,:,1], filtered[:,:,2]))
    
    def test_apply_filter_brightness(self):
        """Test brightness filter application"""
        # Create test frame
        frame = np.full((100, 100, 3), 100, dtype=np.uint8)
        
        # Apply brightness filter
        filtered = self.processor.apply_filter(frame, "brightness")
        
        self.assertEqual(filtered.shape, frame.shape)
        # Brightness should increase pixel values
        self.assertTrue(np.mean(filtered) > np.mean(frame))
    
    def test_apply_filter_none(self):
        """Test no filter application"""
        # Create test frame
        frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        # Apply no filter
        filtered = self.processor.apply_filter(frame, "none")
        
        # Should be identical
        np.testing.assert_array_equal(frame, filtered)
    
    def test_cleanup_temp_files(self):
        """Test temporary file cleanup"""
        # Create temporary files
        temp_files = []
        for i in range(3):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_files.append(temp_file.name)
            temp_file.close()
        
        # Verify files exist
        for temp_file in temp_files:
            self.assertTrue(os.path.exists(temp_file))
        
        # Clean up
        self.processor.cleanup_temp_files(temp_files)
        
        # Verify files are removed
        for temp_file in temp_files:
            self.assertFalse(os.path.exists(temp_file))


if __name__ == '__main__':
    unittest.main()