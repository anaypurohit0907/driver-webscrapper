import os

class Config:
    def __init__(self):
        # Database settings
        self.db_path = "drivers.db"
        
        # Download settings
        self.download_dir = os.path.abspath("downloads")
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Scraping settings
        self.headless = False  # Set to True for headless browsing
        self.delay_between_sites = 2  # seconds
        self.download_timeout = 60  # seconds
        self.keep_non_drivers = False  # Whether to keep files that aren't drivers
        
        # Target websites (example list)
        self.target_websites = [
            "https://downloadcenter.intel.com/",
            "https://www.nvidia.com/drivers/",
            "https://www.amd.com/support/",
            # Add more driver websites
        ]
        
        # File type settings
        self.supported_archives = {'.zip', '.rar', '.7z', '.tar', '.gz'}
        self.driver_keywords = [
            'driver', 'drivers', 'drv', 'device', 'hardware',
            'adapter', 'controller', 'chipset', 'firmware'
        ]

