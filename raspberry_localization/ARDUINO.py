import serial
import time

class Arduino():
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', 9600)
        c_recu = self.ser.read(1)
        while ord(c_recu) != 0:
            c_recu = self.ser.read(1)
        c_recu = self.ser.read(1)
        while ord(c_recu) != 255:
            c_recu = self.ser.read(1)
        c_recu = self.ser.read(1)
        while ord(c_recu) != 0:
            c_recu = self.ser.read(1)
        print('End initialization communication Arduino')

    def close(self):
        self.ser.close()

    def sendToArduino(self, function, angle):
        self.ser.write(chr(function))
        self.ser.write(chr(angle))
        print('Sent to Arduino')
