#!/bin/bash

# Check for correct usage
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <port> <version>"
    echo "Example: $0 3000 v1"
    exit 1
fi

# Parameters
PORT=$1
VERSION=$2

# Configuration
CGROUP_PATH="/sys/fs/cgroup/app-runner/$VERSION"
PROGRAM_PATH="./cmd/flight-booking-service/flight-booking-service"
BIND_ADDRESS="0.0.0.0:$PORT"

# Ensure the cgroup exists
if [ ! -d "$CGROUP_PATH" ]; then
    echo "Cgroup $CGROUP_PATH does not exist. Exiting."
    exit 1
fi

# Check for proper write permissions to the cgroup
if [ ! -w "$CGROUP_PATH/cgroup.procs" ]; then
    echo "No write permissions to $CGROUP_PATH/cgroup.procs. Exiting."
    exit 1
fi

# Ensure the program exists
if [ ! -x "$PROGRAM_PATH" ]; then
    echo "Program $PROGRAM_PATH does not exist or is not executable. Exiting."
    exit 1
fi

# Start the program with the specified environment variable in the background
BIND_ADDRESS="$BIND_ADDRESS" "$PROGRAM_PATH" &
PID=$!

if [ $? -ne 0 ]; then
    echo "Failed to start the program: $PROGRAM_PATH"
    exit 1
fi

echo "Program started with PID $PID."

# Assign the PID to the cgroup
echo $PID > "$CGROUP_PATH/cgroup.procs"
if [ $? -ne 0 ]; then
    echo "Failed to assign PID $PID to cgroup $CGROUP_PATH."
    kill $PID  # Clean up the process if assignment fails
    exit 1
fi

echo "Program assigned to cgroup $CGROUP_PATH successfully."
