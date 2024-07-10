#!/bin/bash

# Define the Python script to run
SERVER_SCRIPT="crawler.py"

# Function to start the crawler
check_log_file() {
    log_dir="/home/ubuntu/log/crawler"
    # Ensure the directory exists
    mkdir -p "$log_dir"
    log_file="$log_dir/$(hostname)-$(date +"%Y%m%d")-crawler-service.log"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
    fi
}

start_crawler() {
    echo "Starting crawler..."
    # Check if the process is already running
    if [ -f crawler.pid ]; then
        PID=$(cat crawler.pid)
        if ps -p $PID > /dev/null; then
            echo "crawler is already running with PID: $PID"
            return
        fi
    fi

    # Run the Python script in the background
    sudo python3 $SERVER_SCRIPT &
    # Save the process ID of the crawler
    echo $! > crawler.pid
    echo "crawler started."

    # Create log entry
    check_log_file
    echo "$(date +"%Y-%m-%d %H:%M:%S") - crawler started" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "crawler started" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"
}

# Function to stop the crawler
# Function to stop the crawler
stop_crawler() {
    echo "Stopping crawler..."
    # Read the process ID from the file
    if [ -f crawler.pid ]; then
        PID=$(cat crawler.pid)
        # Check if the process is running
        kill $PID
        rm crawler.pid
        echo "crawler stopped."

        # Create log entry
        check_log_file

        echo "$(date +"%Y-%m-%d %H:%M:%S") - crawler stopped" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "crawler stopped" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"

    else
        echo "crawler is not running"
    fi
}

# Function to check the status of the crawler
status_crawler() {
    echo "Checking crawler status..."
    # Read the process ID from the file
    if [ -f crawler.pid ]; then
        PID=$(cat crawler.pid)
        # Check if the process is running
        if ps -p $PID > /dev/null; then
            echo "crawler is running with PID: $PID"
            # Create log entry
            check_log_file
            echo "$(date +"%Y-%m-%d %H:%M:%S") - crawler is running with PID: $PID" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        else
            echo "crawler is not running"
            # Create log entry
            check_log_file
            echo "$(date +"%Y-%m-%d %H:%M:%S") - crawler is not running" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        fi
    else
        echo "crawler PID file not found. Is the crawler running?"
    fi
}

# Check command line argument
case "$1" in
    start)
        start_crawler
        ;;
    stop)
        stop_crawler
        ;;
    status)
        status_crawler
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac
