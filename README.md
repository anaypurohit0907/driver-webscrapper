# Driver Web Scraper

This project is a configurable, manufacturer-agnostic web scraper designed to automate the discovery and download of driver files from various vendor websites. The scraper uses Selenium for web scraping and is highly configurable via external JSON configuration files.

---

## Features

- **Configurable Input**: Specify target URLs, allowed file extensions, and HTTP headers in a JSON configuration file.
- **Web Scraping**: Uses Selenium to extract download links from web pages.
- **File Downloading**: Downloads driver files matching the allowed extensions.
- **Directory Organization**: Saves downloaded files in a structured `downloads/` directory.
- **Error Logging**: Logs errors and skipped files during the scraping process.

---

## Prerequisites

1. **Python 3.7+**: Ensure Python is installed on your system.
2. **Google Chrome**: Install Google Chrome on your system.
3. **ChromeDriver**: Download the appropriate version of ChromeDriver for your Chrome browser from [here](https://sites.google.com/chromium.org/driver/).

---

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd driver-webscrapper/scrapper
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify the `example_config.json` file in the `config/` directory:
   - Update the `target_urls` with the URLs you want to scrape.
   - Ensure the `allowed_extensions` list contains the file types you want to download.
   - Update the `headers` if necessary.

---

## Usage

1. Run the scraper:
   ```bash
   python3 run_scraper.py
   ```

2. Check the `downloads/` directory for the downloaded files.

3. Review the terminal output for logs and errors.

---

## Configuration File (`example_config.json`)

The configuration file specifies the scraping parameters. Example:

```json
{
    "target_urls": [
        "https://www.nvidia.com/en-us/drivers/details/250998/"
    ],
    "allowed_extensions": [
        ".inf", ".sys", ".cat", ".cab", ".zip", ".deb", ".rpm", ".exe", ".msi", ".dmg"
    ],
    "headers": {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0"
    }
}
```

- **`target_urls`**: List of URLs to scrape.
- **`allowed_extensions`**: File extensions to download.
- **`headers`**: HTTP headers for requests.

---

## Directory Structure

```
driver-webscrapper/
├── scrapper/
│   ├── config/
│   │   ├── example_config.json
│   ├── downloads/  # Downloaded files will be saved here
│   ├── scraper.py
│   ├── run_scraper.py
│   ├── config_loader.py
│   ├── metadata_extractor.py
│   ├── validator.py
```

---

## Notes

- Ensure the `chromedriver` path in `scraper.py` is correct:
  ```python
  service = Service('path/to/your/driver')
  ```

- The `downloads/` directory is ignored in version control (see `.gitignore`).

---

## License

This project is licensed under the MIT License.
