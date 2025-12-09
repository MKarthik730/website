# main.py - Complete FastAPI + TCP Server with ALL fixes
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import uvicorn
import threading
import socket
from contextlib import asynccontextmanager
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup (SQLite for simplicity)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic models
class UserCreate(BaseModel):
    name: str
    age: int
    number: str
    salary: float

class UserUpdate(BaseModel):
    name: str
    age: int
    number: str
    salary: float

# Database models
class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    number = Column(String)
    salary = Column(Float)

Base.metadata.create_all(bind=engine)

# TCP Server (Thread-safe, production-ready)
class TCPServer:
    def __init__(self, host='127.0.0.1', port=5000):
        self.names: List[str] = []
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: List[Dict] = []
        self.lock = threading.Lock()
        self.running = False
    
    def start(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        logger.info(f"TCP Server listening on {self.host}:{self.port}")
        
        try:
            while self.running:
                try:
                    client_socket, client_addr = self.server_socket.accept()
                    logger.info(f"TCP Connection from {client_addr}")
                    
                    with self.lock:
                        self.clients.append({'socket': client_socket, 'addr': client_addr})
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_addr),
                        daemon=True
                    )
                    client_thread.start()
                except socket.error as e:
                    if self.running:
                        logger.error(f"TCP accept error: {e}")
        except KeyboardInterrupt:
            logger.info("TCP Server shutting down...")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, client_addr):
        client_name = None
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    logger.info(f"TCP Client {client_addr} disconnected")
                    break
                
                message = data.decode('utf-8').strip()
                if not message:
                    continue
                
                logger.info(f"TCP From {client_addr[0]}: {message}")
                
                # Use first message as client name, validate length
                with self.lock:
                    if client_name is None and 1 <= len(message) <= 50:
                        if message not in self.names:
                            self.names.append(message)
                            client_name = message
                
                response = f"Echo: {message}".encode('utf-8')
                client_socket.sendall(response)
                
                self.broadcast(f"{client_addr[0]}: {message}", exclude_addr=client_addr)
                self.intimate()
                
        except Exception as e:
            logger.error(f"TCP Client {client_addr} error: {e}")
        finally:
            with self.lock:
                if client_name and client_name in self.names:
                    self.names.remove(client_name)
                self.clients = [c for c in self.clients if c['addr'] != client_addr]
            try:
                client_socket.close()
            except:
                pass
    
    def broadcast(self, message: str, exclude_addr=None):
        with self.lock:
            for client in self.clients[:]:  # Copy to avoid modification during iteration
                if exclude_addr and client['addr'] == exclude_addr:
                    continue
                try:
                    client['socket'].sendall(message.encode('utf-8'))
                except Exception:
                    # Remove dead clients
                    self.clients.remove(client)
    
    def intimate(self):
        names_str = f"Online: {', '.join(self.names) if self.names else 'None'}"
        with self.lock:
            for client in self.clients[:]:
                try:
                    client['socket'].sendall(names_str.encode('utf-8'))
                except Exception:
                    self.clients.remove(client)
    
    def stop(self):
        logger.info("Stopping TCP Server...")
        self.running = False
        with self.lock:
            for client in self.clients[:]:
                try:
                    client['socket'].close()
                except:
                    pass
            self.clients.clear()
        try:
            self.server_socket.close()
        except:
            pass

# Global TCP server (thread-safe access)
tcp_server = None
tcp_lock = threading.Lock()

# Lifespan events (replaces deprecated @app.on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    global tcp_server
    # Startup
    logger.info("🚀 Starting TCP Server...")
    tcp_server = TCPServer(host='127.0.0.1', port=5000)
    server_thread = threading.Thread(target=tcp_server.start, daemon=True)
    server_thread.start()
    logger.info("🚀 FastAPI + TCP Server started!")
    yield
    # Shutdown
    logger.info("🔴 Shutting down TCP Server...")
    with tcp_lock:
        if tcp_server:
            tcp_server.stop()
    logger.info("🔴 All services stopped")

# FastAPI app
app = FastAPI(title="FastAPI + TCP Chat Server", lifespan=lifespan)

# Secure CORS (no wildcard *)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.get("/")
def read_root():
    return {"message": "FastAPI + TCP Chat Server running ✅"}

@app.get("/tcp/clients")
def get_tcp_clients():
    global tcp_server
    with tcp_lock:
        if tcp_server is None:
            return {"error": "TCP Server not initialized", "client_count": 0}
        with tcp_server.lock:
            return {
                "online_names": tcp_server.names.copy(),
                "client_count": len(tcp_server.clients),
                "tcp_port": 5000,
                "status": "running"
            }

# User CRUD
@app.get("/users", response_model=List[dict])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(Users).all()

@app.post("/users", response_model=dict)
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = Users(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User created: {db_user.name}")
    return db_user

@app.get("/users/search")
def search_user(name: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.name == name).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users", response_model=dict)
def update_user(update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.name == update.name).first()
    if user:
        for key, value in update.dict().items():
            setattr(user, key, value)
        db.commit()
        db.refresh(user)
        logger.info(f"User updated: {user.name}")
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        logger.info(f"User deleted: {user.name}")
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"WebSocket Echo: {data}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
