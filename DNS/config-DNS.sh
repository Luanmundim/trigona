#!/bin/bash

# Define the Python script to run
SERVER_SCRIPT="DNS.py"

# Function to start the DNS
check_log_file() {
    log_dir="/home/ubuntu/log/DNS"
    # Ensure the directory exists
    mkdir -p "$log_dir"
    log_file="$log_dir/$(hostname)-$(date +"%Y%m%d%H%M%S")-DNS-service.log"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
    fi
}

start_DNS() {
    echo "Starting DNS..."
    # Check if the process is already running
    if [ -f DNS.pid ]; then
        PID=$(cat DNS.pid)
        if ps -p $PID > /dev/null; then
            echo "DNS is already running with PID: $PID"
            return
        fi
    fi
    
    # Run the Python script in the background
    sudo python3 $SERVER_SCRIPT &
    # Save the process ID of the DNS
    echo $! > DNS.pid
    echo "DNS started."

    # Create log entry
    check_log_file
    echo "$(date +"%Y-%m-%d %H:%M:%S") - DNS started" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "DNS started" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"
}

# Function to stop the DNS
stop_DNS() {
    echo "Stopping DNS..."
    # Read the process ID from the file
    if [ -f DNS.pid ]; then
        PID=$(cat DNS.pid)
        # Check if the process is running
        kill $PID
        rm DNS.pid
        echo "DNS stopped."

        # Create log entry
        check_log_file
        echo "$(date +"%Y-%m-%d %H:%M:%S") - DNS stopped" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "DNS stopped" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"

    else
        echo "DNS is not running"
    fi
}

# Function to check the status of the DNS
status_DNS() {
    echo "Checking DNS status..."
    # Read the process ID from the file
    if [ -f DNS.pid ]; then
        PID=$(cat DNS.pid)
        # Check if the process is running
        if ps -p $PID > /dev/null; then
            echo "DNS is running with PID: $PID"
            # Create log entry
            check_log_file
            echo "$(date +"%Y-%m-%d %H:%M:%S") - DNS is running with PID: $PID" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        else
            echo "DNS is not running"
            # Create log entry
            check_log_file
            echo "$(date +"%Y-%m-%d %H:%M:%S") - DNS is not running" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        fi
    else
        echo "DNS PID file not found. Is the DNS running?"
    fi
}

# Check command line argument
case "$1" in
    start)
        start_DNS
        ;;
    stop)
        stop_DNS
        ;;
    status)
        status_DNS
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac
