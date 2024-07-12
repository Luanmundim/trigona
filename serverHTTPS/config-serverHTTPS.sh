#!/bin/bash

# Define the Python script to run
SERVER_SCRIPT="serverHTTPS.py"
SERVER_PORT=4443

# Function to start the server
check_log_file() {
    log_dir="/home/ubuntu/log/serverHTTPS"
    # Ensure the directory exists
    mkdir -p "$log_dir"
    log_file="$log_dir/$(hostname)-$(date +"%Y%m%d%H%M%S")-serverHTTPS-service.log"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
    fi
}

start_server() {
    echo "Starting server..."
    # Check if the server is already running
    if [ -f serverHTTPS.pid ]; then
        PID=$(cat serverHTTPS.pid)
        if lsof -i :$SERVER_PORT -t -sTCP:LISTEN | grep -q $PID; then
            echo "Server is already running with PID: $PID"
            return
        fi
    fi

    # Run the Python script in the background
    python3 $SERVER_SCRIPT &
    # Save the process ID of the server
    echo $! > serverHTTPS.pid
    echo "Server started."

    # Create log entry
    check_log_file
    echo "$(date +"%Y-%m-%d %H:%M:%S") - Server started" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "Server started" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"
}

# Function to stop the server
stop_server() {
    echo "Stopping server..."
    # Read the process ID from the file
    if [ -f serverHTTPS.pid ]; then
        PID=$(cat serverHTTPS.pid)
        # Check if the process is running
        if lsof -i :$SERVER_PORT -t -sTCP:LISTEN | grep -q $PID; then
            kill $PID
            rm serverHTTPS.pid
            echo "Server stopped."

            # Create log entry
            check_log_file

            echo "$(date +"%Y-%m-%d %H:%M:%S") - Server stopped" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "Server stopped" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"

        else
        
            echo "Server is not running"
        fi
    else
        echo "Server PID file not found. Is the server running?"
    fi
}

# Function to check the status of the server
status_server() {
    echo "Checking server status..."
    # Read the process ID from the file
    if [ -f serverHTTPS.pid ]; then
        PID=$(cat serverHTTPS.pid)
        # Check if the process is running
        if lsof -i :$SERVER_PORT -t -sTCP:LISTEN | grep -q $PID; then
            echo "Server is running with PID: $PID"
            # Create log entry
            check_log_file
            echo "$(date +"%Y-%m-%d %H:%M:%S") - Server is running with PID: $PID" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        else
            echo "Server is not running"
            # Create log entry
            check_log_file

            echo "$(date +"%Y-%m-%d %H:%M:%S") - Server is not running" >> "$log_file" | jq -Rn '[inputs | split(" - ") | {"timestamp": .[0], "message": .[1]}]' "$log_file" > "$log_file"
        fi
    else
        echo "Server PID file not found. Is the server running?"
    fi
}

# Check command line argument
case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    status)
        status_server
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac
