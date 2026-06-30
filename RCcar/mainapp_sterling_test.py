import pygame
import requests
import time

ESP32_IP = "192.168.4.2"   # ????

pygame.init()
pygame.joystick.init()

js = pygame.joystick.Joystick(0)
js.init()


# 轴编号（你之后可以改）
THROTTLE_AXIS = 2
CLUTCH_AXIS = 1
STERLING = 0

def map_range(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)



def map_range(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def clamp(v, min_v, max_v):
    return max(min_v, min(v, max_v))


last_angle = None #FOR STERLING
last_val = None #FOR THROTTLE




while True:
    pygame.event.pump()

    wheel = js.get_axis(STERLING)   # ???
    throttle_raw = js.get_axis(THROTTLE_AXIS)
    clutch_raw = js.get_axis(CLUTCH_AXIS)



    # 转换成 0~255
    throttle_val = map_range(throttle_raw, 1.0, -1.0, 0, 255)
    clutch_val = map_range(clutch_raw, 1.0, -1.0, 0, 255)

    throttle_val = clamp(throttle_val, 0, 255)
    clutch_val = clamp(clutch_val, 0, 255)

    # ===== 核心逻辑 =====
    drive = throttle_val - clutch_val   # 前进 - 后退

    drive = clamp(drive, -255, 255)

    # 防抖
    if last_val is None or abs(drive - last_val) >= 10:
        try:
            requests.get(
                f"http://{ESP32_IP}/throttle",
                params={"value": drive},
                timeout=0.1
            )
            print("Throttle:", throttle_val, "Clutch:", clutch_val, "Drive:", drive)
            last_val = drive
        except:
            pass

    time.sleep(0.02)








    # -1 ~ 1 ? 60 ~ 120
    angle = map_range(wheel, -1.0, 1.0, 120, 60)

    # ??(???)
    if last_angle is None or abs(angle - last_angle) >= 2:
        try:
            requests.get(f"http://{ESP32_IP}/steer", params={"value": angle}, timeout=0.05)
            print("Steer:", angle)
            last_angle = angle
        except:
            pass

    time.sleep(0.02)
l
