import ARDUINO
import BEACON
import TCP_LOCALIZATION

class Path_planning:
    def __init__(self):
        self.angle = 0
        self.arduino = ARDUINO.Arduino()
        self.localization = BEACON.Beacon()
        self.goalx = self.localization.beaconred_x
        self.goaly = self.localization.beaconred_y
        # AREA OF DESTINATION area 0  = rocks , area 1 = grass , area 2 = recycling, area 3 = ramp
        self.area = 0
        self.move = 85
        self.discharge = 90
        self.liftshovel_up = 165
        self.liftshovel_down = 170
        self.function = self.move
        self.communication = TCP_LOCALIZATION.Communication()
        self.up = 0

    def localize(self,img):
        image = self.localization.Crop(img)
        hsv = self.localization.RGBtoHSV(image)
        self.localization.processing(hsv)
        self.localization.set_corners()
        self.localization.angle_calc()
        self.localization.angle_set()
        return image

    def call_arduino(self,angle):
        """Call the Arduino to give the direction"""
        # angle between 0 and 255  for a value between -180 and 180 degres
        angle_arduino = int((angle + 180) * 256 / 360)
        self.arduino.sendToArduino(self.function,angle_arduino)

    def destination(self):
        if self.area == 0:
            # GO TO ROCK AREA
            self.function = self.move
            if self.localization.red_visible == 0:
                angle = -self.localization.red_ang
            else:
                angle = 0
            if self.goalx - self.localization.R_x < 0.5 and self.goaly - self.localization.R_y < 0.5:
                self.area +=1
                self.goalx = self.localization.beaconblue_x
                self.goaly = self.localization.beaconblue_y
                angle = -self.localization.blue_ang

        elif self.area == 1:
            # GO TO GRASS AREA
            self.function = self.move
            if self.localization.blue_visible == 0:
                angle = -self.localization.blue_ang
            else:
                angle = 0
            if self.goalx - self.localization.R_x < 0.5 and self.goaly - self.localization.R_y < 0.5:
                self.area +=1
                self.goalx = self.localization.beaconyellow_x
                self.goaly = self.localization.beaconyellow_y
                angle = -self.localization.yellow_ang

        elif self.area == 2:
            # GO TO RECYCLING AREA
            if self.localization.yellow_visible == 0:
                angle = -self.localization.yellow_ang
            else:
                angle = 0
            if self.goalx - self.localization.R_x < 0.5 and self.goaly - self.localization.R_y < 0.5:
                self.function = self.discharge
                self.area += 1
        elif self.area == 3:
            # GO TO THE RAMP AREA
            if self.localization.yellow_visible == 0:
                angle = -self.localization.green_ang
            else:
                angle = 0
            if self.goalx - self.localization.R_x < 0.5 and self.goaly - self.localization.R_y < 0.5:
                self.area = 2
                self.goalx = self.localization.beaconyellow_x
                self.goaly = self.localization.beaconyellow_y
                angle = -self.localization.yellow_ang

        # CHECKING IF THE ROBOT IS CLOSE TO THE ROCKS
        if self.localization.R_x >= 2 and self.localization.R_x <= 3:
            if self.localization.R_y >= 0 and self.localization.R_y <= 3 :
                self.function = self.liftshovel_up

        if self.localization.R_x >=0 and self.localization.R_x <=3:
            if self.localization.R_y >= 2.5 and self.localization.R_y <= 3:
                self.function = self.liftshovel_up

        if self.localization.R_x >=0 and self.localization.R_x <=2.5:
            if self.localization.R_y >= 0 and self.localization.R_y <= 2.5:
                self.function = self.liftshovel_down

        # CHECKING IF THE ROBOT IS CLOSE TO THE RAMP
        if self.localization.R_x <=3 and self.localization.R_y >= 7:
            if self.up == 0:
                self.function = self.liftshovel_up
            else :
                self.function = self.liftshovel_down
                self.up = 0

        if self.localization.R_x <=2 and self.localization.R_y >= 7:
            if self.up == 0 :
                self.function = self.liftshovel_down
                self.up = 1
            else :
                self.function = self.liftshovel_up

        if self.localization.R_x >=0 and self.localization.R_x <=2.5:
            if self.localization.R_y >= 0 and self.localization.R_y <= 2.5:
                self.function = self.liftshovel_down

        angle_bottle = self.communication.receive_data()
        if angle_bottle != 255:
            angle = angle_bottle

        self.call_arduino(angle)


