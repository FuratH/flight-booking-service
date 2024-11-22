#!/bin/bash

# Parameters passed from the orchestrating VM
SUT_IP=$1
SERVICE_PORT=$2
TIMESTAMP=$3
BUCKET_NAME=$4
USERNAME=$(whoami)

python3 locust -f /flight-booking-service/locust/benchmark.py --host $SUT_IP:$SERVICE_PORT --web-port $SERVICE_PORT



touch /done