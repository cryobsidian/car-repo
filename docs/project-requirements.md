# Project Requirements

Source: team planning Google Doc, "Puteri's work", last read on 2026-06-30.

Updated with old client code analysis and revised client problem statement on 2026-06-30.

## Objective

Create an RC car control system where a Logitech sim racing wheel controls a physical car, while the driver uses FPV video for the driving view.

The revised priority is stable, repeatable sponsor-demo operation. The client reported that the system worked for one sponsor demo but failed for another. Since the diorama will be near the control booth and ground station, range is currently less important than reliability.

## Functional Requirements

- The user can steer the car using the Logitech wheel.
- The user can accelerate and brake/reverse using Logitech pedals.
- A ground station reads wheel and pedal input over USB.
- The ground station sends control input to the car over Wi-Fi.
- The onboard ESP32 receives control commands continuously.
- The onboard controller converts steering and throttle values to PWM.
- The steering PWM drives a steering servo.
- The throttle/brake output drives a TB6612FNG motor driver or equivalent motor controller.
- The system supports FPV visuals through a DJI FPV VR headset or equivalent FPV system.
- The system exposes status information before and during demos.

## Stability Requirements

- The system should behave consistently across repeated cold starts.
- The operator should be able to verify ESP32 connectivity before running the control loop.
- The operator should be able to verify Logitech wheel detection before enabling motor output.
- The onboard controller must stop the motor if commands stop arriving.
- The system should not depend on a changing DHCP IP address unless discovery is implemented.
- Failed network requests must be visible in logs instead of silently ignored.
- The team should maintain one known-good ground-station script and one known-good ESP32 firmware file.

## Performance Requirements

- Control should feel responsive enough for live driving.
- Newer control input should take priority over older delayed input.
- The system should tolerate occasional lost control packets without freezing on stale commands.
- The system should expose enough status information to tell whether failures come from joystick input, ground-station networking, ESP32 connectivity, or motor/servo output.

## Range and Environment Requirements

- Treat range as secondary for the current build because the diorama will be next to the control booth and ground station.
- Optimize for stable short-range operation first.
- Test from the real booth-to-diorama distance instead of assuming open-field range requirements.
- Record Wi-Fi signal and packet behavior only after the short-range demo flow is repeatable.

## User Experience Requirements

- The car should not continue unsafe motion if control packets stop arriving.
- Steering and throttle response should be predictable.
- FPV video should not lag or freeze enough to make driving unpleasant.
- The operator should have a clear pre-demo checklist and visible readiness indicators.
- The team should be able to reset and recover the system quickly during a sponsor demo.

## Current Concerns

- Stability is the main client concern: it worked during one sponsor demo but failed during another.
- Range is less important now because the diorama will be close to the control booth and ground station.
- Startup and connection assumptions are fragile in the old code.
- Packet loss or missed HTTP requests can disturb control and make the car unpredictable.
- The onboard code needs a failsafe so the motor does not keep running after command loss.
- FPV video at resolutions such as 1080p 30 FPS can require high bandwidth.
- Video bandwidth problems can cause lag, frame drops, or freezing.

## Assumptions To Confirm

- Exact Logitech wheel model: the planning doc mentions both G26 and G29.
- Exact onboard board: the old code points to ESP32 Arduino, while planning notes also mention Raspberry Pi and Pico W.
- Exact RC car motor system: old code targets a TB6612FNG motor driver.
- Whether DJI FPV video uses its own radio link or shares Wi-Fi/network resources with control.
