#!/usr/bin/env python3
"""
Deployment Verification Script for RenderRush
Checks if all required files and dependencies are properly configured for Streamlit Cloud deployment.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_requirements():
    """Check requirements.txt content"""
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_packages = [
        'streamlit',
        'opencv-python-headless',
        'plotly',
        'pandas',
        'numpy',
        'psutil'
    ]
    
    missing = []
    for package in required_packages:
        if package not in content:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages in requirements.txt: {', '.join(missing)}")
        return False
    else:
        print("✅ All required packages found in requirements.txt")
        return True

def check_packages_txt():
    """Check packages.txt for system dependencies"""
    if not os.path.exists('packages.txt'):
        print("❌ packages.txt not found")
        return False
    
    with open('packages.txt', 'r') as f:
        content = f.read()
    
    required_packages = ['ffmpeg', 'libsm6', 'libxext6']
    
    missing = []
    for package in required_packages:
        if package not in content:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing system packages: {', '.join(missing)}")
        return False
    else:
        print("✅ All required system packages found in packages.txt")
        return True

def main():
    """Main verification function"""
    print("🚀 RenderRush Deployment Verification")
    print("=" * 50)
    
    all_good = True
    
    # Check essential files
    files_to_check = [
        ('streamlit_app.py', 'Streamlit Cloud entry point'),
        ('main.py', 'Local development entry point'),
        ('src/video_processor.py', 'Video processing module'),
        ('src/performance_monitor.py', 'Performance monitoring module'),
        ('src/ui_components.py', 'UI components module'),
        ('src/ai_optimizer.py', 'AI optimizer module'),
        ('.streamlit/config.toml', 'Streamlit configuration'),
        ('README.md', 'Documentation')
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False
    
    # Check requirements
    if not check_requirements():
        all_good = False
    
    # Check system packages
    if not check_packages_txt():
        all_good = False
    
    # Check directory structure
    required_dirs = ['src', 'uploads', 'output', 'temp_processing']
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"⚠️  Directory will be created on first run: {directory}")
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 DEPLOYMENT READY!")
        print("✅ All files and dependencies are properly configured")
        print("🌐 Ready for Streamlit Cloud deployment")
        print("\nNext steps:")
        print("1. Push to GitHub repository")
        print("2. Deploy on share.streamlit.io")
        print("3. Set main file path to: streamlit_app.py")
    else:
        print("❌ DEPLOYMENT ISSUES FOUND")
        print("Please fix the issues above before deploying")
        sys.exit(1)

if __name__ == "__main__":
    main()