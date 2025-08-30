import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import random

def has_device_links(url, timeout=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for div_class in ['grid_4 alpha', 'grid_4 omega']:
            div = soup.find('div', class_=div_class)
            if div:
                ul = div.find('ul')
                if ul and ul.find('li'):
                    return True
        return False
    except requests.exceptions.Timeout:
        print(f"  -> Timeout while accessing {url}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"  -> Request failed: {e}")
        return False

input_csv = 'manufacturers.csv'
temp_csv = 'manufacturers_temp.csv'
sleep_seconds = random.randrange(5,15)  # adjust to prevent throttling
start_line = 1060   # line number to start reading from (1 = header line)

# Load already processed manufacturers from temp file to skip them
processed_manufacturers = set()
if os.path.exists(temp_csv):
    with open(temp_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            processed_manufacturers.add(row['Manufacturer'])

with open(input_csv, newline='', encoding='utf-8') as infile, \
     open(temp_csv, 'a', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=['Manufacturer', 'Link'])
    # Write header if temp file did not exist or is empty
    if os.path.getsize(temp_csv) == 0:
        writer.writeheader()

    total = sum(1 for _ in open(input_csv)) - 1  # total input rows excluding header
    current_count = len(processed_manufacturers)
    print(f"Resuming from {current_count} processed entries out of {total}")

    # Skip rows before start_line - 1 (excluding header)
    rows_to_skip = start_line - 2  # because header is line 1
    for _ in range(rows_to_skip):
        next(reader)

    for idx, row in enumerate(reader, start=start_line):
        if row['Manufacturer'] in processed_manufacturers:
            continue  # Skip already processed

        url = row['Link']
        print(f"Checking ({idx}/{total}): {row['Manufacturer']}")
        if has_device_links(url):
            writer.writerow(row)
            print(f"  -> Device links found, kept.")
        else:
            print(f"  -> No device links found, skipped.")
        processed_manufacturers.add(row['Manufacturer'])  # update processed set
        time.sleep(sleep_seconds)
