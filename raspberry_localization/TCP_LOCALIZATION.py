import socket

class Communication:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.bind(('', 9050))
        self.sock.listen(1)  # allow only 1 connection

        # Receive the data
        self.connection, self.addr = self.sock.accept()

    def receive_data(self):
        data = self.connection.recv(1024)   # the buffer in this example is 128 bytes
        if(data):
            print(data)
            angle = int(data)
            print('Done receiving')
        else:
            print('no data')
            angle = 255
        return angle

    def __del__(self):
        self.connection.close()