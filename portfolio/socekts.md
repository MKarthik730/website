# FastAPI WebSocket & Socket Programming - Complete Code Examples

## STEP 1: TCP Socket Server with Threading
```python
# tcp_server.py
import socket
import threading
import time

class TCPServer:
    def __init__(self, host='127.0.0.1', port=5000):
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
        finally:
            self.server_socket.close()
    
    def handle_client(self, client_socket, client_addr):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')
                print(f"From {client_addr[0]}: {message}")
                
                response = f"Echo: {message}".encode('utf-8')
                client_socket.sendall(response)
                
                self.broadcast(f"{client_addr[0]}: {message}", exclude_addr=client_addr)
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

if __name__ == "__main__":
    server = TCPServer()
    server.start()
```

## STEP 1B: TCP Client
```python
# tcp_client.py
import socket

def client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 5000))
    
    try:
        # Send message
        sock.send(b"Hello from client")
        
        # Receive response
        data = sock.recv(1024)
        print(f"Received: {data.decode('utf-8')}")
        
        # Keep receiving broadcast messages
        while True:
            data = sock.recv(1024)
            if data:
                print(f"Broadcast: {data.decode('utf-8')}")
    finally:
        sock.close()

if __name__ == "__main__":
    client()
```

---

## STEP 2: UDP Server (Connectionless)
```python
# udp_server.py
import socket

class UDPServer:
    def __init__(self, host='127.0.0.1', port=5001):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients = {}
    
    def start(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        print(f"UDP Server listening on {self.host}:{self.port}")
        
        try:
            while True:
                data, addr = self.socket.recvfrom(1024)
                message = data.decode('utf-8')
                print(f"From {addr}: {message}")
                
                # Store client
                self.clients[addr] = True
                
                # Echo back
                response = f"UDP Echo: {message}".encode('utf-8')
                self.socket.sendto(response, addr)
                
                # Broadcast to all
                for client_addr in self.clients:
                    try:
                        broadcast_msg = f"Broadcast: {message}".encode('utf-8')
                        self.socket.sendto(broadcast_msg, client_addr)
                    except:
                        pass
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.socket.close()

if __name__ == "__main__":
    server = UDPServer()
    server.start()
```

---

## STEP 3: FastAPI Basic WebSocket
```python
# app_step3.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Chat</title>
</head>
<body>
    <h1>WebSocket Chat</h1>
    <form action="" onsubmit="sendMessage(event)">
        <input type="text" id="messageText" autocomplete="off" />
        <button>Send</button>
    </form>
    <ul id='messages'></ul>
    <script>
        var ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = function(event) {
            var messages = document.getElementById('messages');
            var message = document.createElement('li');
            message.textContent = event.data;
            messages.appendChild(message);
        };
        function sendMessage(event) {
            var input = document.getElementById("messageText");
            ws.send(input.value);
            input.value = '';
            event.preventDefault();
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## STEP 4: FastAPI with Connection Manager
```python
# app_step4.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import json
import uvicorn

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass
    
    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat Room</title>
</head>
<body>
    <h1>Chat Room</h1>
    <form action="" onsubmit="sendMessage(event)">
        <input type="text" id="messageText" autocomplete="off" />
        <button>Send</button>
    </form>
    <ul id='messages'></ul>
    <script>
        var ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = function(event) {
            var data = JSON.parse(event.data);
            var messages = document.getElementById('messages');
            var message = document.createElement('li');
            message.textContent = data.type + ': ' + data.message;
            messages.appendChild(message);
        };
        function sendMessage(event) {
            var input = document.getElementById("messageText");
            if(input.value) {
                ws.send(JSON.stringify({type: "message", message: input.value}));
                input.value = '';
            }
            event.preventDefault();
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.broadcast(json.dumps({
        "type": "info",
        "message": f"User joined! Active: {len(manager.active_connections)}"
    }))
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(json.dumps({
                "type": "message",
                "message": data
            }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({
            "type": "info",
            "message": f"User left! Active: {len(manager.active_connections)}"
        }))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## STEP 5: Production-Ready with Middleware
```python
# app_production.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from contextlib import asynccontextmanager
import logging
import json
from datetime import datetime
import asyncio
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)
        logger.info(f"Connected. Total: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(f"Disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: str):
        async with self.lock:
            dead = []
            for conn in self.active_connections:
                try:
                    await conn.send_text(message)
                except:
                    dead.append(conn)
            
            for conn in dead:
                if conn in self.active_connections:
                    self.active_connections.remove(conn)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")
    async with manager.lock:
        for conn in manager.active_connections[:]:
            try:
                await conn.close()
            except:
                pass

app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "active": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(json.dumps({
                "message": data,
                "timestamp": datetime.now().isoformat()
            }))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Testing WebSocket
```python
# test_websocket.py
from fastapi.testclient import TestClient
from app_production import app

client = TestClient(app)

def test_websocket_echo():
    with client.websocket_connect("/ws") as websocket:
        websocket.send_text("Hello")
        data = websocket.receive_text()
        assert "Hello" in data

def test_websocket_broadcast():
    with client.websocket_connect("/ws") as ws1:
        with client.websocket_connect("/ws") as ws2:
            ws1.send_text("Test")
            data1 = ws1.receive_text()
            data2 = ws2.receive_text()
            assert data1 == data2

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

if __name__ == "__main__":
    test_websocket_echo()
    test_health()
    print("All tests passed!")
```

---

## Docker Deployment Files

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app_production:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
    restart: unless-stopped
    networks:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - fastapi
    restart: unless-stopped
    networks:
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - backend

volumes:
  redis_data:

networks:
  backend:
    driver: bridge
```

### requirements.txt
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
aioredis==2.0.1
PyJWT==2.8.1
aiohttp==3.9.1
prometheus-client==0.19.0
```

### nginx.conf
```nginx
upstream fastapi {
    server fastapi:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_buffering off;
    }

    location /health {
        proxy_pass http://fastapi;
        access_log off;
    }
}
```

---

## Performance Tips

### 1. Use asyncio.gather for concurrent tasks
```python
@app.get("/data")
async def get_data():
    results = await asyncio.gather(
        fetch_from_api_1(),
        fetch_from_api_2(),
        query_database()
    )
    return {"results": results}
```

### 2. Implement Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: "global")
app.state.limiter = limiter

@app.websocket("/ws")
@limiter.limit("100/minute")
async def websocket_endpoint(websocket: WebSocket):
    # ...
```

### 3. Connection Pooling
```python
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://user:pass@localhost/db',
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600,
)
```

### 4. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_user(user_id: int):
    return await db.query(User).get(user_id)
```

---

## Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app_production:app --reload

# Docker deployment
docker-compose build
docker-compose up -d

# Access
curl http://localhost:8000/health
# WebSocket: ws://localhost:8000/ws
```

---

## Monitoring Commands
```bash
# Monitor connections
sudo netstat -tuln | grep 8000

# Monitor system
htop

# Check application logs
docker-compose logs -f fastapi

# Monitor network traffic
sudo tcpdump -i any -A 'tcp port 8000'
```