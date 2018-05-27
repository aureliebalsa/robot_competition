# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import BEACON
import PATH_PLANNING
import numpy as np

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('beacon.avi', fourcc, 20.0, (500, 500))

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)
compteur = 0

path = PATH_PLANNING.Path_planning()

file = open("Pos.text", "w+")
file.write("start")
file.close

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame.array
    image = path.localize(img)

    f = open("Pos.txt", "a+");
    if path.localization.visible > 2:
        if path.localization.beta == 0:
            path.localization.R_x, path.localization.R_y = [-1, -1]
            f.write("error \n")
            pass
        else:
            R_x, R_y, R_dir = path.localization.triangulation()
            R_deg = R_dir * 180 / np.pi
            f.write("R_x: ")
            f.write(str(R_x))
            f.write("R_y: ")
            f.write(str(R_y))
            f.write("R_deg: ")
            f.write(str(R_deg))
            f.write("\n")

    else:
        path.localization.R_x, path.localization.R_y = [-1, -1]
        print("error")
    f.close()
    path.destination()
    image = path.localization.draw_colors(image)
    cv2.imshow("Frame", image)
    # show the frame
    #out.write(image)
    key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
