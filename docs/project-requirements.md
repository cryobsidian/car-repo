# Project Requirements

Source: team planning Google Doc, "Puteri's work", last read on 2026-06-30.

## Objective

Create an RC car control system where a Logitech sim racing wheel controls a physical car, while the driver uses FPV video for the driving view.

## Functional Requirements

- The user can steer the car using the Logitech wheel.
- The user can accelerate and brake using the Logitech pedals.
- A ground station reads wheel and pedal input over USB.
- The ground station sends control input to the car over Wi-Fi.
- The onboard controller receives control packets continuously.
- The onboard controller converts steering and throttle values to PWM.
- The steering PWM drives a steering servo.
- The throttle/brake PWM drives an ESC or motor driver.
- The system supports FPV visuals through a DJI FPV VR headset or equivalent FPV system.

## Performance Requirements

- Control should feel responsive enough for live driving.
- Newer control input should take priority over older delayed input.
- The system should tolerate occasional lost control packets without freezing on stale commands.
- The system should be tested at increasing distances until control or FPV quality becomes unacceptable.

## Range and Environment Requirements

- Test close-range driving first.
- Test longer-distance driving after the close-range path is stable.
- Test line-of-sight operation separately from operation with walls or obstacles.
- Record the distance where Wi-Fi signal, packet loss, latency, or FPV quality becomes unacceptable.

## User Experience Requirements

- The car should not continue unsafe motion if control packets stop arriving.
- Steering and throttle response should be predictable.
- FPV video should not lag or freeze enough to make driving unpleasant.
- The driver should know when the car is near the limit of usable range.

## Current Concerns From Planning

- The car may stop responding after a certain distance.
- Walls or obstacles may block the wireless signal.
- A weak Wi-Fi connection can increase packet loss.
- Packet loss can disturb control and make the car uncontrollable.
- FPV video at resolutions such as 1080p 30 FPS can require high bandwidth.
- Video bandwidth problems can cause lag, frame drops, or freezing.

## Assumptions To Confirm

- Exact Logitech wheel model: the planning doc mentions both G26 and G29.
- Exact onboard board: the planning doc mentions ESP32, Raspberry Pi, and Raspberry Pi Pico W.
- Exact RC car motor system: brushed motor driver or ESC.
- Whether DJI FPV video uses its own radio link or shares Wi-Fi/network resources with control.
