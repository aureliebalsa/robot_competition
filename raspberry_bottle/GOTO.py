import TCP_BOTTLE

class Goto:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.angle = 0
        self.communication = TCP_BOTTLE.Socket_bottle()

    def move(self,angle):
        """Call the Raspberry to give the direction"""
        self.communication.sending_data(str(angle))

    def __del__(self):  # class destructor
        """destructor"""
