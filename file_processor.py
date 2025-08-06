import hashlib
import magic
import os
import re
import zipfile
import tarfile
from pathlib import Path

class FileProcessor:
    def __init__(self):
        self.driver_extensions = {
            '.sys', '.inf', '.dll', '.exe', '.msi', '.cab', 
            '.ko', '.deb', '.rpm', '.pkg'
        }
        self.archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz'}
    
    def calculate_hash(self, file_path, algorithm='sha256'):
        """Calculate file hash using specified algorithm"""
        hash_func = getattr(hashlib, algorithm)()
        
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files efficiently
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def get_file_type(self, file_path):
        """Determine file type using python-magic"""
        try:
            # Get human-readable file type
            file_type = magic.from_file(file_path)
            # Get MIME type
            mime_type = magic.from_file(file_path, mime=True)
            return file_type, mime_type
        except Exception as e:
            print(f"Error determining file type for {file_path}: {e}")
            return None, None
    
    def is_driver_file(self, file_path, filename=""):
        """Determine if a file is likely a driver file"""
        # Check by extension
        file_ext = Path(file_path).suffix.lower()
        if file_ext in self.driver_extensions:
            return True
        
        # Check by filename patterns
        driver_keywords = [
            'driver', 'drv', 'inf', 'sys', 'device', 'hardware',
            'adapter', 'controller', 'chipset'
        ]
        
        filename_lower = filename.lower()
        if any(keyword in filename_lower for keyword in driver_keywords):
            return True
        
        # Check file content for driver signatures
        try:
            file_type, mime_type = self.get_file_type(file_path)
            if file_type and any(sig in file_type.lower() for sig in 
                               ['driver', 'inf', 'executable']):
                return True
        except:
            pass
        
        return False
    
    def extract_driver_metadata(self, file_path):
        """Extract driver-specific metadata"""
        metadata = {}
        
        try:
            # For Windows PE files, extract version info
            if file_path.endswith('.exe') or file_path.endswith('.sys'):
                metadata.update(self._extract_pe_metadata(file_path))
            
            # For INF files, parse driver information
            elif file_path.endswith('.inf'):
                metadata.update(self._extract_inf_metadata(file_path))
            
            # For Linux kernel modules
            elif file_path.endswith('.ko'):
                metadata.update(self._extract_ko_metadata(file_path))
        
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
        
        return metadata
    
    def _extract_pe_metadata(self, file_path):
        """Extract metadata from PE (Portable Executable) files"""
        metadata = {}
        # This would require additional libraries like pefile
        # For now, return basic information
        try:
            import pefile
            pe = pefile.PE(file_path)
            
            if hasattr(pe, 'VS_VERSIONINFO'):
                version_info = pe.VS_VERSIONINFO
                if hasattr(version_info, 'StringFileInfo'):
                    for entry in version_info.StringFileInfo:
                        for string_entry in entry.StringTable:
                            metadata[string_entry.key] = string_entry.value
        except ImportError:
            print("pefile library not installed - PE metadata extraction disabled")
        except Exception as e:
            print(f"Error extracting PE metadata: {e}")
        
        return metadata
    
    def _extract_inf_metadata(self, file_path):
        """Extract metadata from INF files"""
        metadata = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract common INF file sections
                patterns = {
                    'Class': r'Class\s*=\s*([^\r\n]+)',
                    'Provider': r'Provider\s*=\s*([^\r\n]+)',
                    'DriverVer': r'DriverVer\s*=\s*([^\r\n]+)',
                    'CatalogFile': r'CatalogFile\s*=\s*([^\r\n]+)'
                }
                
                for key, pattern in patterns.items():
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        metadata[key] = match.group(1).strip()
        
        except Exception as e:
            print(f"Error parsing INF file {file_path}: {e}")
        
        return metadata
    
    def _extract_ko_metadata(self, file_path):
        """Extract metadata from Linux kernel modules"""
        metadata = {}
        
        try:
            # Use modinfo command if available
            import subprocess
            result = subprocess.run(['modinfo', file_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
        except:
            pass
        
        return metadata

