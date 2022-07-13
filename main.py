#!/usr/bin/env pybricks-micropython
# This program requires LEGO EV3 MicroPython v2.0 or higher.
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.ev3devices import UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait
from pybricks.media.ev3dev import SoundFile, ImageFile
from pybricks.parameters import Button


# user define
# import button_usr

""" INITIALIZED  """
# Create your objects here.
ev3 = EV3Brick()

# Khoi tao ngoai vi
drv_mot = Motor(Port.A)
Steer_mot = Motor(Port.B)
ult_sen = UltrasonicSensor(Port.S1)

# Khoi tao bien
offset = 0
VEL_MAX = 1000 # Degree per second (DPS)
vel_StrtReduce_dist = 500 #mm khoang cach xe bat dau giam toc do
stop_dist = 50 #mm khoang cach phai dung lai

velFactor = VEL_MAX/(vel_StrtReduce_dist - stop_dist) #He so toc do. dam bao toc do giam ve 0
raw_dist = ult_sen.distance()
calculated_dist = raw_dist + offset
vel = VEL_MAX

""" MAIN """
# Giu banh lai dung yen khi di chuyen thang.
#  screen.print(*args, sep=' ', end='\n')
Steer_mot.hold()


ev3.speaker.beep(frequency=200, duration=100)
ev3.speaker.say("Con cac")
# ev3.speaker.say("Press!")

pressed = []
button = 0

ev3.speaker.say("Press CENTER to go")
while button != Button.CENTER:    
    pressed = ev3.buttons.pressed()
    if(len(pressed) > 0):
        button = pressed[0]
    ev3.screen.print("PRESS CENTER TO GO")

ev3.speaker.say("GET GO")

# bat dau tang toc

for i in range(0, VEL_MAX, 10 ):
    raw_dist = ult_sen.distance()
    calculated_dist = raw_dist + offset
    
    if (calculated_dist > vel_StrtReduce_dist):
        vel = i
        drv_mot.run(vel)
        # wait(1) # trong vong 2s tang tu 0 den max toc do
    else:
        # dung tang toc khi:
        # bat ngo gap vat can
        # xe nam trong vung giam toc
        break
        

ev3.speaker.say("Tang toc xong")

# array_len = 2
# peek = 0
# array = [0]*array_len

# for i in range(array_len):
#     array[i] = ult_sen.distance()

while True:

    # read button
    pressed = ev3.buttons.pressed()
    if(len(pressed) > 0):
        button = pressed[0]
        
    #calculate toc do giua vao khoang cach giua xe vs vat can
    offset = 0
    
    # peek = peek + 1
    # peek = peek % array_len
    # print(len(array))
    # raw = ult_sen.distance()
    # array[peek] = raw
    # for i in array:
    #     raw_dist += i
        
    # raw_dist = int(raw_dist/array_len)
    raw_dist = ult_sen.distance()
    
    calculated_dist = raw_dist + offset
    
    
    # wait(10)
    # print(real_dist)
    if (calculated_dist < vel_StrtReduce_dist):
        vel = int(VEL_MAX - (vel_StrtReduce_dist - calculated_dist)*velFactor)
    
    # #gioi han min,max cho toc do
    if (vel > VEL_MAX): 
        vel = VEL_MAX
    if (vel < 0): 
        vel = 0

    # if (calculated_dist < 50 and calculated_dist >= 2550):
    #     vel = 0
    # else:
    #     vel = 500
        
    drv_mot.run(vel)
    
    ev3.screen.print(str(calculated_dist) + "," + str(vel))