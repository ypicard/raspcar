import socket
from flask import Flask
import threading
app = Flask(__name__)

data = []

def launch_socket_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8089))
    server_socket.listen(5) # become a server socket, maximum 5 connections
    print(f"Socker server listening on port {8089}")
    connection, address = server_socket.accept()
    while True:
        
        buf = connection.recv(1024)
        if len(buf) > 0:
            print('buf' + str(buf))
            data.append(buf.decode())


@app.route("/")
def hello():
    return "Hello World! " + str(len(data))


print("Start thread")
t = threading.Thread(target=launch_socket_server)
t.start()

print("Start flask")
app.run(host='localhost', port=8080)
