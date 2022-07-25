#!/usr/bin/env pybricks-micropython
# This program requires LEGO EV3 MicroPython v2.0 or higher.
from math import floor
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.ev3devices import UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait
from pybricks.parameters import Button, Color
from uerrno import ENODEV
from velcalc.py import *

""" INITIALIZED  """
# Create your objects here.
ev3 = EV3Brick()

# Khoi tao ngoai vi
try:
    drv_mot = Motor(Port.A)
    Steer_mot = Motor(Port.B)
    ult_sen = UltrasonicSensor(Port.S1)
except OSError as ex:
    while True:
        ev3.speaker.beep(frequency=800, duration=100)
        ev3.screen.print("CONNECTION FAIL")
        if ((Button.CENTER in ev3.buttons.pressed()))
            break

""" MAIN """
ev3.speaker.beep(frequency=200, duration=100)

# Giữ bánh đánh lái đứng yên
Steer_mot.hold() #comment for mo phong

# chờ đến khi user nhấn CENTER
ev3.speaker.say("Press CENTER to go")


# Nhấn enter để chạy
while (not Button.CENTER in ev3.buttons.pressed()):    
    pass

demand2go_b = True

if (calculated_dist >= DIS_MAX or calculated_dist <= STOP_DIST):
    able2go_b = False
else:
    able2go_b = True
    
ev3.speaker.say("GEC GO")

array_len = 5
array = [0]*array_len
peek = 0

for i in range(array_len):
    array[i] = ult_sen.distance()
    
while True:
    
    # doc khoang cach
    peek = peek + 1
    peek = peek % array_len
    try:
        array[peek] = ult_sen.distance()
    except OSError as ex:
        while True:
            ev3.speaker.beep(frequency=800, duration=100)
            ev3.screen.print("CONNECTION FAIL, CHECK, RESET")
            drv_mot.run(0)
    
    for i in array:
        raw_dist += i 
    raw_dist = int(raw_dist/array_len)
    
    calculated_dist = raw_dist + DISOFFSET
    
    ev3.screen.print("dist: "+ str(calculated_dist) + "vel: " + str(vel))
    
    # kiem tra dieu kien nguy hiem
    if (calculated_dist <= STOP_DIST):
        able2go_b = False
    else:
        able2go_b = True
    
    # kiem tra menh lenh driver
    if (demand2go_b == True):
        # dieu khien xe
        if (able2go_b == True):
            
            if (calculated_dist <= REDUCE_VEL_ZONE - SMOOTH_CALIB):
                if (calculated_dist_old != calculated_dist):
                    vel = veloc_calc(calculated_dist)
            else:
                vel = veloc_calc(calculated_dist)

            calculated_dist_old = calculated_dist
        drv_mot.dc(vel) #comment for mo phong
                    
        # yeu cau nhan phanh khi gap nguy hiem
        if (able2go_b == False):
            ev3.light.on(Color.RED)
            safe_check_b = False
            vel = VEL_STOP
            demand2go_b = False
            
    # Chờ lệnh từ driver
    if (demand2go_b == False):
        
        # drv_mot.brake()
        drv_mot.run(0)
        
        if ((Button.DOWN in ev3.buttons.pressed()) and (able2go_b == True)):
            safe_check_b = True
            ev3.light.on(Color.YELLOW)
        if ((Button.UP in ev3.buttons.pressed()) and (able2go_b == True)):
            if (safe_check_b == True):
                ev3.light.on(Color.GREEN)
                ev3.speaker.say("OK GO")
                demand2go_b = True
        elif ((Button.UP in ev3.buttons.pressed()) and (able2go_b == False)):
            ev3.speaker.say("DANGER CAN NOT GO FORWARD")
            demand2go_b = False