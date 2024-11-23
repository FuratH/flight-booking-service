#!/bin/bash


# Parameters passed from the orchestrating VM
SUT_IP=$1
SERVICE_PORT=$2
TIMESTAMP=$3
BUCKET_NAME=$4
USERNAME=$(whoami)

locust -f /flight-booking-service/locust/benchmark.py --host=http://$SUT_IP:$SERVICE_PORT --headless -u 180 --run-time 10m --csv=client_results_${SERVICE_PORT} --html=client_results_${SERVICE_PORT}.html --spawn-rate=10

wait


gsutil cp ../client_results_${SERVICE_PORT}_stats.csv gs://duet-benchmarking-results/${TIMESTAMP}/client_results_${SERVICE_PORT}_stats.csv & gsutil cp ../client_results_${SERVICE_PORT}.html gs://duet-benchmarking-results/${TIMESTAMP}/client_results_${SERVICE_PORT}.html



touch /done

locust -f /flight-booking-service/locust/benchmark.py --host=http://35.198.124.184:3000 --headless -u 150 --run-time 10m --csv=client_results_3000 --html=client_results_3000.html --spawn-rate=10