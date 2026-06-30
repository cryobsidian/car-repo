# RC Car Simulator Control Project

This project is for controlling a physical RC car with a Logitech sim racing wheel while using FPV video for the driver experience.

The current planning source is the team Google Doc:

https://docs.google.com/document/d/1lLJxTWNvFdowMAlKwHoxLd9_VtGjU7h_2kNzVmCavCI/edit?usp=sharing

## Goal

Build a prototype where a Logitech G29/G26-style racing wheel and pedals control a generic RC car over Wi-Fi. The car carries an onboard ESP32-class controller, and the driver views the car through a DJI FPV VR headset or similar FPV video system.

## Current System Concept

The old client code uses this control path:

```text
Logitech wheel and pedals
  -> ground station laptop running Python + pygame
  -> HTTP requests over Wi-Fi
  -> ESP32 WebServer endpoints
  -> PWM output
  -> steering servo and TB6612FNG motor driver
  -> RC car movement
```

FPV video is a separate path. It must still be tested with the control system, but the current client concern is no longer long range. The diorama is expected to be near the control booth and ground station, so short-range stability and repeatable demo setup are now the main priorities.

## Documentation

- [Project Requirements](docs/project-requirements.md)
- [System Architecture](docs/system-architecture.md)
- [Hardware Notes](docs/hardware-notes.md)
- [Networking and Latency Risks](docs/networking-and-latency.md)
- [Testing Plan](docs/testing-plan.md)
- [Open Questions](docs/open-questions.md)
- [Old Code Analysis](docs/old-code-analysis.md)

## Key Risks

- Demo stability is the current primary risk. The old system reportedly worked for one sponsor demo, then failed for a later sponsor demo.
- Startup order, Wi-Fi connection state, joystick detection, and device IP assumptions must be made repeatable.
- The old code uses HTTP requests for control and has no onboard failsafe timeout, so the car can keep its last motor state if the ground station stops sending commands.
- Packet loss can disturb control input, especially because steering and throttle are sent as separate requests.
- FPV video bandwidth can create lag, freezing, or frame drops.
- The onboard board choice must match the code target. The old code points most concretely to ESP32 Arduino firmware.
- Range is now a secondary concern because the diorama is expected to be near the control booth and ground station.

## Next Implementation Step

Choose one canonical version of the old code, then build a stable proof of concept:

1. Read steering and pedal values on the host computer.
2. Make startup repeatable: fixed Wi-Fi mode, known IP, joystick detection, and a visible health/status check.
3. Send normalized steering and throttle values as one coherent control update.
4. Add an onboard failsafe that stops the motor when commands stop arriving.
5. Measure stability across repeated setup cycles before optimizing range.
