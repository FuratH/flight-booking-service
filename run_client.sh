#!/bin/bash

# Parameters passed from the orchestrating VM
SUT_IP=$1
SERVICE_PORT=$2
TIMESTAMP=$3
BUCKET_NAME=$4
USERNAME=$(whoami)

# Run the k6 load test
k6 run /flight-booking-service/k6/script.js -e target="$SUT_IP:$SERVICE_PORT" \
    --out csv=client_results_${SERVICE_PORT}_${TIMESTAMP} --summary-export client_summary_${SERVICE_PORT}_${TIMESTAMP}.json

# Wait for the test to complete
wait


gsutil cp client_results_${SERVICE_PORT}_${TIMESTAMP}.csv gs://duet-benchmarking-results/client_results_${SERVICE_PORT}_${TIMESTAMP}.csv & gsutil cp client_summary_${SERVICE_PORT}_${TIMESTAMP}.json gs://duet-benchmarking-results/client_summary_${SERVICE_PORT}_${TIMESTAMP}.json



# Indicate that the task is done
touch /done