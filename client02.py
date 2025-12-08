import socket

def client(name: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect(('127.0.0.1', 5000))
        
      
        msg = f"{name}"
        sock.sendall(msg.encode('utf-8'))  
        while True:
            data = sock.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode('utf-8')}")
    finally:
        sock.close()

if __name__ == "__main__":
    client("rahul")