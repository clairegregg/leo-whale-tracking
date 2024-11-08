import threading
import random
import time
import argparse
import os
import sys
import socket
import requests
import signal
from flask import Flask, jsonify

# TODO set up local verification
import urllib3
urllib3.disable_warnings()

# Path to protocol headers
bob2_protocol_path = os.path.abspath("../bobb/src/utils/headers/")
sys.path.append(bob2_protocol_path)
import necessary_headers as bobb
import optional_header as bobb_optional

WANT_BOB_MAJOR_VERSION = 0
WANT_BOB_MINOR_VERSION = 2

def handle_sigint(signal, frame):
    print("Program interrupted. Exiting...")
    sys.exit(0)  # Exit the program

class WhaleModel:
    def __init__(self, whale_id, min_diving_time, max_diving_time, min_surface_time, max_surface_time, satellite_host, satellite_port, ip, port):
        self.whale_id = whale_id
        self.min_diving_time = min_diving_time
        self.max_diving_time = max_diving_time
        self.min_surface_time = min_surface_time
        self.max_surface_time = max_surface_time
        self.satellite_host = satellite_host
        self.satellite_port = satellite_port
        self.ip = ip
        self.port = port
        self.app = Flask(f"whale_{whale_id}")

        # Define the Flask app to handle simple acknowledgment requests
        @self.app.route('/', methods=['GET'])
        def acknowledge():
            return jsonify({"message": "Acknowledged", "whale_id": self.whale_id})

    # Method to send data to the satellite when the whale resurfaces
    def send_data(self, time_since_surfaced):
        surface_time = random.randint(self.min_surface_time, self.max_surface_time)
        sample_data = f"whale {self.whale_id} says: Whale Data wHaLe DaTa whale data WHALE DATA" * time_since_surfaced
        sample_data = sample_data.encode()

        # Prepare header
        header = bobb.BobbHeaders(
            version_major=WANT_BOB_MAJOR_VERSION,
            version_minor=WANT_BOB_MINOR_VERSION,
            message_type=0,
            dest_ipv6="::1",
            dest_port=12345,
            source_ipv6=self.ip,
            source_port=self.port
        )
        header = header.build_header().hex()

        opt_header = bobb_optional.BobbOptionalHeaders(
            timestamp=int(time.time()),
            hop_count=5,
            priority=0,
        )
        opt_header = opt_header.build_optional_header().hex()

        headers = {
            "X-Bobb-Header": header,
            "X-Bobb-Optional-Header": opt_header,
        }
        
        # Send acknowledgment request to satellite
        try:
            # TODO: enable verification
            response = requests.get(f"https://{self.satellite_host}:{self.satellite_port}/", headers=headers, verify=False, timeout=surface_time)
            print(f"Whale {self.whale_id} received response code {response.status_code} and content: {response.text}")
        except Exception as e:
            print(f"Failed to send data for whale {self.whale_id}: {e}")

    # Simulate whale routine with diving and resurfacing
    def start_whale_routine(self):
        while True:
            diving_time = random.randint(self.min_diving_time, self.max_diving_time)
            time.sleep(diving_time)  # Simulate whale diving

            # Whale surfaces
            time_since_surfaced = diving_time
            self.send_data(time_since_surfaced)

    # Start the Flask app for this whale in a separate thread
    def start_flask_app(self):
        threading.Thread(target=self.app.run, kwargs={"port": self.port, "use_reloader": False, "debug": False}, daemon=True).start()

def main(num_whales, min_diving_time, max_diving_time, min_surface_time, max_surface_time, satellite_host, satellite_port):
    # Set up the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_sigint)

    whales = []
    base_port = 5000

    hostname = socket.gethostname()
    ip = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]

    for whale_id in range(num_whales):
        # Assign a unique port to each whale
        port = base_port + whale_id
        whale = WhaleModel(whale_id, min_diving_time, max_diving_time, min_surface_time, max_surface_time, satellite_host, satellite_port, ip, port)
        
        # Start the Flask app for each whale
        whale.start_flask_app()
        
        # Start the whale routine in a separate thread
        threading.Thread(target=whale.start_whale_routine, daemon=True).start()
        
        whales.append(whale)

    print(f"{num_whales} whales modeled, each listening on individual ports starting from {base_port}.")
    
    signal.pause()  # Wait indefinitely until a signal is received

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Model whales coming to the surface and diving deep, sending data when they are at the surface.")
    parser.add_argument("--num_whales", type=int, default=10, help="Number of whales to model (default: 10)")
    parser.add_argument("--min_diving_time", type=int, default=300, help="Minimum time a whale spends diving (in seconds, default: 300)")
    parser.add_argument("--max_diving_time", type=int, default=3600, help="Maximum time a whale spends diving (in seconds, default: 3600)")
    parser.add_argument("--min_surface_time", type=int, default=30, help="Minimum time a whale spends at the surface (in seconds, default: 30)")
    parser.add_argument("--max_surface_time", type=int, default=1200, help="Maximum time a whale spends at the surface (in seconds, default: 1200)")
    parser.add_argument("--satellite_host", type=str, default="127.0.0.1", help="Satellite host")
    parser.add_argument("--satellite_port", type=int, default=8189, help="Satellite port")
    args = parser.parse_args()

    # Start the model
    main(args.num_whales, args.min_diving_time, args.max_diving_time, args.min_surface_time, args.max_surface_time, args.satellite_host, args.satellite_port)
