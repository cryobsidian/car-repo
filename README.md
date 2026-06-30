# RC Car Simulator Control Project

This project is for controlling a physical RC car with a Logitech sim racing wheel while using FPV video for the driver experience.

The current planning source is the team Google Doc:

https://docs.google.com/document/d/1lLJxTWNvFdowMAlKwHoxLd9_VtGjU7h_2kNzVmCavCI/edit?usp=sharing

## Goal

Build a prototype where a Logitech G29/G26-style racing wheel and pedals control a generic RC car over Wi-Fi. The car carries an onboard microcontroller or small computer, and the driver views the car through a DJI FPV VR headset or similar FPV video system.

## Current System Concept

The planned control path is:

```text
Logitech wheel and pedals
  -> ground station laptop or host computer
  -> Wi-Fi control packets
  -> onboard ESP32 / Raspberry Pi / Raspberry Pi Pico W
  -> PWM output
  -> steering servo and ESC / motor driver
  -> RC car movement
```

FPV video is a separate high-bandwidth path. It must be tested alongside control traffic because video lag, dropped frames, and weak wireless signal directly affect the driving experience.

## Documentation

- [Project Requirements](docs/project-requirements.md)
- [System Architecture](docs/system-architecture.md)
- [Hardware Notes](docs/hardware-notes.md)
- [Networking and Latency Risks](docs/networking-and-latency.md)
- [Testing Plan](docs/testing-plan.md)
- [Open Questions](docs/open-questions.md)

## Key Risks

- Wireless range can degrade as the car moves farther from the controller.
- Walls and obstacles can block or weaken the signal.
- Packet loss can disturb control input.
- FPV video bandwidth can create lag, freezing, or frame drops.
- The onboard board choice must match the code target. The planning doc mentions ESP32, Raspberry Pi, Raspberry Pi Pico W, and Raspberry Pi in different places.

## Next Implementation Step

Choose the exact onboard board and ground station setup, then build the smallest proof of concept:

1. Read steering and pedal values on the host computer.
2. Send normalized steering and throttle values over UDP.
3. Receive the values on the onboard board.
4. Output PWM to a servo and ESC or motor driver.
5. Measure control latency and maximum usable range.
