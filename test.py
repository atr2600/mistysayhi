import mistyPy
import os, requests, time
from xml.etree import ElementTree
import requests
from io import BytesIO
import time
import base64
import json

mistyIPAddress = "192.168.43.62"
robot = mistyPy.Robot(mistyIPAddress)
# robot.playAudio("tts.wav")

# robot.moveHead(1,1,1)
# robot.playAudio('temp.wav')

# {
#   "Pitch": -40,
#   "Roll": 0,
#   "Yaw": 0,
#   "Velocity": 60
# }  https://docs.mistyrobotics.com/misty-ii/reference/rest/#movehead


# assert roll in range(-5,6) and pitch in range(-5,6) and yaw in range(-5,6), " moveHead: Roll, Pitch and Yaw needs to be in range -5 to +5"

# Roll is head tilt left to right (-40,40,0)
# Pitch is head up and downt (-40,26)
# Yaw is left and right  (-81,81)
# First argument is tilt head, second is up and down, third is left and right
# robot.moveHead(-29,-10,-80,80)
# time.sleep(5)
# robot.moveHead(0,-7,0,90)
# time.sleep(5)
# robot.moveHead(29,-10,80,90)
# time.sleep(5)
# robot.moveHead(0,-7,0,90)
# time.sleep(5)

# robot.drive(0, 99, 505)
print("hello")
robot.driveTime(0, 100, 4000)
time.sleep(6)
robot.driveTime(0, -100, 4000)

# time.sleep(1)
# robot.drive(0, 0)