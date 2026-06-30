# Networking and Latency Risks

## Main Risk

The team planning doc identifies distance and obstacles as primary concerns. As the car moves farther away, the Wi-Fi connection can weaken, packet loss can increase, and control can become delayed or unstable.

## Failure Chain

```text
More distance or blocked signal
  -> weaker Wi-Fi connection
  -> more packet loss
  -> delayed or missing control packets
  -> disturbed steering/throttle response
  -> car becomes difficult or impossible to control
```

## Video Bandwidth

FPV video can require significant bandwidth. A stream such as 1080p at 30 FPS can create lag, freezing, or frame drops if the link cannot keep up.

Even if the control link is stable, the user experience can still fail if FPV video is delayed or unreliable.

## Recommended Control Protocol

Use UDP for the first prototype.

UDP is appropriate because:

- Low latency matters more than perfect delivery.
- The newest input replaces older input.
- Retransmitting old steering/throttle commands can make the car feel delayed.

## Required Failsafe Behavior

The onboard controller should track the time since the last valid packet.

If no valid packet arrives within the timeout:

- Set throttle to neutral or zero.
- Center steering or hold the last steering position, depending on test safety.
- Ignore stale packets.
- Optionally blink an LED or send debug status.

Suggested first timeout: 250 ms.

## Measurements To Capture

During tests, record:

- Distance from ground station.
- Line-of-sight or blocked by walls/obstacles.
- Packet send rate.
- Packet loss rate if available.
- Control latency.
- FPV latency or visible lag.
- Whether the car remains controllable.
- Whether Wi-Fi remains connected after the failure distance.

## Diagnostic Question

When the system fails around a distance limit, determine whether the onboard device is still connected to Wi-Fi.

This separates two different problems:

- Wi-Fi disconnected entirely.
- Wi-Fi still connected, but packet loss or latency is too high.
