import numpy as np
import cv2
import math

class Beacon:
    def __init__(self):

        # hsv-converted image
        self.hsv = 0

        # visibility (total and every color)
        self.visible = 0
        self.red_visible = 0
        self.green_visible = 0
        self.blue_visible = 0
        self.yellow_visible = 0

        # corner (which lights to triangulate)
        self.corner = 0

        # color coord moment
        self.red_x = 0
        self.red_y = 0
        self.green_x = 0
        self.green_y = 0
        self.blue_x = 0
        self.blue_y = 0
        self.yellow_x = 0
        self.yellow_y = 0

        # color-bearings
        self.red_ang = 0
        self.green_ang = 0
        self.blue_ang = 0
        self.yellow_ang = 0

        # bearing "second" and "third" light (anti-clockwise)
        self.alpha = 0
        # bearing "first" and "second" light (anti-clockwise)
        self.beta = 0
        # angle "first" light to robot direction
        self.delta = 0

        # Robot coordinates and direction (rad)
        self.R_x = 0
        self.R_y = 0
        self.R_dir = 0

        # Coordonates of the beacons on the map
        self.beaconred_x = 0
        self.beaconred_y = 0
        self.beacongreen_x = 8
        self.beacongreen_y = 0
        self.beaconyellow_x = 0
        self.beaconyellow_y = 8
        self.beaconblue_x = 8
        self.beaconblue_y = 8

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        return

    def Crop(self, img):

        # crop to the center of the image (found by inspection)
        c_x = 244
        c_y = 322
        r = 130
        cimg = img[(c_x - r):(c_x + r), (c_y - r):(c_y + r)]

        # crop unuseful areas to circular picture
        black = np.zeros((2 * r, 2 * r, 3), np.uint8)
        cv2.circle(black, tuple([r, r]), 130, (255, 255, 255), -1)
        cv2.circle(black, tuple([r, r]), 100, (0, 0, 0), -1)
        cimg = cv2.bitwise_and(cimg, black)

        # cover unuseful area in center by drawing a circle
        cv2.circle(cimg, (r, r), 100, (0, 0, 0), -1)

        #enlarge to 500 by 500 
        t = 500.0 / cimg.shape[1]
        dim = (500, int(cimg.shape[0] * t))
        cimg = cv2.resize(cimg, dim, interpolation=cv2.INTER_AREA)

        #flip picture for proper orientation (seen from above)
        cimg = cv2.flip(cimg, 0)

        #set picture parameter (center, direction and radius)
        self.x_c = 250
        self.y_c = 250
        self.x_dir = 250
        self.y_dir = 0
        self.r = 250

        return cimg

    def RGBtoHSV(self, cimg):
        # Convert BGR to HSV
        hsv = cv2.cvtColor(cimg, cv2.COLOR_BGR2HSV)
        return hsv

    def processing(self, hsv):

        # color thresholding
        t_r, t_g, t_b, t_y = self.thresholding(hsv)

        # filter images by applying "opening"
        op_r, op_g, op_b, op_y = self.filtering(t_r, t_g, t_b, t_y)

        # detect by find contours, take moments to find center of contours,
        self.moments(op_r, op_g, op_b, op_y)
        return

    def thresholding(self, hsv):
        # create color-thresholded images with HSV-ranges
        lower_red = np.array([0, 110, 150])
        upper_red = np.array([20, 255, 255])
        lower_green = np.array([65, 100, 100])
        upper_green = np.array([85, 255, 255])
        lower_blue = np.array([90, 100, 100])
        upper_blue = np.array([110, 255, 255])
        lower_yellow = np.array([20, 0, 170])
        upper_yellow = np.array([35, 100, 255])

        #color filter (pos/neg)
        thresh_red = cv2.inRange(hsv, lower_red, upper_red)
        thresh_green = cv2.inRange(hsv, lower_green, upper_green)
        thresh_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        thresh_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        return thresh_red, thresh_green, thresh_blue, thresh_yellow

    def filtering(self, thresh_red, thresh_green, thresh_blue, thresh_yellow):
        # filter images by applying "opening"

        # filter parameters
        kernel_red = np.ones((3, 3), np.uint8)
        kernel_blue = np.ones((3, 3), np.uint8)
        kernel_green = np.ones((3, 3), np.uint8)
        kernel_yellow = np.ones((3, 3), np.uint8)

        # clear noise by "opening"
        open_red = cv2.morphologyEx(thresh_red, cv2.MORPH_OPEN, kernel_red)
        open_blue = cv2.morphologyEx(thresh_blue, cv2.MORPH_OPEN, kernel_blue)
        open_green = cv2.morphologyEx(thresh_green, cv2.MORPH_OPEN, kernel_green)
        open_yellow = cv2.morphologyEx(thresh_yellow, cv2.MORPH_OPEN, kernel_yellow)

        return open_red, open_green, open_blue, open_yellow

    def moments(self, open_red, open_green, open_blue, open_yellow):
        # detect if lights present and if so where from filter

        #reset visibilities
        self.visible = 0
        self.red_vis = 0
        self.green_vis = 0
        self.blue_vis = 0

        # find red contours
        _, contours_red, _ = cv2.findContours(open_red, 1, 2)

        # if no contours, not visible
        if not contours_red:
            self.red_vis = 0
            self.red_x = 0
            self.red_y = 0

        else:
            # check area of contour
            cnt_red = contours_red[0]
            area_red = cv2.contourArea(cnt_red)

            # check area is adequate, calculate moment
            if area_red > 3 and area_red < 200:
                self.red_vis = 1
                M = cv2.moments(cnt_red)
                self.red_x = int(M['m10'] / M['m00'])
                self.red_y = int(M['m01'] / M['m00'])
                self.red_x = float(self.red_x)
                self.red_y = float(self.red_y)

        # find green contours
        _, contours_green, _ = cv2.findContours(open_green, 1, 2)

        # if no contours, not visible
        if not contours_green:
            self.green_vis = 0
            self.green_x = 0
            self.green_y = 0

        else:
            # check area of contour
            cnt_green = contours_green[0]
            area_green = cv2.contourArea(cnt_green)

            # if area appears adequate, calculate moment
            if area_green > 3 and area_green < 200:
                self.green_vis = 1
                M = cv2.moments(cnt_green)
                self.green_x = int(M['m10'] / M['m00'])
                self.green_y = int(M['m01'] / M['m00'])
                self.green_x = float(self.green_x)
                self.green_y = float(self.green_y)

                # find blue contours
        _, contours_blue, _ = cv2.findContours(open_blue, 1, 2)

        # if no contours, not visible
        if not contours_blue:
            self.blue_vis = 0
            self.blue_x = 0
            self.blue_y = 0
        # check area of contour
        else:
            cnt_blue = contours_blue[0]
            area_blue = cv2.contourArea(cnt_blue)

            # if area appears adequate, calculate moment
            if area_blue > 3 and area_blue < 200:
                self.blue_vis = 1
                M = cv2.moments(cnt_blue)
                self.blue_x = int(M['m10'] / M['m00'])
                self.blue_y = int(M['m01'] / M['m00'])
                self.blue_x = float(self.blue_x)
                self.blue_y = float(self.blue_y)

        # find yellow contours
        _, contours_yellow, _ = cv2.findContours(open_yellow, 1, 2)

        # if no contours, not visible
        if not contours_yellow:
            self.yellow_vis = 0
            self.yellow_x = 0
            self.yellow_y = 0

        else:
            # check area of contour
            cnt_yellow = contours_yellow[0]
            area_yellow = cv2.contourArea(cnt_yellow)

            # if area appears adequate, calculate moment
            if area_yellow > 3 and area_yellow < 200:
                self.yellow_vis = 1
                M = cv2.moments(cnt_yellow)
                self.yellow_x = int(M['m10'] / M['m00'])
                self.yellow_y = int(M['m01'] / M['m00'])
                self.yellow_x = float(self.yellow_x)
                self.yellow_y = float(self.yellow_y)


        #add number of visible lights
        self.visible = self.red_vis + self.green_vis + self.blue_vis + self.yellow_vis

        return

    def set_corners(self):
        #choose corners to triangulate on

        if self.visible < 3:
            self.corner = 0

        else:
            if self.visible == 4:
                # if all lights detected triangulate Blue-Green-Red
                self.corner = 1

            if self.yellow_vis == 0:
                # if yellow missing triangulate Blue-Green-Red
                self.corner = 1

            if self.red_vis == 0:
                # if red missing triangulate Yellow-Blue-Green
                self.corner = 2

            if self.green_vis == 0:
                # if green missing triangulate Red-Yellow-Blue
                self.corner = 3

            if self.blue_vis == 0:
                # if blue missing triangulate Green-Red-Yellow
                self.corner = 4

        return

    def angle_calc(self):
        # calculation of angles
        #the arctan (atan) function only returns -pi/2 to +pi/2
        #with the robot direction being the origin the range of angle should
        #be given as -pi to +pi. Thus there are three cases.
        #first/fourth quadrant: returns angles -pi/2 to +pi/2
        #second quadrant: returns +pi/2 to +pi
        #third quadrant: returns -pi to -pi/2

        # if red detected
        if self.red_vis == 1 and (self.y_c - self.red_y) != 0:

            # first or fourth quadrant
            if self.red_y < self.y_c:
                self.red_ang = math.atan((self.x_c - self.red_x) / (self.y_c - self.red_y))
                self.red_deg = int((math.atan((self.x_c - self.red_x) / (self.y_c - self.red_y))) * 180 / math.pi)

            else:
                # second quadrant
                if self.red_x < self.x_c:
                    self.red_ang = (math.pi + math.atan((self.x_c - self.red_x) / (self.y_c - self.red_y)))
                    self.red_deg = int(
                        (math.pi + math.atan((self.x_c - self.red_x) / (self.y_c - self.red_y))) * 180 / math.pi)

                # third quadrant
                else:
                    self.red_ang = (-math.pi + math.atan((self.x_c - self.red_x) / (self.y_c - self.red_y)))
                    self.red_deg = int(
                        (-math.pi + math.atan((self.x_c - self.red_x) / (self.y_c - self.red_y))) * 180 / math.pi)

        # if green detected
        if self.green_vis == 1 and (self.y_c - self.green_y) != 0:

            # first or fourth quadrant
            if self.green_y < self.y_c:
                self.green_ang = math.atan((self.x_c - self.green_x) / (self.y_c - self.green_y))
                self.green_deg = int((math.atan((self.x_c - self.green_x) / (self.y_c - self.green_y))) * 180 / math.pi)

            else:
                # second quadrant
                if self.green_x < self.x_c:
                    self.green_ang = (math.pi + math.atan((self.x_c - self.green_x) / (self.y_c - self.green_y)))
                    self.green_deg = int(
                        (math.pi + math.atan((self.x_c - self.green_x) / (self.y_c - self.green_y))) * 180 / math.pi)

                # third quadrant
                else:
                    self.green_ang = (-math.pi + math.atan((self.x_c - self.green_x) / (self.y_c - self.green_y)))
                    self.green_deg = int(
                        (-math.pi + math.atan((self.x_c - self.green_x) / (self.y_c - self.green_y))) * 180 / math.pi)

        # if blue detected
        if self.blue_vis == 1 and (self.y_c - self.blue_y) != 0:

            # first or fourth quadrant
            if self.blue_y < self.y_c:
                self.blue_ang = math.atan((self.x_c - self.blue_x) / (self.y_c - self.blue_y))
                self.blue_deg = int((math.atan((self.x_c - self.blue_x) / (self.y_c - self.blue_y))) * 180 / math.pi)

            else:
                # second quadrant
                if self.blue_x < self.x_c:
                    self.blue_ang = (math.pi + math.atan((self.x_c - self.blue_x) / (self.y_c - self.blue_y)))
                    self.blue_deg = int(
                        (math.pi + math.atan((self.x_c - self.blue_x) / (self.y_c - self.blue_y))) * 180 / math.pi)

                # third quadrant
                else:
                    self.blue_ang = (-math.pi + math.atan((self.x_c - self.blue_x) / (self.y_c - self.blue_y)))
                    self.blue_deg = int(
                        (-math.pi + math.atan((self.x_c - self.blue_x) / (self.y_c - self.blue_y))) * 180 / math.pi)

        # if yellow detected
        if self.yellow_vis == 1 and (self.y_c - self.yellow_y) != 0:

            # first or fourth quadrant
            if self.yellow_y < self.y_c:
                self.yellow_ang = ((math.atan((self.x_c - self.yellow_x) / (self.y_c - self.yellow_y))))
                self.yellow_deg = int(
                    (math.atan((self.x_c - self.yellow_x) / (self.y_c - self.yellow_y))) * 180 / math.pi)


            else:
                # second quadrant
                if self.yellow_x < self.x_c:
                    self.yellow_ang = (math.pi + math.atan((self.x_c - self.yellow_x) / (self.y_c - self.yellow_y)))
                    self.yellow_deg = int(
                        (math.pi + math.atan((self.x_c - self.yellow_x) / (self.y_c - self.yellow_y))) * 180 / math.pi)

                # third quadrant
                else:
                    self.yellow_ang = (-math.pi + math.atan((self.x_c - self.yellow_x) / (self.y_c - self.yellow_y)))
                    self.yellow_deg = int(
                        (-math.pi + math.atan((self.x_c - self.yellow_x) / (self.y_c - self.yellow_y))) * 180 / math.pi)

        return

    def angle_set(self):
        # choose which angles to triangulate on

        # delta: angle between direction of robot and angle to "first" light
        # beta: angle btw first and second light (trig/anti-clockwise sense)
        # alpha: angle btw second and third light (trig/anti-clockwise sense)

        # corner: parameter of which three lights are available
        # 0: 2 or less lights, 1: centered on green (RGB),
        # 2: centered on red, 3: centered on yellow, 4: centered on blue

        # set alpha, beta and delta

        if self.corner == 1:
            self.alpha = self.red_ang - self.green_ang
            self.beta = self.green_ang - self.blue_ang
            self.delta = self.blue_ang

        if self.corner == 2:
            self.alpha = self.yellow_ang - self.red_ang
            self.beta = self.red_ang - self.green_ang
            self.delta = self.green_ang

        if self.corner == 3:
            self.alpha = self.blue_ang - self.yellow_ang
            self.beta = self.yellow_ang - self.red_ang
            self.delta = self.red_ang

        if self.corner == 4:
            self.alpha = self.green_ang - self.blue_ang
            self.beta = self.blue_ang - self.yellow_ang
            self.delta = self.yellow_ang

        #ensures alpha and beta are of the correct form i.e. btw -pi and pi.

        if self.alpha > math.pi:
            self.alpha = abs(self.alpha - 2*math.pi)
        if self.beta > math.pi:
            self.beta = abs(self.beta - 2*math.pi)
        if self.alpha < (-math.pi):
            self.alpha = abs(self.alpha + 2*math.pi)
        if self.beta < (-math.pi):
            self.beta = abs(self.beta + 2*math.pi)
        if self.alpha>(-math.pi) and self.alpha<math.pi:
            self.alpha=abs(self.alpha)
        if self.beta>(-math.pi) and self.beta<math.pi:
            self.beta=abs(self.beta)

        #if not enough lights visible no angles to triangulate
        if self.corner == 0:
            self.alpha = 0
            self.beta = 0
            self.delta = 0

        return

    def triangulation(self):
        # triangulates position if 3 lights are detected

        # delta: angle between direction of robot and angle to "first" light
        # alpha: angle btw second and third light (trig/anti-clockwise sense)
        # beta: angle btw first and second light (trig/anti-clockwise sense)
        # corner: parameter of which three lights are available
        # 0: 2 or less lights, 1: centered on green,
        # 2: centered on red, 3: centered on yellow, 4: centered on blue

        # phi is a constructed angle
        phi = math.atan(math.sin(self.alpha) / math.sin(self.beta))
        K = 2 * math.pi - self.alpha - self.beta - (math.pi / 2)
        W = 2 * math.atan(math.tan((math.pi / 4) - phi) * math.tan(0.5 * (self.alpha + self.beta + (math.pi / 2))))

        # x and y are complement angles to alpha and beta
        x = (K + W) / 2
        y = (K - W) / 2

        # arena side length
        S = 8

        # length to center beacon
        if abs(math.sin(self.beta)) > abs(math.sin(self.alpha)):
            d_second = S * math.sin(y) / math.sin(self.beta)
        else:
            d_second = S * math.sin(x) / math.sin(self.alpha)

        # d_first = math.sqrt(S*S + d_second*d_second - 2*S*d_second*math.cos(math.pi-beta-y))
        d_third = math.sqrt(S * S + d_second * d_second - 2 * S * d_second * math.cos(math.pi - self.alpha - x))

        # local coordinates (different coordinate system)
        x_loc = math.sin(x) * d_third
        y_loc = math.cos(x) * d_third
        loc_dir = 1.5 * math.pi - x - self.alpha - self.beta - self.delta

        # angle Red-Green (alpha) Green-Blue (beta)
        if self.corner == 1:
            self.R_x = x_loc
            self.R_y = y_loc
            self.R_dir = loc_dir
            
        # angle Yellow-Red (alpha) Red-Green (beta)
        if self.corner == 2:
            self.R_x = S - y_loc
            self.R_y = x_loc
            self.R_dir = loc_dir + (0.5 * math.pi)
            
        # angle Blue-Yellow (alpha) Yellow-Red (beta)
        if self.corner == 3:
            self.R_x = S - x_loc
            self.R_y = S - y_loc
            self.R_dir = loc_dir + (math.pi)
        # angle Green-Blue (alpha) Blue-Yellow (beta)
        if self.corner == 4:
            self.R_x = y_loc
            self.R_y = S - x_loc
            self.R_dir = loc_dir + (1.5 * math.pi)

        # R_x, R_y: robot coordinates in global coordinate system
        # R_dir: robot direction in global coordinate system (trigonometric/anti-clockwise

        return self.R_x, self.R_y, self.R_dir

    def draw_colors(self, cimg):
        # illustrates lights, detected, angles and position
        # this function is not required for functional purposes, only verification

        RED_x = int(self.red_x)
        RED_y = int(self.red_y)
        GREEN_x = int(self.green_x)
        GREEN_y = int(self.green_y)
        BLUE_x = int(self.blue_x)
        BLUE_y = int(self.blue_y)
        YELLOW_x = int(self.yellow_x)
        YELLOW_y = int(self.yellow_y)
        X_c = int(self.r)
        Y_c = int(self.r)
        X_dir = int(self.r)
        Y_dir = int(0)
        ALPHA = int(self.alpha * 180 / math.pi)
        BETA = int(self.beta * 180 / math.pi)
        R_X = round(self.R_x, 2)
        R_Y = round(self.R_y, 2)

        # direction-line center=>forward
        cv2.line(cimg, (X_dir, Y_dir), (X_c, Y_c), (255, 255, 255), 2)

        # draw color angles
        if self.red_vis == 1:
            cv2.line(cimg, (RED_x, RED_y), (X_c, Y_c), (0, 0, 255), 2)
            cv2.putText(cimg, str(self.red_ang), (RED_x, RED_y), self.font, 1, (0, 0, 255))

        if self.green_vis == 1:
            cv2.line(cimg, (GREEN_x, GREEN_y), (X_c, Y_c), (0, 255, 0), 2)
            cv2.putText(cimg, str(self.green_ang), (GREEN_x, GREEN_y), self.font, 1, (0, 255, 0))

        if self.blue_vis == 1:
            cv2.line(cimg, (BLUE_x, BLUE_y), (X_c, Y_c), (255, 0, 0), 2)
            cv2.putText(cimg, str(self.blue_ang), (BLUE_x, BLUE_y), self.font, 1, (255, 0, 0))

        if self.yellow_vis == 1:
            cv2.line(cimg, (YELLOW_x, YELLOW_y), (X_c, Y_c), (0, 255, 255), 2)
            cv2.putText(cimg, str(self.yellow_ang), (YELLOW_x, YELLOW_y), self.font, 1, (0, 255, 255))

        if self.visible > 2:
            cv2.putText(cimg, "alpha", (0, 150), self.font, 1, (0, 0, 255))
            cv2.putText(cimg, "beta", (0, 200), self.font, 1, (0, 0, 255))
            cv2.putText(cimg, str(ALPHA), (80, 150), self.font, 1, (255, 0, 0))
            cv2.putText(cimg, str(BETA), (80, 200), self.font, 1, (255, 0, 0))

            cv2.putText(cimg, "R_x", (0, 50), self.font, 1, (0, 0, 255))
            cv2.putText(cimg, "R_y", (0, 100), self.font, 1, (0, 0, 255))
            cv2.putText(cimg, str(R_X), (80, 50), self.font, 2, (0, 255, 255))
            cv2.putText(cimg, str(R_Y), (80, 100), self.font, 2, (0, 255, 255))

            cv2.putText(cimg, "Red", (0, 250), self.font, 1, (255,0,0))
            red_deg=self.red_ang*180/math.pi
            cv2.putText(cimg, str(red_deg), (80,250), self.font, 1, (255,0,0))

            cv2.putText(cimg, "Blue", (0, 300), self.font, 1, (0,0,255))
            blue_deg=self.blue_ang*180/math.pi
            cv2.putText(cimg, str(blue_deg), (80,300), self.font, 1, (0,0,255))

            cv2.putText(cimg, "Yellow", (0, 350), self.font, 1, (255,255,0))
            yellow_deg=self.yellow_ang*180/math.pi
            cv2.putText(cimg, str(yellow_deg), (80,350), self.font, 1, (255,255,0))

            cv2.putText(cimg, "Green", (0, 400), self.font, 1, (0,255,0))
            green_deg=self.green_ang*180/math.pi
            cv2.putText(cimg, str(green_deg), (80,400), self.font, 1, (0,255,0))
            

        return cimg
