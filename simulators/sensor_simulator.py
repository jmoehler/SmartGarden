import time
import requests
import random

from enviroment import *

base_url = "http://127.0.0.1:8000"

"""
Simulates a sensor device sending data to the server.

Registers a sensor device, obtains an API key, and continuously sends random sensor data to the server.
"""
def simulate():
    print(" * Serving sensor device 'sensor_simulator'")
    print(" * Debug mode: off")
    # print ctrl c to quit message in yellow
    print("\033[33m * Press Ctrl+C to quit\033[0m")
    
    # register the sensor device and get the api key
    response = requests.post(f"{base_url}/api/authenticate", json={"device_type": "sensor-device", "device_id": "12:23:34:45:56:67", "sensors": ["ph", "ec", "waterlevel", "temperature", "humidity", "light"]}, timeout=1)
    api_key = response.json().get("api_key")
    
    while True:
        # send data (from all sensors) to the hub
        response = requests.post(f"{base_url}/api/sensors/ph", headers={"Authorization": api_key}, json={"ph": get_ph()}, timeout=1)
        response = requests.post(f"{base_url}/api/sensors/ec", headers={"Authorization": api_key}, json={"ec": get_ec()}, timeout=1)
        response = requests.post(f"{base_url}/api/sensors/waterlevel", headers={"Authorization": api_key}, json={"waterlevel": random.randint(0, 1)}, timeout=1)
        response = requests.post(f"{base_url}/api/sensors/temperature", headers={"Authorization": api_key}, json={"temperature": get_temp()}, timeout=1)
        response = requests.post(f"{base_url}/api/sensors/humidity", headers={"Authorization": api_key}, json={"humidity": get_humidity()}, timeout=1)
        response = requests.post(f"{base_url}/api/sensors/light", headers={"Authorization": api_key}, json={"visible": random.randint(0, 50), "ir": random.randint(80, 100), "uv": random.randint(0, 100)}, timeout=1)
        
        # if the api key is invalid, register the sensor device again
        if response.status_code == 401:
            response = requests.post(f"{base_url}/api/authenticate", json={"device_type": "sensor-device", "device_id": "71891", "sensors": ["ph", "ec", "waterlevel", "temperature", "humidity", "light"]})
            api_key = response.json().get("api_key")
            
        # wait for 5 seconds
        time.sleep(5)
        

if __name__ == "__main__":
    simulate()