#!/bin/bash

# Move all files from /cowrie/cowrie to /home/scripts/log/cowrie
# Ensure the target directory exists
mkdir -p /home/scripts/log/cowrie

# Move the files
cp -r /home/cowrie/cowrie/var/log/cowrie /home/scripts/log/cowrie/cowrie-$(date '+%Y-%m-%d_%H-%M')

