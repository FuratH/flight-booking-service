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

gsutil cp ../client_results_3000_stats.csv gs://duet-benchmarking-results/a/client_results_3000_stats.csv & gsutil cp ../client_results_3000.html gs://duet-benchmarking-results/a/client_results_3000.html
gsutil cp ../client_results_3001_stats.csv gs://duet-benchmarking-results/a/client_results_3001_stats.csv & gsutil cp ../client_results_3001.html gs://duet-benchmarking-results/a/client_results_3001.html

touch /done
