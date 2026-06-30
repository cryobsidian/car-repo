# Hardware Notes

## Planned Hardware

- Logitech sim racing wheel and pedals, likely G29 or similar.
- Generic RC car platform.
- Onboard ESP32, Raspberry Pi, or Raspberry Pi Pico W.
- Steering servo.
- ESC or motor driver.
- Battery for car drivetrain.
- Separate regulated power for onboard controller if required.
- FPV camera and DJI FPV VR headset or compatible video system.

## Logitech Wheel

The wheel connects to a host computer over USB. The host computer reads steering and pedal values and sends control commands to the car.

The planning doc says "G26" in one place and "G29" elsewhere. Confirm the exact model before writing final input code.

## Onboard Controller

The onboard controller acts as the car brain. It should not directly power the motor from GPIO.

Possible choices:

- ESP32: good Wi-Fi support, common MicroPython target, suitable for PWM control.
- Raspberry Pi Pico W: MicroPython-friendly and supports Wi-Fi, but has different networking and PWM constraints from ESP32.
- Raspberry Pi: more powerful and can run full Python/Linux, but has more boot and power complexity.

## Steering

The steering servo should be controlled with PWM. Calibrate the minimum, center, and maximum pulse widths before allowing full-speed tests.

## Throttle and Braking

The throttle path depends on the car:

- If the car uses a hobby ESC, send RC PWM-style throttle signals.
- If the car uses a simple brushed DC motor, use a motor driver board that can handle the required current.

GPIO pins must only send control signals. They must not carry motor current.

## FPV Video

The FPV path is critical to the driving experience. Video lag, freezing, or frame drops can make the car hard to drive even if control packets are working.

Confirm whether the DJI FPV system uses an independent radio/video link or shares networking resources with the control system.
