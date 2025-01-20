# Use the official k6 image as the base
FROM loadimpact/k6:latest

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the k6 script from the local machine to the container
COPY ./script.js /usr/src/app/k6/script.js

# Set the default command to run the k6 script
ENTRYPOINT ["k6", "run", "/usr/src/app/k6/script.js"]
