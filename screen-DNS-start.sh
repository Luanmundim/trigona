#!/bin/bash

# Terminate all screens with "DNS" in the name
screen -ls | grep DNS | cut -d. -f1 | awk '{print $1}' | xargs kill

screen -dmS DNS bash -c 'sudo python3 /home/scripts/DNS/DNS.py'

echo "Script de divulgacao DNS foi iniciado"
