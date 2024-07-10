#!/bin/bash

# Move all files from /cowrie/cowrie to /home/scripts/log/cowrie
# Ensure the target directory exists
mkdir -p /home/ubuntu/log/cowrie

# Move the files
cp -r /home/cowrie/cowrie/var/log/cowrie /home/ubuntu/log/cowrie/cowrie-$(date '+%Y-%m-%d_%H-%M-%S')

