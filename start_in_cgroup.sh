#!/bin/bash

# Validate number of arguments based on the component
if [ "$#" -lt 3 ] || [ "$#" -gt 5 ]; then
    echo "Usage for SUT: $0 <port> <version> SUT"
    echo "Usage for client: $0 <port> <version> client <timestamp> <bucket_name>"
    echo "Component must be either 'SUT' or 'client'."
    exit 1
fi

# Parameters
PORT=$1
VERSION=$2
COMPONENT=$3
TIMESTAMP=$4
BUCKET_NAME=$5

# Validate component
if [ "$COMPONENT" != "SUT" ] && [ "$COMPONENT" != "client" ]; then
    echo "Invalid component: $COMPONENT. Must be 'SUT' or 'client'. Exiting."
    exit 1
fi

# Ensure proper arguments are provided based on the component
if [ "$COMPONENT" == "client" ]; then
    if [ -z "$TIMESTAMP" ] || [ -z "$BUCKET_NAME" ]; then
        echo "For client, you must provide <timestamp> and <bucket_name>."
        echo "Usage: $0 <port> <version> client <timestamp> <bucket_name>"
        exit 1
    fi
elif [ "$COMPONENT" == "SUT" ]; then
    if [ -n "$TIMESTAMP" ] || [ -n "$BUCKET_NAME" ]; then
        echo "For SUT, no additional arguments beyond <port>, <version>, and 'SUT' are allowed."
        echo "Usage: $0 <port> <version> SUT"
        exit 1
    fi
fi

# Debugging output (optional, can be removed)
echo "Port: $PORT"
echo "Version: $VERSION"
echo "Component: $COMPONENT"
[ "$COMPONENT" == "client" ] && echo "Timestamp: $TIMESTAMP, Bucket Name: $BUCKET_NAME"

# Configuration
CGROUP_PATH="/sys/fs/cgroup/app-runner/$VERSION"
if [ "$COMPONENT" == "SUT" ]; then
    PROGRAM_PATH="./cmd/flight-booking-service/flight-booking-service"
else
    PROGRAM_PATH="./run_client.sh $SUT_IP $PORT $TIMESTAMP $BUCKET_NAME"
fi
BIND_ADDRESS="0.0.0.0:$PORT"

# Define CPU affinity based on the port
if [ "$PORT" -eq 3000 ]; then
    CPU_AFFINITY="0,1"  # Use cores 0 and 1
elif [ "$PORT" -eq 3001 ]; then
    CPU_AFFINITY="2,3"  # Use cores 2 and 3
else
    echo "Unsupported port: $PORT. Exiting."
    exit 1
fi

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
if [ "$COMPONENT" == "SUT" ]; then
    if [ ! -x "$PROGRAM_PATH" ]; then
        echo "Program $PROGRAM_PATH does not exist or is not executable. Exiting."
        exit 1
    fi
fi

# Start the program
if [ "$COMPONENT" == "SUT" ]; then
    export BIND_ADDRESS="$BIND_ADDRESS"
    taskset -c $CPU_AFFINITY "$PROGRAM_PATH" --port="$PORT" &
else
    taskset -c $CPU_AFFINITY bash "$PROGRAM_PATH" &
fi

PID=$!

if [ $? -ne 0 ]; then
    echo "Failed to start the program: $PROGRAM_PATH"
    exit 1
fi

echo "Program started with PID $PID and CPU affinity set to cores $CPU_AFFINITY."

# Assign the PID to the cgroup
echo $PID > "$CGROUP_PATH/cgroup.procs"
if [ $? -ne 0 ]; then
    echo "Failed to assign PID $PID to cgroup $CGROUP_PATH."
    kill $PID  # Clean up the process if assignment fails
    exit 1
fi

echo "Program assigned to cgroup $CGROUP_PATH successfully."
