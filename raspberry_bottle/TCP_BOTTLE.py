import socket

class Socket_bottle:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('192.168.0.6', 9050))

    def sending_data(self,string):
        print('Sending...')
        self.sock.send(string)