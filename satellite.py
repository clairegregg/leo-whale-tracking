import socket
import argparse

def start_tcp_server(host, port):
    # Create a TCP/IP socket with IPv6
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    
    # Bind the socket to the address and port
    server_socket.bind((host, port))
    print(f"Server started on {host}:{port}")
    
    # Listen for incoming connections
    server_socket.listen(5)
    print("Waiting for a connection...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                print("Received message:", data.decode('utf-8'))
            
            client_socket.close()
            print(f"Connection closed for {client_address}")

    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple IPv6 TCP server.")
    parser.add_argument("--host", type=str, default="::1", help="IPv6 address to listen on (default: ::1)")
    parser.add_argument("--port", type=int, default=12345, help="Port to listen on (default: 12345)")
    args = parser.parse_args()

    start_tcp_server(host=args.host, port=args.port)
