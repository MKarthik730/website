import ssl
import socket

context = ssl.create_default_context()
conn = socket.create_connection(('facebook.com', 443))
ssock = context.wrap_socket(conn, server_hostname='facebook.com')


print("TLS handshake complete")
print(f"Protocol: {ssock.version}")
print(f"Cipher: {ssock.cipher()}")