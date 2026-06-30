# Open Questions

## Hardware

- Is the steering wheel a Logitech G29, G26, or another model?
- Which onboard board is the final target: ESP32, Raspberry Pi, or Raspberry Pi Pico W?
- What exact RC car platform is being modified?
- Does the car use a hobby ESC, a brushed motor driver, or another drivetrain controller?
- What steering servo is installed?
- What batteries and voltage regulators are available?

## Networking

- Will the car connect to an existing Wi-Fi router, or will the ground station create a hotspot?
- What is the target maximum driving distance?
- What environments must work: open line-of-sight only, indoor rooms, through walls, or mixed?
- Does FPV video use its own radio link or share Wi-Fi with control traffic?
- What packet update rate should the control loop use?

## Software

- Will the ground station code be Python?
- Which input library should be used for the Logitech wheel: `pygame`, `inputs`, or another option?
- Will the onboard code be MicroPython or full Python/Linux?
- What packet format should be standardized for the first prototype?
- What failsafe timeout should be used?

## Testing

- What distance caused failure in earlier tests?
- At the failure distance, was Wi-Fi disconnected or still connected with high packet loss?
- Was the bad experience caused by control lag, FPV lag, or both?
- What safety area is available for range testing?
