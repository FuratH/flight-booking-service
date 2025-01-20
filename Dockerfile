# Use an official Go image as the base image
FROM golang:1.20

# Set the working directory
WORKDIR /app

# Copy the Go modules manifest and download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the application source code
COPY . .

# Build the Go application
RUN GO_ENABLED=0 CGO_ENABLED=0 go build -a -installsuffix cgo -o ./cmd/flight-booking-service/flight-booking-service ./cmd/flight-booking-service

# Expose the default port (optional, for documentation purposes)
EXPOSE 3000

# Command to run the application with a placeholder for arguments
CMD ["./flight-booking-service"]
