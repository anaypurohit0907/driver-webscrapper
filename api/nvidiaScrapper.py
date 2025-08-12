from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import time

start_id = 11
end_id = 252782
base_url = "https://www.nvidia.com/en-us/drivers/details/{}/"

# Setup Chrome options (headless for speed)
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

for driver_id in range(start_id, end_id + 1):
    url = base_url.format(driver_id)
    try:
        driver.get(url)
        time.sleep(1)  # small delay to let page load

        try:
            # The NVIDIA "Download" button usually has this class
            download_button = driver.find_element(By.XPATH, "//a[contains(text(),'Download')]")
            download_link = download_button.get_attribute("href")

            print(f"[OK] {driver_id} → {download_link}")
        except NoSuchElementException:
            print(f"[NO LINK] {driver_id}")

    except (TimeoutException, WebDriverException) as e:
        print(f"[ERROR] {driver_id} - {e}")

driver.quit()
