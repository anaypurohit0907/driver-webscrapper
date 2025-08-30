## Overview

- Input: A CSV file (manufacturers.csv) containing manufacturer names and URLs.

- Task: Visit each manufacturer’s webpage to check if it contains links to downloadable device drivers.

- Output: A filtered CSV file (manufacturers_temp.csv) containing only manufacturers whose pages include device driver links.

## Key Features

- Uses requests and BeautifulSoup to fetch and parse HTML pages.

- Detects device links by looking for <ul> lists within <div> containers of classes grid_4 alpha or grid_4 omega, as these contain product links.

- Adds a custom User-Agent header to mimic a real browser for better acceptance by servers.

- Implements a configurable delay between requests (default 5 to 15 seconds) to minimize risk of IP throttling or bans.

- Supports resuming progress: if interrupted, it reads the temp CSV to skip already processed manufacturers and appends new results (but remember to change the start line variable in the rem.py file).

## Usage notes

- Adjust the sleep_seconds variable to manage crawling speed depending on server tolerance.

- check from which line you need to start in the rem.py start_line variable

- make sure you have manufacturer.csv

- you dont need to run main.py if you have the manufacturer.csv file, main.py just genenrates manufacturer.csv

- each IP will work for around 400 links (around 1.5 to 2 hours) checking and then all your requests will be timed out, when that happens please <ctrl+c> interrupt the program, note your progress and change your ip then after modifying the start_line variable to match the last working requests in your cmd continue
