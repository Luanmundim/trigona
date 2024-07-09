#!/bin/bash

# Define the Python script to run
SERVER_SCRIPT="request.py"

# Function to start the request
check_log_file() {
    log_file="`hostname`-`date +"%Y%m%d"`-request-service.log"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
    fi
}

start_request() {
    echo "Starting request..."
    # Check if the process is already running
    if [ -f request.pid ]; then
        PID=$(cat request.pid)
        if ps -p $PID > /dev/null; then
            echo "request is already running with PID: $PID"
            return
        fi
    fi

    # Run the Python script in the background
    sudo python3 $SERVER_SCRIPT &
    # Save the process ID of the request
    echo $! > request.pid
    echo "request started."

    # Create log entry
    log_file="`hostname`-`date +"%Y%m%d"`-request-service.log"
    echo "$(date +"%Y-%m-%d %H:%M:%S") - request started" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "request started" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"
}

# Function to stop the internal
# Function to stop the internal
stop_request() {
    echo "Stopping request..."
    # Read the process ID from the file
    if [ -f request.pid ]; then
        PID=$(cat request.pid)
        # Check if the process is running
        kill $PID
        rm request.pid
        echo "request stopped."

        # Create log entry
        log_file="`hostname`-`date +"%Y%m%d"`-request-service.log"

        echo "$(date +"%Y-%m-%d %H:%M:%S") - request stopped" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "request stopped" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"

    else
        echo "request is not running"
    fi
}

# Function to check the status of the request
status_request() {
    echo "Checking request status..."
    # Read the process ID from the file
    if [ -f request.pid ]; then
        PID=$(cat request.pid)
        # Check if the process is running
        if ps -p $PID > /dev/null; then
            echo "request is running with PID: $PID"
            # Create log entry
            log_file="`hostname`-`date +"%Y%m%d"`-request-service.log"
            echo "$(date +"%Y-%m-%d %H:%M:%S") - request is running with PID: $PID" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        else
            echo "request is not running"
            # Create log entry
            log_file="`hostname`-`date +"%Y%m%d"`-request-service.log"
            echo "$(date +"%Y-%m-%d %H:%M:%S") - request is not running" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        fi
    else
        echo "request PID file not found. Is the request running?"
    fi
}

# Check command line argument
case "$1" in
    start)
        start_request
        ;;
    stop)
        stop_request
        ;;
    status)
        status_request
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac
