# System Architecture

## High-Level Design

```text
+----------------------+       USB        +----------------------+
| Logitech wheel/pedal | ----------------> | Ground station       |
| input device         |                   | laptop / host        |
+----------------------+                   +----------+-----------+
                                                      |
                                                      | Wi-Fi control traffic
                                                      v
                                           +----------+-----------+
                                           | ESP32 onboard       |
                                           | controller          |
                                           +----------+-----------+
                                                      |
                                                      | PWM / GPIO
                             +------------------------+------------------------+
                             v                                                 v
                    +--------+---------+                              +--------+-------+
                    | Steering servo   |                              | TB6612FNG /    |
                    |                  |                              | motor driver   |
                    +------------------+                              +----------------+
```

The FPV video system runs alongside this control path:

```text
Camera / FPV transmitter on car -> DJI FPV headset / receiver
```

## Old Code Architecture

The copied client code appears to use this architecture:

```text
Logitech wheel/pedals
  -> Python ground-station script using pygame
  -> HTTP GET requests with requests
  -> ESP32 WebServer endpoints
  -> TB6612FNG motor driver and steering servo
```

Relevant files:

- `RCcar/mainapp.py`: joystick axis print/debug script.
- `RCcar/mainapp_V1.py`: early HTTP control script; contains a variable-name bug where `angle` is calculated but `steer_angle` is used.
- `RCcar/mainapp_V2.py`: clearer axis constants, steering/throttle mapping, and HTTP helper functions.
- `RCcar/mainapp_V3.py`: latest-looking Python control script, using ESP32 IP `192.168.4.2`, deadzone handling, and separate `/throttle` and `/steer` requests.
- `RCcar/motor_test.py` and top-level `motor_test.py`: throttle-only test scripts.
- `RCcar/sterling.ino`: ESP32 steering-only web server.
- `RCcar/motor.ino`: combined ESP32 motor and steering web server targeting a TB6612FNG motor driver and a servo.

## Input Tier

The Logitech wheel does not directly control the car over Wi-Fi. It needs a host device, usually a laptop, to read input over USB.

Expected host responsibilities:

- Detect the wheel and pedals.
- Poll steering and pedal values continuously.
- Normalize values into a small control payload.
- Verify axis mapping before enabling motor output.
- Send the newest payload to the car at a fixed update rate.

The old code uses `pygame` for input polling.

## Transmission Tier

The existing code uses HTTP GET requests. That is acceptable for early testing, but it creates avoidable demo risk because steering and throttle are sent as separate transactions and each request depends on the ESP32 web server responding quickly.

Recommended target protocol for a stable rebuild: one repeated control update message containing steering, throttle, brake/reverse, timestamp or sequence number, and optional mode flags.

UDP is a good candidate for this control update.

## Onboard Control Tier

The onboard ESP32 listens for control commands, extracts values, and maps them to hardware outputs.

Expected onboard responsibilities:

- Connect to the control Wi-Fi network or run a dedicated access point.
- Expose a health/status endpoint before control starts.
- Parse steering, throttle, and brake/reverse values.
- Clamp values to safe limits.
- Convert normalized values to PWM commands.
- Stop or neutralize output if commands stop arriving.
- Log command age and failsafe state.

## Actuation Tier

The old combined firmware uses:

- Steering servo on pin 13.
- TB6612FNG motor driver pins: `PWMA=25`, `AIN1=26`, `AIN2=27`, `STBY=14`.
- 8-bit PWM for motor speed from 0 to 255.
- Steering angle clamp from 60 to 120 degrees.

The onboard controller must not drive high motor current directly from GPIO pins.

## Board Choice

The old code points most concretely to ESP32 Arduino firmware because `motor.ino` and `sterling.ino` include `WiFi.h`, `WebServer.h`, and `ESP32Servo.h`.

Planning notes mention Raspberry Pi and Raspberry Pi Pico W, but switching boards would change GPIO, PWM, Wi-Fi, deployment, and dependency assumptions. The fastest stabilization path is likely to keep ESP32 and improve firmware/ground-station reliability.
