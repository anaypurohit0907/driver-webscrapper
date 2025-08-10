import os
import requests
from urllib.parse import urljoin
from config_loader import load_config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class DriverScraper:
    def __init__(self, config_path):
        self.config = load_config(config_path)
        self.allowed_extensions = self.config.get("allowed_extensions", [])
        self.headers = self.config.get("headers", {})
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service('path/to/the/driver/file(not folder the filename too)')  # Update with the correct path to chromedriver
        return webdriver.Chrome(service=service, options=options)

    def scrape_and_download(self):
        target_urls = self.config.get("target_urls", [])
        for url in target_urls:
            self._process_url(url)

    def _process_url(self, url):
        self.driver.get(url)
        try:
            links = self._extract_links()
            for link in links:
                if self._is_valid_file(link):
                    self._download_file(link)
        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    def _extract_links(self):
        # Example: Extract all anchor tags with href attributes
        elements = self.driver.find_elements(By.TAG_NAME, 'a')
        return [element.get_attribute('href') for element in elements if element.get_attribute('href')]

    def _is_valid_file(self, link):
        return any(link.endswith(ext) for ext in self.allowed_extensions)

    def _download_file(self, link):
        local_filename = os.path.join("downloads", os.path.basename(link))
        os.makedirs(os.path.dirname(local_filename), exist_ok=True)

        with requests.get(link, stream=True) as response:
            if response.status_code == 200:
                with open(local_filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                print(f"Downloaded: {local_filename}")
            else:
                print(f"Failed to download: {link}")

    def close(self):
        self.driver.quit()
