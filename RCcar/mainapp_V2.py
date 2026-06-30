import pygame
import requests
import time

ESP32_IP = "192.168.50.111"

# ===== Steering range =====
STEER_MIN = 60
STEER_CENTER = 90
STEER_MAX = 120

# ===== Axis index =====
STEER_AXIS = 0
THROTTLE_AXIS = 2
CLUTCH_AXIS = 1

# ===== Send thresholds =====
SEND_STEER_THRESHOLD = 2
SEND_DRIVE_THRESHOLD = 8

LOOP_DELAY = 0.02

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise RuntimeError("No joystick found")

js = pygame.joystick.Joystick(0)
js.init()

print("Joystick name:", js.get_name())
print("Axes:", js.get_numaxes())

def map_range(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def clamp(v, min_v, max_v):
    return max(min_v, min(v, max_v))

def send_steer(angle):
    try:
        r = requests.get(
            f"http://{ESP32_IP}/steer",
            params={"value": angle},
            timeout=0.1
        )
        return r.status_code
    except Exception as e:
        print("Steer request error:", e)
        return None

def send_throttle(value):
    try:
        r = requests.get(
            f"http://{ESP32_IP}/throttle",
            params={"value": value},
            timeout=0.1
        )
        return r.status_code
    except Exception as e:
        print("Throttle request error:", e)
        return None

last_angle = None
last_drive = None

while True:
    pygame.event.pump()

    # ===== Steering =====
    wheel_raw = js.get_axis(STEER_AXIS)

    # deadzone,??????
    if abs(wheel_raw) < 0.03:
        wheel_raw = 0.0

    # ??????,?? STEER_MAX / STEER_MIN ??
    steer_angle = map_range(wheel_raw, -1.0, 1.0, STEER_MAX, STEER_MIN)
    steer_angle = clamp(steer_angle, STEER_MIN, STEER_MAX)

    # ===== Throttle / Clutch =====
    throttle_raw = js.get_axis(THROTTLE_AXIS)
    clutch_raw = js.get_axis(CLUTCH_AXIS)

    # ????:
    # ???? 1.0
    # ???? -1.0
    throttle_val = map_range(throttle_raw, 1.0, -1.0, 0, 255)
    clutch_val = map_range(clutch_raw, 1.0, -1.0, 0, 255)

    throttle_val = clamp(throttle_val, 0, 255)
    clutch_val = clamp(clutch_val, 0, 255)

    # ?? - ??
    drive = throttle_val - clutch_val
    drive = clamp(drive, -255, 255)

    # ===== Send steer =====
    if last_angle is None or abs(steer_angle - last_angle) >= SEND_STEER_THRESHOLD:
        status = send_steer(steer_angle)
        print(f"STEER raw={wheel_raw:.3f} angle={steer_angle} status={status}")
        last_angle = steer_angle

    # ===== Send throttle =====
    if last_drive is None or abs(drive - last_drive) >= SEND_DRIVE_THRESHOLD:
        status = send_throttle(drive)
        print(
            f"THROTTLE raw={throttle_raw:.3f} mapped={throttle_val} | "
            f"CLUTCH raw={clutch_raw:.3f} mapped={clutch_val} | "
            f"drive={drive} status={status}"
        )
        last_drive = drive

    time.sleep(LOOP_DELAY)
