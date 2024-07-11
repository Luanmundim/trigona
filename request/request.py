import requests
from requests.adapters import HTTPAdapter
import csv
import time
import socket
import json
from datetime import datetime
import os

# Get the hostname of the machine
hostname = socket.gethostname()

count = 1

# Fetch the host's IPv6 address
host_ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d%H%M%S")

# Define the path to the input CSV file and the error log file
input_csv_path = 'internalIP.csv'
# Create the directory if it doesn't exist
directory = '/home/ubuntu/log/request'
if not os.path.exists(directory):
    os.makedirs(directory)

error_log_path = f'{directory}/{hostname}-{current_date}-request-error-log.json'

# Generate the output file name based on hostname and current date
output_file_path = f'/home/ubuntu/log/request/{hostname}-{current_date}-request.json'

# Function to ensure URL has http:// or https://
def ensure_scheme(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        return 'https://' + url
    return url

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
        ipv6_address = row[1]
        try:
            print(f"Processing {ipv6_address} - {count} of {total_rows}...")
            start_time = time.time()
            response = session.get(f'http://[{ipv6_address}]', timeout=2)  # Set the timeout to 2 seconds
            response_time = time.time() - start_time
            # Include the host's IPv6 address and timestamp in the result
            results.append({"ipv6_address": ipv6_address, "status_code": response.status_code, "response_time": response_time, "origin_ipv6": host_ipv6, "timestamp": datetime.now().isoformat()})
        except requests.RequestException as e:
            errors.append({"ipv6_address": ipv6_address, "error": str(e), "timestamp": datetime.now().isoformat()})
        count += 1
# Write the errors to the error log file as JSON
with open(error_log_path, mode='w') as error_file:
    json.dump(errors, error_file, indent=4)

# Write the results to the output file as JSON
with open(output_file_path, mode='w') as output_file:
    json.dump(results, output_file, indent=4)
