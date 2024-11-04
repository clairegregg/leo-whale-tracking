import threading
import random
import time
import argparse

class WhaleModel:
    def __init__(self, num_whales, min_diving_time, max_diving_time, min_surface_time, max_surface_time):
        self.num_whales = num_whales
        self.min_diving_time = min_diving_time
        self.max_diving_time = max_diving_time
        self.min_surface_time = min_surface_time
        self.max_surface_time = max_surface_time

    # Whale has breached, send data to satellite
    def send_data(self, whale_id):
        # TODO make this send data
        print(f"Whale {whale_id} came to the surface at {time.strftime('%X')}")
        # Simulate time spent at the surface - TODO make this cut off data once the time runs out
        time.sleep(random.randint(self.min_surface_time, self.max_surface_time))

    # Function to simulate whale diving and resurfacing
    def start_whale_routine(self, whale_id):
        while True:
            # Simulate diving delay before resurfacing
            diving_time = random.randint(self.min_diving_time, self.max_diving_time)
            time.sleep(diving_time)
            self.send_data(whale_id)

    # Method to start all whales' routines
    def start(self):
        for i in range(self.num_whales):
            # Start a thread for each whale's routine
            threading.Thread(target=self.start_whale_routine, args=(i,), daemon=True).start()
        
        print(f"{self.num_whales} whales modeled. Whales are now running in the background.")

def main(num_whales=10, min_diving_time=300, max_diving_time=3600, min_surface_time=30, max_surface_time=1200):
    # Create an instance of WhaleModel with the provided arguments
    whale_model = WhaleModel(num_whales, min_diving_time, max_diving_time, min_surface_time, max_surface_time)
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
    args = parser.parse_args()

    # Model the specified number of whales
    main(args.num_whales, args.min_diving_time, args.max_diving_time, args.min_surface_time, args.max_surface_time)
