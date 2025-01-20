# Use the official k6 image
FROM loadimpact/k6:latest

# Set the working directory
WORKDIR /usr/src/app

# Copy the k6 script into the container
COPY ./k6 /usr/src/app/k6

# Default command to run the k6 script
CMD ["run", "./k6/script.js"]
