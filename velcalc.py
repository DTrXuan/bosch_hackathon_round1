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