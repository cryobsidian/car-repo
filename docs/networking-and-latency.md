# Networking and Latency Risks

## Main Risk

The current client concern is stability, not long range. The system reportedly worked once for a sponsor and failed later for a different sponsor. Because the diorama will be near the control booth and ground station, the first networking goal is repeatable short-range setup.

The old code has several stability-sensitive assumptions:

- The ESP32 IP address is hard-coded in Python.
- Different Python versions use different ESP32 IPs: `192.168.50.111` and `192.168.4.2`.
- The ESP32 sketch connects to a fixed Wi-Fi SSID and password.
- The host sends steering and throttle as separate HTTP GET requests.
- Some Python scripts silently ignore request failures.
- The ESP32 does not stop the motor if commands stop arriving.

## Failure Chain

```text
Unstable demo setup
  -> wrong Wi-Fi network, changed IP, missing joystick, or stale process
  -> ground station cannot reliably reach ESP32
  -> steering/throttle commands are delayed or dropped
  -> ESP32 keeps last known output or receives partial updates
  -> sponsor demo appears to fail randomly
```

## Video Bandwidth

FPV video can require significant bandwidth. A stream such as 1080p at 30 FPS can create lag, freezing, or frame drops if the link cannot keep up.

Even if the control link is stable, the user experience can still fail if FPV video is delayed or unreliable.

## Existing HTTP Control Protocol

The old code uses HTTP GET endpoints:

- `/steer?value=<angle>`
- `/throttle?value=<drive>`
- `/stop`
- `/status`

This is useful for manual testing, but fragile for demos. Steering and throttle can arrive separately, short request timeouts can drop commands, and silent exception handling can hide the real failure.

## Recommended Control Protocol

For the next stable prototype, prefer a single repeated control packet rather than separate steering and throttle requests. UDP is a good fit if the onboard code includes a timeout failsafe.

UDP is appropriate because:

- Low latency matters more than perfect delivery.
- The newest input replaces older input.
- Retransmitting old steering/throttle commands can make the car feel delayed.

## Required Failsafe Behavior

The onboard controller should track the time since the last valid command.

If no valid command arrives within the timeout:

- Set throttle to neutral or zero.
- Center steering or hold the last steering position, depending on test safety.
- Ignore stale packets.
- Report failsafe state through `/status` or serial logs.

Suggested first timeout: 250 ms.

This is the highest-priority firmware change. Without it, the motor driver can keep the last commanded throttle if the Python process freezes, the joystick disconnects, Wi-Fi drops, or the sponsor-demo laptop changes networks.

## Measurements To Capture

During tests, record:

- Startup attempt number.
- Wi-Fi network name and ESP32 IP address.
- Whether the ground station can reach `/status`.
- Whether the joystick is detected and which axis mapping is active.
- Packet send rate.
- Request failure rate or packet loss rate.
- Control latency.
- FPV latency or visible lag.
- Whether the car remains controllable.
- Whether the ESP32 failsafe triggers correctly when the host stops.

## Diagnostic Question

When the system fails during demo setup, determine the exact failing layer.

This separates different problems:

- Joystick not detected or wrong axis mapping.
- Ground station on wrong Wi-Fi network.
- ESP32 connected but using a different IP.
- HTTP requests timing out or being dropped.
- ESP32 receiving commands but motor/servo output not responding.
- FPV issue unrelated to control.
