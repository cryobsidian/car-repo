import time
import requests
import pygame

ESP32_IP = "192.168.50.111"

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise RuntimeError("No joystick found")

js = pygame.joystick.Joystick(0)
js.init()

print("Joystick:", js.get_name())

def map_range(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

last_steer = None
last_throttle = None

while True:
    pygame.event.pump()

    # ?? axis ????????
    wheel = js.get_axis(0)      # ???
    throttle = js.get_axis(1)   # ??
    brake = js.get_axis(2)      # ??

    # ??: -1.0 ~ 1.0 -> 45 ~ 135
    angle = map_range(wheel, -1.0, 1.0, 120, 60)

    # ???:throttle/brake ?? -255 ~ 255
    # ?????????
    t = map_range(throttle, -1.0, 1.0, 255, 0)
    b = map_range(brake, -1.0, 1.0, 255, 0)
    drive = t - b

    if last_steer is None or abs(steer_angle - last_steer) >= 2:
        try:
            requests.get(f"http://{ESP32_IP}/steer", params={"value": steer_angle}, timeout=0.1)
            last_steer = steer_angle
        except:
            pass

    if last_throttle is None or abs(drive - last_throttle) >= 8:
        try:
            requests.get(f"http://{ESP32_IP}/throttle", params={"value": drive}, timeout=0.1)
            last_throttle = drive
        except:
            pass

    time.sleep(0.02)
