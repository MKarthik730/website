from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import threading
import socket


from data import users, usersupdate
from database import SessionLocal, engine
import databasemodels
from databasemodels import Users


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
                print(f"TCP Connection from {client_addr}")
                
                with self.lock:
                    self.clients.append({'socket': client_socket, 'addr': client_addr})
                
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_addr)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("TCP Server shutting down...")
            self.stop()
    
    def handle_client(self, client_socket, client_addr):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    print(f"TCP Client {client_addr} disconnected")
                    break
                
                message = data.decode('utf-8').strip()
                if not message:
                    continue
                
                print(f"TCP From {client_addr[0]}: {message}")
                
                with self.lock:
                    if message not in self.names:
                        self.names.append(message)
                
                response = f"Echo: {message}".encode('utf-8')
                client_socket.sendall(response)
                
                self.broadcast(f"{client_addr[0]}: {message}", exclude_addr=client_addr)
                self.intimate()
                
        except Exception as e:
            print(f"TCP Error: {e}")
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
    
    def intimate(self):
        names_str = f"Online: {', '.join(self.names)}"
        with self.lock:
            for client in self.clients:
                try:
                    client['socket'].sendall(names_str.encode('utf-8'))
                except:
                    pass
    
    def stop(self):
        print("Stopping TCP Server...")
        with self.lock:
            for client in self.clients[:]:
                try:
                    client['socket'].close()
                except:
                    pass
            self.clients.clear()
        self.server_socket.close()


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", ""], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


databasemodels.Base.metadata.create_all(bind=engine)

def get_db():
    db_instance = SessionLocal()
    try:
        yield db_instance        
    finally:
        db_instance.close()


tcp_server = None


@app.on_event("startup")
async def startup_event():
    global tcp_server
    tcp_server = TCPServer(host='127.0.0.1', port=5000)
    server_thread = threading.Thread(target=tcp_server.start, daemon=True)
    server_thread.start()
    print("🚀 FastAPI + TCP Server started!")

@app.on_event("shutdown")
async def shutdown_event():
    global tcp_server
    if tcp_server:
        tcp_server.stop()
    print("🔴 All services stopped")


@app.get("/tcp/clients")
def get_tcp_clients():
    if tcp_server:
        with tcp_server.lock:
            return {
                "online_names": tcp_server.names,
                "client_count": len(tcp_server.clients),
                "tcp_port": 5000
            }
    return {"error": "TCP Server not running"}


@app.get("/")
def login():
    return {"message": "FastAPI + TCP Chat Server running"}

@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(Users).all()

@app.post("/users")
def add_user(usr: users, db: Session = Depends(get_db)):
    new_user = databasemodels.Users(
        name=usr.name,
        age=usr.age,
        number=usr.number,
        salary=usr.salary
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.delete('/users/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db)):
    d_user = db.query(Users).filter(Users.id == id).first()
    if d_user:
        db.delete(d_user)
        db.commit()
        return
    else:
        raise HTTPException(status_code=404, detail="not found")

@app.get("/users/search")
def search_user(name: str, db: Session = Depends(get_db)):
    usr_v = db.query(Users).filter(Users.name == name).first()
    if not usr_v:
        raise HTTPException(status_code=404, detail="user not found")
    return usr_v

@app.put("/users")
def update_user(update: usersupdate, db: Session = Depends(get_db)):
    usr_v = db.query(Users).filter(Users.name == update.name).first()
    if usr_v:
        usr_v.name = update.name
        usr_v.age = update.age
        usr_v.number = update.number
        usr_v.salary = update.salary
        db.commit()
        db.refresh(usr_v)
        return usr_v
    else:
        raise HTTPException(status_code=404, detail="user not found")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"WebSocket Echo: {data}")
    except:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
