#!/bin/bash

SUT_IP=$1
SERVICE_PORT_1=$2
SERVICE_PORT_2=$3
TIMESTAMP=$4
BUCKET_NAME=$5

# Export environment variables for the Docker Compose run
export SUT_IP
export SERVICE_PORT_1
export SERVICE_PORT_2
export TIMESTAMP
export BUCKET_NAME

# Build and run both k6 instances in Docker containers using the specified docker-compose file
docker-compose -f docker-compose-client.yml up --build --abort-on-container-exit

# Wait for both containers to finish
wait

# Copy results from containers
docker cp $(docker-compose -f docker-compose-client.yml ps -q k6-instance-1):/usr/src/app/k6/client_results_${SERVICE_PORT_1}.csv ./client_results_${SERVICE_PORT_1}.csv
docker cp $(docker-compose -f docker-compose-client.yml ps -q k6-instance-1):/usr/src/app/k6/client_summary_${SERVICE_PORT_1}.json ./client_summary_${SERVICE_PORT_1}.json

docker cp $(docker-compose -f docker-compose-client.yml ps -q k6-instance-2):/usr/src/app/k6/client_results_${SERVICE_PORT_2}.csv ./client_results_${SERVICE_PORT_2}.csv
docker cp $(docker-compose -f docker-compose-client.yml ps -q k6-instance-2):/usr/src/app/k6/client_summary_${SERVICE_PORT_2}.json ./client_summary_${SERVICE_PORT_2}.json

# Upload results to Google Cloud Storage
gsutil cp client_results_${SERVICE_PORT_1}.csv gs://duet-benchmarking-results/${TIMESTAMP}/client_results_${SERVICE_PORT_1}.csv
gsutil cp client_summary_${SERVICE_PORT_1}.json gs://duet-benchmarking-results/${TIMESTAMP}/client_summary_${SERVICE_PORT_1}.json

gsutil cp client_results_${SERVICE_PORT_2}.csv gs://duet-benchmarking-results/${TIMESTAMP}/client_results_${SERVICE_PORT_2}.csv
gsutil cp client_summary_${SERVICE_PORT_2}.json gs://duet-benchmarking-results/${TIMESTAMP}/client_summary_${SERVICE_PORT_2}.json

# Copy VM stresser log if necessary
sudo gcloud compute ssh hamdanfurat@sut --zone europe-west1-c -- \
    "gsutil cp '/VMStresser/stresser.log' 'gs://duet-benchmarking-results/${TIMESTAMP}/stresser.log'"
