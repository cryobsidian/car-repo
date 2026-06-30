# Old Code Analysis

Source files reviewed on 2026-06-30:

- `RCcar/mainapp.py`
- `RCcar/mainapp_V1.py`
- `RCcar/mainapp_V2.py`
- `RCcar/mainapp_V3.py`
- `RCcar/mainapp_sterling_test.py`
- `RCcar/motor_test.py`
- `motor_test.py`
- `RCcar/motor.ino`
- `RCcar/sterling.ino`

## Summary

The old code is an ESP32-based HTTP control prototype. A Python ground-station script reads a Logitech wheel with `pygame`, maps wheel and pedal axes to steering and drive values, and sends HTTP GET requests to an ESP32. The ESP32 exposes web endpoints that control a steering servo and a TB6612FNG motor driver.

The architecture is simple and useful for proving the concept, but it is fragile for sponsor demos. The most important missing pieces are startup verification, consistent network configuration, visible failure logs, and onboard failsafe behavior.

## Ground Station Python

The Python scripts use:

- `pygame` for joystick input.
- `requests` for HTTP calls to the ESP32.
- Hard-coded ESP32 IP addresses.
- Axis mapping constants for steering, throttle, and clutch/reverse.
- Thresholds to avoid sending tiny changes.

Observed variants:

- `mainapp.py` only prints joystick axes.
- `mainapp_V1.py` is an early combined script but uses `steer_angle` without defining it. It calculates `angle`, so this version would crash when steering is sent.
- `mainapp_V2.py` adds constants, clamping, helper functions, and better logging.
- `mainapp_V3.py` appears to be the latest control script. It uses IP `192.168.4.2`, adds a drive deadzone, scales steering sensitivity, and only updates last sent state after successful requests.
- `motor_test.py` scripts test throttle only.
- `mainapp_sterling_test.py` tests steering and throttle, but has duplicated helper code and a stray `l` at the end, which would raise an error if reached.

## ESP32 Firmware

The ESP32 sketches use:

- `WiFi.h`
- `WebServer.h`
- `ESP32Servo.h`
- Servo output on pin 13.
- TB6612FNG motor driver pins in `motor.ino`: `PWMA=25`, `AIN1=26`, `AIN2=27`, `STBY=14`.

Endpoints in the combined sketch:

- `/steer?value=<angle>`
- `/throttle?value=<drive>`
- `/stop`
- `/status`

The combined `motor.ino` has two `handleRoot()` functions with the same signature. That file would not compile as-is until the duplicate root handler is resolved.

## Stability Risks

- No onboard command timeout. If the host script stops or Wi-Fi drops, the ESP32 does not automatically stop the motor.
- Hard-coded IPs differ between Python versions: `192.168.50.111` and `192.168.4.2`.
- ESP32 Wi-Fi credentials are hard-coded to `LWK_Network`.
- The host sends steering and throttle separately, so the ESP32 can receive one without the other.
- Some scripts swallow exceptions silently, which hides the real failure during demos.
- Some scripts assume joystick index 0 exists without checking.
- Axis mapping is not automatically validated, so a different laptop, OS, driver, or wheel mode can change behavior.
- HTTP request timeouts are very short. That can keep the loop responsive, but it can also turn brief network jitter into missed commands.
- The `/status` endpoint reports throttle only, not steering, Wi-Fi state, last command age, or failsafe state.

## Recommended Stabilization Work

1. Pick one canonical ground-station script and archive/remove the broken variants from the run path.
2. Pick one canonical ESP32 sketch and make sure it compiles cleanly.
3. Add an ESP32 command watchdog. If no valid command arrives within about 250 ms, stop the motor.
4. Add a richer `/status` response with throttle, steering angle, Wi-Fi IP, uptime, last command age, and failsafe state.
5. Add a ground-station startup check that verifies joystick detection, axis mapping, ESP32 reachability, `/status`, `/stop`, and steering center.
6. Use a reserved/static IP or ESP32 access-point mode so the host script does not depend on changing router DHCP behavior.
7. Log every failed request during demos instead of silently ignoring errors.
8. Send steering and throttle together as one control update for the next protocol revision.
9. Run repeated cold-start demo simulations before sponsor use.

## Range Priority

Range was previously documented as a major concern, but the current setup places the diorama near the control booth and ground station. That makes repeatability, startup reliability, and failsafe behavior more important than long-distance wireless optimization.
