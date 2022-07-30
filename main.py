#!/usr/bin/env pybricks-micropython
# This program requires LEGO EV3 MicroPython v2.0 or higher.

from math import floor
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.ev3devices import UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait
from uerrno import ENODEV

""" INITIALIZED  """
# Create your objects here.
ev3 = EV3Brick()

# Khoi tao ngoai vi
isHWConnect = False
isRecheckConfirm = False
while isHWConnect == False:
    try:
        drv_mot = Motor(Port.A)
        Steer_mot = Motor(Port.B)
        ult_sen = UltrasonicSensor(Port.S4)
        isHWConnect = True
    except OSError as ex:
        isHWConnect = False
        ev3.screen.clear()
        ev3.screen.print(0, 0, "CONNECTION FAIL")
        while True:
            ev3.speaker.beep(frequency=800, duration=100)
            if (Button.CENTER in ev3.buttons.pressed()):
                wait(100)
                ev3.screen.clear()
                ev3.screen.print("Press CENTER to recheck")
                isRecheckConfirm = True
                break
    while isRecheckConfirm == True:
        if (Button.CENTER in ev3.buttons.pressed()):
            ev3.screen.clear()
            isRecheckConfirm = False
            break

# Khoi tao bien

VEL_MAX = 100 #duty 
VEL_MIN_CANMOVE = 15 #duty
VEL_STOP = 0 #stop 

DISOFFSET = 0 #mm bu so sai lech khoang cach thuc te voi ket qua do duoc
STOP_DIST = 50 #mm khoang cach phai dung lai
REDUCE_VEL_ZONE = 150 #mm vung giam toc: khoang cach tu xe den vat can. trong vung nay xe bat dau giam toc do
SMOOTH_CALIB = 90
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
calculated_dist_old = calculated_dist
vel = 0 #biến vận tốc hiện tại
prevel = vel #biến vận tốc trước đó
able2go_b = False
demand2go_b = False
safe_check_b = False


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
    if (vel_rt <= VEL_MIN_CANMOVE): 
        vel_rt = VEL_STOP
    return vel_rt

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