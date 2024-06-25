import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.connection import allowed_gai_family
import csv
import time
import socket
import json
from datetime import datetime

# Custom function to force the use of IPv6
def force_ipv6():
    def _allowed_gai_family():
        """
        Use AF_INET6 address family (IPv6) for name resolution.
        """
        return socket.AF_INET6
    allowed_gai_family = _allowed_gai_family

# Get the hostname of the machine
hostname = socket.gethostname()

count = 1

# Fetch the host's IPv6 address
host_ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d%H%M%S")

# Define the path to the input CSV file and the error log file
input_csv_path = 'sitesipv6.csv'
error_log_path = f'/home/scripts/log/crawler/{hostname}-{current_date}-crawler-error-log.json'

# Generate the output file name based on hostname and current date
output_file_path = f'/home/scripts/log/crawler/{hostname}-{current_date}-crawler.json'

# Function to ensure URL has http:// or https://
def ensure_scheme(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'https://' + url
    return url

# Force the use of IPv6
force_ipv6()

# Create a session and mount a custom adapter
session = requests.Session()
adapter = HTTPAdapter()
session.mount('http://', adapter)
session.mount('https://', adapter)

# Open the input CSV file and read the websites
with open(input_csv_path, mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    csv_data = list(csv_reader)  # Convert csv_reader to a list
    results = []
    errors = []
    total_rows = len(csv_data)  # Use the converted list in len() function
    for row in csv_data:
        website_id, website_url = row
        website_url = ensure_scheme(website_url)
        try:
            print(f"Processing {website_url} - {count} of {total_rows}...")
            start_time = time.time()
            response = session.get(website_url, timeout=2)  # Set the timeout to 2 seconds
            response_time = time.time() - start_time
            # Include the host's IPv6 address in the result
            results.append({"website_id": website_id, "website_url": website_url, "status_code": response.status_code, "response_time": response_time, "origin_ipv6": host_ipv6})
        except requests.RequestException as e:
            errors.append({"website_id": website_id, "website_url": website_url, "error": str(e)})
        count += 1
# Write the errors to the error log file as JSON
with open(error_log_path, mode='w') as error_file:
    json.dump(errors, error_file, indent=4)

# Write the results to the output file as JSON
with open(output_file_path, mode='w') as output_file:
    json.dump(results, output_file, indent=4)

