#!/bin/bash

# Function to start the tcpdump
check_log_file() {
    log_dir="/home/ubuntu/log/tcpdump"
    # Ensure the directory exists
    mkdir -p "$log_dir"
    log_file="$log_dir/$(hostname)-$(date +"%Y%m%d%H%M%S")-tcpdump-service.log"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
    fi
}

start_tcpdump() {
    echo "Starting tcpdump..."
    # Run the tcpdump command and save the output
    TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
    sudo tcpdump -i ens4 > "/home/scripts/log/tcpdump/${HOSTNAME}-${TIMESTAMP}-tcpdump.pcap" &
    # Save the process ID of the tcpdump
    echo $! > tcpdump.pid
    echo "tcpdump started."

    # Create log entry
    check_log_file
    echo "$(date +"%Y-%m-%d %H:%M:%S") - tcpdump started" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "tcpdump started" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"
}
# Function to stop the tcpdump
stop_tcpdump() {
    echo "Stopping tcpdump..."
    # Read the process ID from the file
    if [ -f tcpdump.pid ]; then
        PID=$(cat tcpdump.pid)
        # Check if the process is running
        kill $PID
        rm tcpdump.pid
        echo "tcpdump stopped."

        # Create log entry
        check_log_file

        echo "$(date +"%Y-%m-%d %H:%M:%S") - tcpdump stopped" | jq -Rn --arg timestamp "$(date +"%Y-%m-%d %H:%M:%S")" --arg message "tcpdump stopped" '{"timestamp": $timestamp, "message": $message}' >> "$log_file"

    else
        echo "tcpdump is not running"
    fi
}

# Function to check the status of the tcpdump
status_tcpdump() {
    echo "Checking tcpdump status..."
    # Read the process ID from the file
    if [ -f tcpdump.pid ]; then
        PID=$(cat tcpdump.pid)
        # Check if the process is running
        echo "tcpdump is running with PID: $PID"
        # Create log entry
        check_log_file
        echo "$(date +"%Y-%m-%d %H:%M:%S") - tcpdump is running with PID: $PID" >> "$log_file"
    else
        echo "tcpdump is not running"
        # Create log entry
        check_log_file
        echo "$(date +"%Y-%m-%d %H:%M:%S") - tcpdump is not running" >> "$log_file"
    fi
}

# Check command line argument
case "$1" in
    start)
        start_tcpdump
        ;;
    stop)
        stop_tcpdump
        ;;
    status)
        status_tcpdump
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac
