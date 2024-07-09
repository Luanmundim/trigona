#!/bin/bash

# Generate a timestamp
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Ensure the directory exists
mkdir -p "/home/ubuntu/log/tcpdump/"

# Run tcpdump and save the output
tcpdump -i eth0 > "/home/ubuntu/log/tcpdump/${HOSTNAME}-${TIMESTAMP}-tcpdump.pcap"
