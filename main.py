#!/usr/bin/env python3

import sys
import signal
from config import Config
from scraper import DriverScraper
from database import DriverDatabase
from utils import format_bytes, log_progress

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down gracefully...")
    sys.exit(0)

def main():
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize configuration
    config = Config()
    
    # Initialize scraper
    scraper = DriverScraper(config)
    
    try:
        log_progress("Starting driver scraper...")
        
        # Example: scrape specific websites
        target_urls = [
            "https://downloadcenter.intel.com/",
            # Add more URLs as needed
        ]
        
        # Start scraping
        scraper.crawl_multiple_sites(target_urls)
        
        # Print statistics
        db = DriverDatabase(config.db_path)
        stats = db.get_statistics()
        
        log_progress(f"Scraping completed!")
        log_progress(f"Total drivers found: {stats['total_drivers']}")
        log_progress(f"Unique sources: {stats['unique_sources']}")
        log_progress(f"Total size: {format_bytes(stats['total_size_bytes'])}")
        
    except KeyboardInterrupt:
        log_progress("Interrupted by user")
    except Exception as e:
        log_progress(f"Error during execution: {e}", "ERROR")
    finally:
        scraper.cleanup()
        log_progress("Cleanup completed")

if __name__ == "__main__":
    main()

