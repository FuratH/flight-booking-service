#!/bin/bash

# Function to display usage information
usage() {
    echo "Usage: $0 <cgroup_parent> <cgroup_name> <cpu_limit_percentage>"
    echo "Example: $0 /sys/fs/cgroup/app-runner v1 150"
    exit 1
}

# Ensure correct usage
if [ "$#" -ne 3 ]; then
    usage
fi

# Parameters
CGROUP_PARENT=$1
CGROUP_NAME=$2
CPU_LIMIT_PERCENT=$3
CGROUP_PATH="$CGROUP_PARENT/$CGROUP_NAME"

# Check if cgroup2 is mounted
if ! mount | grep -q "cgroup2 on /sys/fs/cgroup"; then
    echo "cgroup2 is not mounted. Ensure your system uses cgroup2."
    exit 1
fi

# Step 1: Create the cgroup if it doesn't exist
echo "Creating cgroup: $CGROUP_PATH"
if [ ! -d "$CGROUP_PATH" ]; then
    mkdir -p "$CGROUP_PATH"
    if [ $? -ne 0 ]; then
        echo "Failed to create cgroup $CGROUP_PATH. Exiting."
        exit 1
    fi
    echo "Cgroup $CGROUP_PATH created successfully."
else
    echo "Cgroup $CGROUP_PATH already exists."
fi

# Step 2: Enable controllers in the parent cgroup
echo "Enabling controllers for $CGROUP_PARENT"
echo "+cpu +memory +io" > "$CGROUP_PARENT/cgroup.subtree_control" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Failed to enable controllers in $CGROUP_PARENT. Ensure proper permissions."
    exit 1
fi
echo "Controllers enabled successfully in $CGROUP_PARENT."

# Step 3: Set CPU limit
echo "Setting CPU limit for $CGROUP_PATH to $CPU_LIMIT_PERCENT%"
CPU_QUOTA=$(echo "$CPU_LIMIT_PERCENT * 1000" | bc | awk '{printf "%.0f", $0}')
CPU_PERIOD=100000
echo "$CPU_QUOTA $CPU_PERIOD" | sudo tee "$CGROUP_PATH/cpu.max" >/dev/null
if [ $? -ne 0 ]; then
    echo "Failed to set CPU limit for $CGROUP_PATH. Exiting."
    exit 1
fi
echo "CPU limit set to $CPU_LIMIT_PERCENT% successfully."

# Final verification
echo "Cgroup $CGROUP_NAME under $CGROUP_PARENT configured successfully."
echo "Current settings:"
echo "  CPU Max: $(cat "$CGROUP_PATH/cpu.max")"
