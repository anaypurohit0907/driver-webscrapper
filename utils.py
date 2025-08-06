import os
import time
from pathlib import Path

def clean_filename(filename):
    """Clean filename to remove invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def format_bytes(bytes_value):
    """Format bytes into human readable format"""
    if bytes_value == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    
    while bytes_value >= 1024 and size_index < len(size_names) - 1:
        bytes_value /= 1024.0
        size_index += 1
    
    return f"{bytes_value:.2f} {size_names[size_index]}"

def monitor_downloads(download_dir, timeout=60):
    """Monitor download directory for new files"""
    initial_files = set(os.listdir(download_dir))
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        
        # Filter out temporary files
        completed_files = []
        for filename in new_files:
            file_path = os.path.join(download_dir, filename)
            if (not filename.endswith('.crdownload') and 
                not filename.endswith('.tmp') and 
                os.path.exists(file_path)):
                completed_files.append(file_path)
        
        if completed_files:
            return completed_files
        
        time.sleep(1)
    
    return []

def log_progress(message, level="INFO"):
    """Simple logging function"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

