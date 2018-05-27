# Robot Competition code

The aim of the robot competition is to have an autonomous robot able to pick up PET bottles and bring them back in a specific area.

For this project, two raspberries Pi and one arduino were used. One raspberry was used for the bottle recognition while the other one was used for the localization. The arduino was used for the control of the motors and the sensors for obstacle avoidance.

The raspberry localization was in charge of sending data to the arduino, based on the different goal from path planning and the position of the bottles. The position of the bottles were given by the raspberry bottle using socket communication.

## raspberry_bottle
It contains six different files that are all related to the raspberry used for bottle detection:

<ul><li>main_pi.py: Launch the camera and the bottle detection</li>
<li>HAAR.py: Bottle detection based on the file cascade.xml</li>
<li>BOTTLE.py: Analysis of the bottle detection, where is the bottle and tracking of the bottle</li>
<li>GOTO.py: Movement of the robot towards the bottle</li>
<li>TCP_BOTTLE.py: Socket communication with the other rapsberry</li>
<li>cascade.xml: Result of the trained cascade</li>
</ul>

## raspberry_localization
It contains three different files that are all related to the raspberry used for localization:

<ul><li>ARDUINO.py: Serial communication with the arduino</li>
<li>PATH_PLANNING.py: Definition of the path the robot should take when no bottle found</li>
<li>TCP_LOCALIZATION.py: Socket communcation with the other rapsberry</li>
</ul>

## videos
Both Haar videos are a proof of concept of the bottle detection.

The last video is a small demo of how the robot was working.

## Authors

Aurélie Balsa

This github contains only the code I programmed, however the competition was a team project of three people.

Other team members:  
Basile Audergon  
Björn Andersson  
