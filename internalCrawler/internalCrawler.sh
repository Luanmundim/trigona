#!/bin/bash

# Define the Python script to run
SERVER_SCRIPT="internalCrawler.py"

# Function to start the crawler
check_log_file() {
    log_file="`hostname`-`date +"%Y%m%d"`-crawler-service.log"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
    fi
}

start_internalCrawler() {
    echo "Starting internalCrawler..."
    # Check if the process is already running
    if [ -f internalCrawler.pid ]; then
        PID=$(cat internalCrawler.pid)
        if ps -p $PID > /dev/null; then
            echo "internalCrawler is already running with PID: $PID"
            return
        fi
    fi

    # Run the Python script in the background
    sudo python3 $SERVER_SCRIPT &
    # Save the process ID of the internalCrawler
    echo $! > internalCrawler.pid
    echo "internalCrawler started."

    # Create log entry
    log_file="`hostname`-`date +"%Y%m%d"`-internalCrawler-service.log"
    echo "$(date +"%Y-%m-%d %H:%M:%S") - internalCrawler started" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "internalCrawler started" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"
}

# Function to stop the internal
# Function to stop the internal
stop_internalCrawler() {
    echo "Stopping internalCrawler..."
    # Read the process ID from the file
    if [ -f internalCrawler.pid ]; then
        PID=$(cat internalCrawler.pid)
        # Check if the process is running
        kill $PID
        rm internalCrawler.pid
        echo "internalCrawler stopped."

        # Create log entry
        log_file="`hostname`-`date +"%Y%m%d"`-internalCrawler-service.log"

        echo "$(date +"%Y-%m-%d %H:%M:%S") - internalCrawler stopped" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "internalCrawler stopped" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"

    else
        echo "crawler is not running"
    fi
}

# Function to check the status of the internalCrawler
status_internalCrawler() {
    echo "Checking internalCrawler status..."
    # Read the process ID from the file
    if [ -f internalCrawler.pid ]; then
        PID=$(cat internalCrawler.pid)
        # Check if the process is running
        if ps -p $PID > /dev/null; then
            echo "internalCrawler is running with PID: $PID"
            # Create log entry
            log_file="`hostname`-`date +"%Y%m%d"`-internalCrawler-service.log"
            echo "$(date +"%Y-%m-%d %H:%M:%S") - internalCrawler is running with PID: $PID" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        else
            echo "internalCrawler is not running"
            # Create log entry
            log_file="`hostname`-`date +"%Y%m%d"`-internalCrawler-service.log"
            echo "$(date +"%Y-%m-%d %H:%M:%S") - internalCrawler is not running" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        fi
    else
        echo "internalCrawler PID file not found. Is the internalCrawler running?"
    fi
}

# Check command line argument
case "$1" in
    start)
        start_internalCrawler
        ;;
    stop)
        stop_internalCrawler
        ;;
    status)
        status_internalCrawler
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac
