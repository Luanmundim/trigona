#!/bin/bash

# Terminate all screens with "tcpdump" in the name
screen -ls | grep tcpdump | cut -d. -f1 | awk '{print $1}' | xargs kill


# Open a screen called tcpdump, run /home/tcpdump/tcpdump.sh, then detach the screen
screen -dmS tcpdump bash -c '/home/scripts/tcpdump/sniff-tcpdump.sh'

# Create a directory named teste
echo "Script de monitoramento com TCPDUMP foi iniciado!"
