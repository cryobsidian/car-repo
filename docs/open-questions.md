# Open Questions

## Hardware

- Is the steering wheel a Logitech G29, G26, or another model?
- Is ESP32 the final onboard target, matching the old `.ino` code?
- What exact RC car platform is being modified?
- Is the motor path definitely the TB6612FNG driver used in `RCcar/motor.ino`?
- What steering servo is installed?
- What batteries and voltage regulators are available?

## Networking

- Which IP should the ground-station scripts use: `192.168.50.111`, `192.168.4.2`, or a reserved/static IP?
- Should the ESP32 run as a Wi-Fi station on the booth network or as its own access point?
- What is the exact booth-to-diorama distance?
- Does FPV video use its own radio link or share Wi-Fi with control traffic?
- What packet update rate should the control loop use?

## Software

- Which Python file was used in the successful sponsor demo?
- Which ESP32 sketch was flashed during the successful sponsor demo?
- Should the onboard code stay on ESP32 Arduino, based on the old `.ino` files?
- Should the control protocol remain HTTP for compatibility or move to UDP for stability and lower latency?
- What control format should be standardized for the next prototype?
- What failsafe timeout should be used?
- Should steering and throttle be sent together in one update instead of separate requests?
- What logs should be visible to the demo operator?

## Testing

- During the failed sponsor demo, did the ESP32 connect to Wi-Fi?
- During the failed sponsor demo, could the laptop open the ESP32 status page?
- Was the Logitech wheel detected by the laptop?
- Was the issue control, motor power, steering servo, FPV video, or startup sequence?
- Was the same laptop used for both sponsor demos?
- Was the same Wi-Fi network used for both sponsor demos?
- What safety area is available for range testing?
