import cv2
import numpy as np
import BOTTLE
import GOTO

list_bottles = list()


class Haar():
    """Class that is in charg of doing the haar cascade
    and that calls the class bottle"""

    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.compteur_bottle = 0
        self.compteur_direction = 0
        self.goto = GOTO.Goto()

    def rectangles(self,img):
        height = np.size(img, 0)
        width = np.size(img, 1)

        center_x = width / 2
        center_y = height / 2

        bottle_cascade = cv2.CascadeClassifier('cascade.xml')

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        bottles = bottle_cascade.detectMultiScale(gray, 1.3, 5)

        detection = 0

        for (x, y, w, h) in bottles:
            detection = 1
            rect_center_x = x + w / 2
            rect_center_y = y + h / 2

            angle = np.degrees(np.arctan2((rect_center_x - center_x),rect_center_y))
            if (len(list_bottles)==0):
                print('First bottle')
                list_bottles.append(BOTTLE.Bottle(rect_center_x, rect_center_y, angle))
                list_bottles[-1].add_name(0)
                indice_comp=0
            else:
                # CHECK if new bottle
                indice_comp = list_bottles[-1].comparison(rect_center_x,rect_center_y,angle,list_bottles)

            img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img, 'bottle'+str(indice_comp), (x, y), self.font, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)

        if detection == 0 and len(list_bottles)>0:
            list_bottles[-1].no_detection(list_bottles)

        if self.compteur_direction >= 10:
            # direction(bottles)->dans bottle
            if len(list_bottles)>0:
                l = 0
                indice_go = 0
                detection = 0
                while(l<len(list_bottles)):
                    #check which bottle has more detection
                    if list_bottles[l].quantity>detection:
                        detection = list_bottles[l].quantity
                        indice_go = l
                    l +=1
                self.goto.move(list_bottles[indice_go].angle)
            self.compteur_direction = 0


        if self.compteur_bottle == 5:
            self.compteur_bottle = 0
            if len(list_bottles)>0:
                list_bottles[-1].delete_no_detection(list_bottles)

        return img



    def __del__(self):  # class destructor
            """destructor of the class"""
