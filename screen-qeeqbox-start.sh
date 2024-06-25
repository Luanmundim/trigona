#!/bin/bash

# Terminate all screens with "tcpdump" in the name
screen -ls | grep qeeqbox | cut -d. -f1 | awk '{print $1}' | xargs kill

# Open a screen called tcpdump, run /home/tcpdump/tcpdump.sh, then detach the screen
screen -dmS qeeqbox bash -c '/home/scripts/qeeqbox/config-qeeqbox.sh'

# Create a directory named teste
echo "Qeeqbox foi iniciado."
