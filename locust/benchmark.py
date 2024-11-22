from locust import HttpUser, TaskSet, task, between
import random
import time
import json
import os
import base64

def select_random_element(data):
    return random.choice(data)

def select_random_unique_elements(data, count):
    res = []
    for _ in range(count * 3):
        el = select_random_element(data)
        if el in res:
            continue
        res.append(el)
        if len(res) == count:
            return res
    return res

class SearchFlightsTaskSet(TaskSet):
    @task
    def search_flights(self):
        destination_res = self.client.get("/destinations")
        if destination_res.status_code != 200:
            return

        destination = destination_res.json()
        self.client.get(f"/flights?from={select_random_element(destination['from'])}")

class SearchAndBookFlightTaskSet(TaskSet):
    @task
    def search_and_book_flight(self):
        endpoint = self.user.host  # Already includes schema and is clean
        
        destination_res = self.client.get("/destinations")
        if destination_res.status_code != 200:
            return

        destination = destination_res.json()
        time.sleep(1) 

        flights_res = self.client.get(f"/flights?from={select_random_element(destination['from'])}")
        if flights_res.status_code != 200:
            return

        flights = flights_res.json()
        random_flight = select_random_element(flights)
        time.sleep(1) 

        booking_request = {"flightId": random_flight['id'], "passengers": []}
        seats_res = self.client.get(f"/flights/{random_flight['id']}/seats")
        if seats_res.status_code == 200:
            seats = seats_res.json()
            booking_request['passengers'] = [
                {"name": f"Passenger {i}", "seat": v['seat']}
                for i, v in enumerate(select_random_unique_elements(seats, 2))
            ]
        else:
            booking_request['passengers'] = [{"name": "Passenger", "seat": "XX"}]

        time.sleep(random.randint(0, 3))

        auth_header = base64.b64encode(b"user:pw").decode("utf-8")
        headers = {"Authorization": f"Basic {auth_header}"}
        res = self.client.post("/bookings", json=booking_request, headers=headers)
        assert res.status_code == 200, "Booking failed"

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    # Ensure a clean host value with schema and no trailing slashes
    host = os.getenv('TARGET', 'http://localhost').rstrip('/')
    tasks = {SearchFlightsTaskSet: 20, SearchAndBookFlightTaskSet: 5}
