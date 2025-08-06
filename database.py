import sqlite3
import hashlib
import os
from datetime import datetime

class DriverDatabase:
    def __init__(self, db_path="drivers.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main drivers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS drivers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_type TEXT,
                mime_type TEXT,
                download_url TEXT,
                source_website TEXT,
                device_vendor TEXT,
                device_model TEXT,
                driver_version TEXT,
                os_compatibility TEXT,
                architecture TEXT,
                digital_signature TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sources table to track crawled URLs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                last_crawled TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Driver metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS driver_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_id INTEGER,
                metadata_key TEXT,
                metadata_value TEXT,
                FOREIGN KEY (driver_id) REFERENCES drivers (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_exists(self, file_hash):
        """Check if a file hash already exists in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM drivers WHERE file_hash = ?", (file_hash,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def insert_driver(self, driver_data):
        """Insert new driver record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO drivers (
                    file_hash, filename, file_path, file_size, file_type,
                    mime_type, download_url, source_website, device_vendor,
                    device_model, driver_version, os_compatibility,
                    architecture, digital_signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', driver_data)
            
            driver_id = cursor.lastrowid
            conn.commit()
            return driver_id
        except sqlite3.IntegrityError:
            print(f"Duplicate hash detected: {driver_data[0]}")
            return None
        finally:
            conn.close()
    
    def get_statistics(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM drivers")
        total_drivers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT source_website) FROM drivers")
        unique_sources = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(file_size) FROM drivers")
        total_size = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_drivers': total_drivers,
            'unique_sources': unique_sources,
            'total_size_bytes': total_size
        }

