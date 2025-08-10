from scraper import DriverScraper

if __name__ == "__main__":
    config_path = "config/example_config.json"  # Path to your configuration file
    scraper = DriverScraper(config_path)
    try:
        scraper.scrape_and_download()
    finally:
        scraper.close()