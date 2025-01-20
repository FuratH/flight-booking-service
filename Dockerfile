# Use an official Golang image as a base
FROM golang:1.20

# Set the working directory
WORKDIR /app

# Copy the Go modules manifest and dependencies
COPY go.mod go.sum ./
COPY chi ./chi  
RUN go mod download

# Copy the rest of the application source code
COPY . .

# Build the Go application with the required options
RUN GO_ENABLED=0 CGO_ENABLED=0 go build -a -installsuffix cgo -o ./cmd/flight-booking-service/flight-booking-service ./cmd/flight-booking-service

# Expose the application port
EXPOSE 3000

# Run the application
CMD ["./cmd/flight-booking-service/flight-booking-service"]
