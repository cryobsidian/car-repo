# Hardware Notes

## Planned Hardware

- Logitech sim racing wheel and pedals, likely G29 or similar.
- Generic RC car platform.
- ESP32 onboard controller, based on the old `.ino` code.
- Steering servo.
- TB6612FNG motor driver or equivalent motor controller.
- Battery for car drivetrain.
- Separate regulated power for onboard controller if required.
- FPV camera and DJI FPV VR headset or compatible video system.

## Logitech Wheel

The wheel connects to a host computer over USB. The host computer reads steering and pedal values and sends control commands to the car.

The planning doc says "G26" in one place and "G29" elsewhere. Confirm the exact model before writing final input code.

The old Python code assumes `pygame.joystick.Joystick(0)` and uses these likely axis mappings in the latest script:

- Steering: axis 0
- Throttle: axis 2
- Clutch/reverse: axis 1

This must be validated on the actual demo laptop because joystick axis order can vary by OS, driver, and wheel mode.

## Onboard Controller

The old firmware points to ESP32 Arduino code, using:

- `WiFi.h`
- `WebServer.h`
- `ESP32Servo.h`

This is currently the fastest path to stabilize because it matches the old code and hardware assumptions.

## Steering

The old code drives a servo on pin 13 and clamps steering angle between 60 and 120 degrees, with 90 degrees as center.

Calibrate the true physical limits before allowing full-speed tests.

## Throttle and Braking

The old combined firmware uses TB6612FNG-style motor control:

- `PWMA=25`
- `AIN1=26`
- `AIN2=27`
- `STBY=14`

The Python code maps throttle minus clutch/reverse into a `drive` value from -255 to 255. Positive values drive forward, negative values drive reverse, and zero stops.

GPIO pins must only send control signals. They must not carry motor current.

## FPV Video

The FPV path is critical to the driving experience. Video lag, freezing, or frame drops can make the car hard to drive even if control commands are working.

Confirm whether the DJI FPV system uses an independent radio/video link or shares networking resources with the control system.

## Demo Stability Hardware Checks

Before a sponsor demo, confirm:

- ESP32 boots and reports its IP address.
- Ground-station laptop is on the expected network.
- Motor driver standby pin is enabled only after the operator is ready.
- Motor power and ESP32 logic power are stable.
- Servo centers before drive output is enabled.
- The car stops when the Python process is closed or network commands stop.
