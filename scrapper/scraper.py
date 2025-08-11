import os
import requests
from urllib.parse import urljoin
from config_loader import load_config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import urllib.robotparser

class DriverScraper:
    def __init__(self, config_path):
        self.config = load_config(config_path)
        self.allowed_extensions = self.config.get("allowed_extensions", [])
        self.headers = self.config.get("headers", {})
        self.driver = self._initialize_driver()
        self.visited_urls = set()  # Track visited URLs
        self.robot_parsers = {}  # Cache for robots.txt parsers

    def _initialize_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service('/home/anay/Downloads/chromedriver-linux64/chromedriver')  # Update with the correct path to chromedriver
        return webdriver.Chrome(service=service, options=options)

    def _get_robot_parser(self, url):
        from urllib.parse import urlparse, urljoin

        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        if base_url not in self.robot_parsers:
            robots_url = urljoin(base_url, "/robots.txt")
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception:
                parser = None  # If robots.txt cannot be read, ignore it
            self.robot_parsers[base_url] = parser
        return self.robot_parsers[base_url]

    def _is_allowed_by_robots(self, url):
        print(f"Checking robots.txt for {url}")
        parser = self._get_robot_parser(url)
        if parser is None:
            return True  # If robots.txt doesn't exist or cannot be read, allow scraping
        return parser.can_fetch("*", url)

    def scrape_and_download(self):
        print(f"Starting scrape and download...")
        target_urls = self.config.get("target_urls", [])
        for url in target_urls:
            if self._is_allowed_by_robots(url):
                self.crawl(url, depth=0)
            else:
                print(f"Skipping URL due to robots.txt restrictions: {url}")

    def crawl(self, url, depth, max_depth=2):
        print(f"Crawling URL: {url} (Depth: {depth})")
        if depth > max_depth or url in self.visited_urls:
            return

        if not self._is_allowed_by_robots(url):
            print(f"Skipping URL due to robots.txt restrictions: {url}")
            return

        self.visited_urls.add(url)
        self._process_url(url)

        # Extract links to other pages
        page_links = self._extract_page_links()
        for link in page_links:
            self.crawl(link, depth + 1, max_depth)

    def _process_url(self, url):
        print(f"Processing URL: {url}")
        self.driver.get(url)
        try:
            links = self._extract_links()
            for link in links:
                if self._is_valid_file(link):
                    self._download_file(link)
        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    def _extract_links(self):
        # Extract file download links
        elements = self.driver.find_elements(By.TAG_NAME, 'a')
        return [element.get_attribute('href') for element in elements if element.get_attribute('href')]

    def _extract_page_links(self):
        print(f"Extracting page links from current URL")
        # Extract links to other pages (e.g., pagination or related pages)
        elements = self.driver.find_elements(By.TAG_NAME, 'a')
        return [element.get_attribute('href') for element in elements if element.get_attribute('href') and not self._is_valid_file(element.get_attribute('href'))]

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
