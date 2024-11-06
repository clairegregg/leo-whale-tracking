import threading
import random
import time
import argparse
import socket
import os
import sys
import math

bob2_protocol_path = os.path.abspath("../Bob2/src/protocol")
sys.path.append(bob2_protocol_path)
import bob2_protocol

WANT_BOB_MAJOR_VERSION = 0
WANT_BOB_MINOR_VERSION = 2

class WhaleModel:
    def __init__(self, num_whales, min_diving_time, max_diving_time, min_surface_time, max_surface_time, packet_size, satellite_host, satellite_port):
        self.num_whales = num_whales
        self.min_diving_time = min_diving_time
        self.max_diving_time = max_diving_time
        self.min_surface_time = min_surface_time
        self.max_surface_time = max_surface_time
        self.packet_size = packet_size
        self.satellite_host = satellite_host
        self.satellite_port = satellite_port
        self.bob2 = bob2_protocol.Bob2Protocol()

    # Whale has breached, send data to satellite
    def send_data(self, whale_id, whale_connection, time_since_surfaced):
        # Random surface time as timeout for the transmission
        surface_time = random.randint(self.min_surface_time, self.max_surface_time)
        end_time = time.time() + surface_time

        sample_data = f"whale {whale_id} says: Whale Data wHaLe DaTa whale data WHALE DATA" * time_since_surfaced
        sample_data = sample_data.encode()
        packet_count = math.ceil(len(sample_data)/self.packet_size)

        whale_connection.connect((self.satellite_host, self.satellite_port))

        # Loop through packets - note that Bob2 expects packet count to start at 1
        for packet_num in range(1, packet_count+1):
            if packet_num == packet_count+1:
                content_for_packet = sample_data[(packet_num-1)*self.packet_size:]
            else:
                content_for_packet = sample_data[(packet_num-1)*self.packet_size : packet_count*self.packet_size]
            packet = self.bob2.build_message(
                message_type=0,
                dest_ipv6="::1", # Dummy value
                dest_port=12345, # Dummy value
                message_content=content_for_packet.decode(), 
                multiple_packets=True,
                packet_num=packet_num,
            )
            whale_connection.send(packet)
            # If the surface time has run out, stop sending packets
            # TODO also let this stop transmission in the middle of a packet!
            if time.time() >= end_time:
                whale_connection.close()
                break

        if time.time() < end_time:
            time_remaining = end_time-time.time()
            time.sleep(time_remaining)

    # Function to simulate whale diving and resurfacing
    def start_whale_routine(self, whale_id, whale_connection):
        while True:
            # Simulate diving delay before resurfacing
            diving_time = random.randint(self.min_diving_time, self.max_diving_time)
            time.sleep(diving_time)
            self.send_data(whale_id, whale_connection, diving_time)

    # Method to start all whales' routines
    def start(self):
        for i in range(self.num_whales):
            # Create TCP connection
            whale_connection = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            # Start a thread for each whale's routine
            threading.Thread(target=self.start_whale_routine, args=(i,whale_connection,), daemon=True).start()
        
        print(f"{self.num_whales} whales modeled. Whales are now swimming in the background.")

def main(num_whales, min_diving_time, max_diving_time, min_surface_time, max_surface_time, packet_size,  satellite_host, satellite_port):
    # Create an instance of WhaleModel with the provided arguments
    whale_model = WhaleModel(num_whales, min_diving_time, max_diving_time, min_surface_time, max_surface_time, packet_size, satellite_host, satellite_port)
    # Start the whale model
    whale_model.start()

    # Keep the main thread alive indefinitely
    stop_event = threading.Event()
    try:
        stop_event.wait()  # This will wait indefinitely until the event is set
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Model whales coming to the surface and diving deep, sending data when they are at the surface.")
    parser.add_argument("--num_whales", type=int, default=10, help="Number of whales to model (default: 10)")
    parser.add_argument("--min_diving_time", type=int, default=300, help="The minimum time a whale should spend diving/out of the range of LEO satellites (in seconds, default: 300)")
    parser.add_argument("--max_diving_time", type=int, default=3600, help="The maximum time a whale should spend diving/out of the range of LEO satellites (in seconds, default: 3600)")
    parser.add_argument("--min_surface_time", type=int, default=30, help="The minimum time a whale should spend at the surface (in seconds, default: 30)")
    parser.add_argument("--max_surface_time", type=int, default=1200, help="The maximum time a whale should spend at the surface (in seconds, default: 1200)")
    parser.add_argument("--packet_size", type=int, default=32, help="Maximum length in bytes which should be included in a message")
    
    # TODO: remove these once code to select satellite is written
    parser.add_argument("--satellite_host", type=str, default="::1", help="Satellite host")
    parser.add_argument("--satellite_port", type=int, default=12345, help="Satellite port")
    args = parser.parse_args()

    if bob2_protocol.CURRENT_MAJOR_VERSION != WANT_BOB_MAJOR_VERSION or bob2_protocol.CURRENT_MINOR_VERSION != WANT_BOB_MINOR_VERSION:
        print(f"Wrong version of Bob2 installed in ../Bob2/src/protocol ({bob2_protocol.CURRENT_MAJOR_VERSION}.{bob2_protocol.CURRENT_MINOR_VERSION}), want version {WANT_BOB_MAJOR_VERSION}.{WANT_BOB_MINOR_VERSION}")

    # Model the specified number of whales
    main(args.num_whales, args.min_diving_time, args.max_diving_time, args.min_surface_time, args.max_surface_time, args.packet_size, args.satellite_host, args.satellite_port)
