#!/usr/bin/env pybricks-micropython
# This program requires LEGO EV3 MicroPython v2.0 or higher.
from math import floor
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.ev3devices import UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait
from pybricks.parameters import Button, Color


""" INITIALIZED  """
# Create your objects here.
ev3 = EV3Brick()

# Khoi tao ngoai vi
drv_mot = Motor(Port.A)
Steer_mot = Motor(Port.B)
ult_sen = UltrasonicSensor(Port.S1)

# Khoi tao bien
pressed = [] #mang luu gia tri nut nhan
button = 0 #bien luu gia tri nut nhan

VEL_MAX = 1050 #dps Degree per second (DPS)
VEL_MIN_CANMOVE = 10 #dps toc do nho nhat co the lam di chuyen xe
VEL_STOP = 0 #stop 

DISOFFSET = 0 #mm bu so sai lech khoang cach thuc te voi ket qua do duoc
STOP_DIST = 45 #mm khoang cach phai dung lai
REDUCE_VEL_ZONE = 150 #mm vung giam toc: khoang cach tu xe den vat can. trong vung nay xe bat dau giam toc do
DIS_MAX = 2550 #mm k co vat can hoac vat can qua gan truoc cam bien.

"""
phương trình vận tốc - khoảng cách : vantoc(khoangcach) = a*khoangcach +b

van toc: VEL_MIN_CANMOVE -> VEL_MAX
khoang cach: STOP_DIST -> REDUCE_VEL_ZONE
    
b1 dat phuong trinh
    veloc = a*distance + b    
b2 ta co
    VEL_MIN_CANMOVE = a*STOP_DIST + b
    VEL_MAX = a*REDUCE_VEL_ZONE + b
b3 tinh a va b
    a = (VEL_MAX - VEL_MIN_CANMOVE)/(REDUCE_VEL_ZONE - STOP_DIST)
    b = VEL_MAX - a*REDUCE_VEL_ZONE
"""
VELFACTOR = (VEL_MAX - VEL_MIN_CANMOVE)/(REDUCE_VEL_ZONE - STOP_DIST)
VELOFFSET = VEL_MAX - VELFACTOR*REDUCE_VEL_ZONE

# raw_dist = ult_sen.distance()
raw_dist = DIS_MAX #khoảng cách cảm biến đọc được
calculated_dist = raw_dist + DISOFFSET #khoảng cách sau khi bù sai số

vel = 0 #biến vận tốc hiện tại
prevel = vel #biến vận tốc trước đó
able2go_b = False
demand2go_b = False

def veloc_calc(dist):
    vel_rt = 0

    # tính giá trị tốc độ dựa trên khoảng cách
    if (dist <= STOP_DIST):
        vel_rt = VEL_STOP
    elif (dist > REDUCE_VEL_ZONE):
        vel_rt = VEL_MAX
    else:
        vel_rt = round(dist*VELFACTOR + VELOFFSET)

    # chặn trên/dưới cho tốc độ
    if (vel_rt > VEL_MAX): 
        vel_rt = VEL_MAX
    if (vel_rt < VEL_MIN_CANMOVE): 
        vel_rt = VEL_STOP
    return vel_rt

def wait_for_driver():
    ev3.speaker.say("DANGER! PLEASE PRESS BRAKE")        
    while (not Button.DOWN in ev3.buttons.pressed()):
        for i in range(3):
            ev3.speaker.beep(frequency=500, duration=100)
        ev3.light.on(Color.RED)
        wait(20)
        ev3.light.off()
        
    ev3.speaker.say("OK")

#
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
    
ev3.speaker.say("GEC GOOOO")

while True:

    # doc khoang cach
    raw_dist = ult_sen.distance()
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
            vel = veloc_calc(calculated_dist)
                        
        # yeu cau nhan phanh khi gap nguy hiem
        if (able2go_b == False):
            # robot.straight(0)
            vel = VEL_STOP
            # wait_for_driver()
            demand2go_b = False
        
        drv_mot.run(vel) #comment for mo phong
    
    # Chờ lệnh từ driver
    if (demand2go_b == False):
        ev3.light.on(Color.RED)
        if ((Button.UP in ev3.buttons.pressed()) and (able2go_b == True)):
            ev3.speaker.say("OK GO")
            demand2go_b = True
        elif ((Button.UP in ev3.buttons.pressed()) and (able2go_b == False)):
            ev3.speaker.say("DANGER CAN NOT GO FORWARD")
            demand2go_b = False