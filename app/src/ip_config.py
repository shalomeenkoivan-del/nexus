import socket

def get_server_ip():
    return socket.gethostbyname(socket.gethostname())