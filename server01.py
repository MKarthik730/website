import socket
import threading
import time

class TCPServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.names = []
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.lock = threading.Lock()
    
    def start(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"TCP Server listening on {self.host}:{self.port}")
        
        try:
            while True:
                client_socket, client_addr = self.server_socket.accept()
                print(f"Connection from {client_addr}")
                
                with self.lock:
                    self.clients.append({'socket': client_socket, 'addr': client_addr})
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_addr)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Shutting down...")
            self.stop()
    
    def handle_client(self, client_socket, client_addr):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    print(f"Client {client_addr} disconnected")
                    break
                
                message = data.decode('utf-8').strip()
                if not message:
                    continue
                
                print(f"From {client_addr[0]}: {message}")
                
                # Store UNIQUE name only ONCE
                with self.lock:
                    if message not in self.names:
                        self.names.append(message)
                
                # Echo back FIRST - FIXED order
                response = f"Echo: {message}".encode('utf-8')
                client_socket.sendall(response)
                
                self.broadcast(f"{client_addr[0]}: {message}", exclude_addr=client_addr)
                self.intimate()
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            with self.lock:
                self.clients = [c for c in self.clients if c['addr'] != client_addr]
            client_socket.close()
    
    def broadcast(self, message, exclude_addr=None):
        with self.lock:
            for client in self.clients:
                if exclude_addr and client['addr'] == exclude_addr:
                    continue
                try:
                    client['socket'].sendall(message.encode('utf-8'))
                except:
                    pass
    
    def intimate(self):  # FIXED: Proper 4-space indentation
        names_str = f"Online: {', '.join(self.names)}"
        with self.lock:
            for client in self.clients:
                try:
                    client['socket'].sendall(names_str.encode('utf-8'))
                except:
                    pass
    
    def stop(self):  # FIXED: Proper 4-space indentation
        """Graceful shutdown - disconnect all clients first"""
        print("Stopping server...")
        with self.lock:
            for client in self.clients[:]:
                try:
                    client['socket'].close()
                except:
                    pass
            self.clients.clear()
        self.server_socket.close()

if __name__ == "__main__":
    server = TCPServer()
    server.start()
