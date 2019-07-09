import socket
from time import sleep
import sys
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 8089))

while True:
    my_str = 'hello'
    print(f'Bytes to be sent: {sys.getsizeof(my_str)}')
    
    clientsocket.send(my_str.encode())
    