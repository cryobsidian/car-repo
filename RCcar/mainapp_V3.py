import pygame
import requests
import time

ESP32_IP = "192.168.4.2"

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise RuntimeError("No joystick found")

js = pygame.joystick.Joystick(0)
js.init()

# Axis index
THROTTLE_AXIS = 2
CLUTCH_AXIS = 1
STEERING_AXIS = 0

# Steering range
STEER_MIN = 60
STEER_CENTER = 90
STEER_MAX = 120

# Thresholds
STEER_SEND_THRESHOLD = 2
DRIVE_SEND_THRESHOLD = 8
DRIVE_DEADZONE = 12   # ???????? 0

LOOP_DELAY = 0.02


def map_range(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def clamp(v, min_v, max_v):
    return max(min_v, min(v, max_v))


def send_throttle(value):
    try:
        requests.get(
            f"http://{ESP32_IP}/throttle",
            params={"value": value},
            timeout=0.08
        )
        return True
    except requests.RequestException:
        return False


def send_steer(angle):
    try:
        requests.get(
            f"http://{ESP32_IP}/steer",
            params={"value": angle},
            timeout=0.05
        )
        return True
    except requests.RequestException:
        return False


last_angle = None
last_drive = None

print("Joystick name:", js.get_name())
print("Start control loop...")

while True:
    pygame.event.pump()

    # Read joystick
    wheel = js.get_axis(STEERING_AXIS)
    throttle_raw = js.get_axis(THROTTLE_AXIS)
    clutch_raw = js.get_axis(CLUTCH_AXIS)

    # Convert pedals to 0~255
    throttle_val = map_range(throttle_raw, 1.0, -1.0, 0, 255)
    clutch_val = map_range(clutch_raw, 1.0, -1.0, 0, 255)

    throttle_val = clamp(throttle_val, 0, 255)
    clutch_val = clamp(clutch_val, 0, 255)

    # Drive logic: throttle forward, clutch reverse
    drive = throttle_val - clutch_val
    drive = clamp(drive, -255, 255)

    # Deadzone to prevent creeping
    if abs(drive) < DRIVE_DEADZONE:
        drive = 0

    # Steering: -1~1 -> 120~60
    wheel = wheel * 1.5
    wheel = max(-1.0,min(1.0, wheel))
    angle = map_range(wheel, -1.0, 1.0, STEER_MAX, STEER_MIN)
    angle = clamp(angle, STEER_MIN, STEER_MAX)

    # Send throttle only when changed enough
    if last_drive is None or abs(drive - last_drive) >= DRIVE_SEND_THRESHOLD:
        if send_throttle(drive):
            print(
                f"ThrottleRaw={throttle_raw:.3f} "
                f"ClutchRaw={clutch_raw:.3f} "
                f"Throttle={throttle_val} "
                f"Clutch={clutch_val} "
                f"Drive={drive}"
            )
            last_drive = drive

    # Send steer only when changed enough
    if last_angle is None or abs(angle - last_angle) >= STEER_SEND_THRESHOLD:
        if send_steer(angle):
            print(f"Wheel={wheel:.3f} Steer={angle}")
            last_angle = angle

    time.sleep(LOOP_DELAY)
