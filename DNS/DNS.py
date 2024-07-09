import os
import socket
import datetime
import json

import dns.resolver

# Ensure the directory exists
log_directory = "/home/ubuntu/log/DNS"
os.makedirs(log_directory, exist_ok=True)

count = 1

# Get hostname and current datetime
hostname = socket.gethostname()
current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Filename format: hostname-currentdatetime-DNS.json, saved in the specified directory
filename = f"{log_directory}/{hostname}-{current_datetime}-DNS.json"

# Read DNS servers from a text file
with open("nameservers.txt", "r") as file:
    dns_servers = file.readlines()

# Initialize a dictionary to store the results
dns_results = {}

# Get the IPv6 address of the host
host_ipv6 = None
try:
    host_ipv6 = [ip[4][0] for ip in socket.getaddrinfo(hostname, None, socket.AF_INET6) if ip[0] == socket.AF_INET6][0]
except Exception as e:
    host_ipv6 = f"Error getting host IPv6: {e}"

# Collect DNS query results using only IPv6
for server in dns_servers:
    server = server.strip()
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    dns_results[server] = {"results": [], "host_ipv6": host_ipv6, "timestamp": str(datetime.datetime.now())}  # Initialize server entry in dictionary with timestamp
    try:
        print(f"Processing {server} - {count} of {len(dns_servers)}...")
        # Perform an "AAAA" query to get IPv6 addresses
        answers = resolver.resolve("google.com", "AAAA")
        for rdata in answers:
            dns_results[server]["results"].append(str(rdata))  # Add successful query results
    except Exception as e:
        dns_results[server]["results"].append(f"Error: {e}")  # Log any errors
    count += 1

# Open the JSON file for writing and dump the dictionary into it
with open(filename, "w") as json_file:
    json.dump(dns_results, json_file, indent=4)  # Write the dictionary to the file in JSON format
