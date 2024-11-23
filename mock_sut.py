from flask import Flask, jsonify, request, abort
import random
import time
import math
import numpy as np

app = Flask(__name__)

# Sample data for mocking responses
DESTINATIONS = {
    "from": ["NYC", "LAX", "CHI", "DFW", "ATL"],
    "to": ["MIA", "SEA", "DEN", "BOS", "SFO"]
}

FLIGHTS = [
    {"id": 1, "from": "NYC", "to": "MIA", "price": 200},
    {"id": 2, "from": "LAX", "to": "SEA", "price": 150},
    {"id": 3, "from": "CHI", "to": "DEN", "price": 180},
    {"id": 4, "from": "DFW", "to": "BOS", "price": 220},
    {"id": 5, "from": "ATL", "to": "SFO", "price": 250}
]

SEATS = {
    1: [{"seat": "1A"}, {"seat": "1B"}, {"seat": "1C"}],
    2: [{"seat": "2A"}, {"seat": "2B"}, {"seat": "2C"}],
    3: [{"seat": "3A"}, {"seat": "3B"}, {"seat": "3C"}],
    4: [{"seat": "4A"}, {"seat": "4B"}, {"seat": "4C"}],
    5: [{"seat": "5A"}, {"seat": "5B"}, {"seat": "5C"}],
}

BOOKINGS = []

# Simulate a more complex, CPU-intensive task (factorial)
def calculate_factorial(limit):
    result = 1
    for i in range(1, limit + 1):
        result *= i
    return result

# Simulate matrix multiplication to simulate larger load
def matrix_multiplication(size):
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    return np.dot(a, b)

# Simulate calculating Fibonacci sequence with a larger range
def calculate_fibonacci(limit=1000):
    fib = [0, 1]
    for i in range(2, limit):
        fib.append(fib[-1] + fib[-2])
    return fib

# Utility function to simulate a long processing time (up to 3 seconds)
def simulate_processing_time(min_time=0.5, max_time=3):
    time.sleep(random.uniform(min_time, max_time))

# Endpoints
@app.route('/destinations', methods=['GET'])
def get_destinations():
    simulate_processing_time()  # Simulate some latency
    calculate_fibonacci(3000)  # Moderate computation (larger Fibonacci)
    calculate_factorial(1000)  # Higher CPU load task (factorial)
    matrix_multiplication(500)  # Matrix multiplication (complex computation)
    return jsonify(DESTINATIONS)

@app.route('/flights', methods=['GET'])
def get_flights():
    simulate_processing_time()
    flight_from = request.args.get('from')
    if not flight_from:
        abort(400, "Missing 'from' query parameter")
    filtered_flights = [f for f in FLIGHTS if f["from"] == flight_from]
    
    # Triggering multiple computationally expensive tasks
    calculate_fibonacci(2000)  # More intensive Fibonacci calculation
    calculate_factorial(1000)  # More CPU-intensive factorial calculation
    matrix_multiplication(600)  # Simulate large matrix multiplication

    return jsonify(filtered_flights)

@app.route('/flights/<int:flight_id>/seats', methods=['GET'])
def get_seats(flight_id):
    simulate_processing_time()
    seats = SEATS.get(flight_id, [])
    
    # More intensive computation for seats
    calculate_fibonacci(1500)
    calculate_factorial(800)
    matrix_multiplication(400)
    
    return jsonify(seats)

@app.route('/bookings', methods=['POST'])
def create_booking():
    simulate_processing_time()
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        abort(401, "Missing Authorization header")
    
    try:
        booking_data = request.get_json()
        flight_id = booking_data["flightId"]
        passengers = booking_data.get("passengers", [])
        BOOKINGS.append({"flightId": flight_id, "passengers": passengers})
        
        # Increase computational load during booking
        calculate_fibonacci(2500)
        calculate_factorial(1200)
        matrix_multiplication(700)

        return jsonify({"status": "success", "bookingId": len(BOOKINGS)}), 200
    except Exception as e:
        abort(400, str(e))

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
