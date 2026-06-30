# Old Code Analysis

Source files reviewed on 2026-06-30:

- `RCcar/mainapp_V3.py` as the current main ground-station file.
- `RCcar/motor.ino` as the current combined ESP32 motor and steering firmware reference.
- `RCcar/sterling.ino` as a steering-only firmware reference.
- Deprecated references: `RCcar/mainapp.py`, `RCcar/mainapp_V1.py`, `RCcar/mainapp_V2.py`, `RCcar/mainapp_sterling_test.py`, `RCcar/motor_test.py`, and top-level `motor_test.py`.

## Current Canonical File

Use `RCcar/mainapp_V3.py` as the active ground-station script.

`mainapp_V1.py` and `mainapp_V2.py` are deprecated old versions. They are useful only for historical comparison and should not be used for demos or future development.

## Summary

The old code is an ESP32-based HTTP control prototype. A Python ground-station script reads a Logitech wheel with `pygame`, maps wheel and pedal axes to steering and drive values, and sends HTTP GET requests to an ESP32. The ESP32 exposes web endpoints that control a steering servo and a TB6612FNG motor driver.

The architecture is simple and useful for proving the concept, but it is fragile for sponsor demos. The most important missing pieces are startup verification, consistent network configuration, visible failure logs, onboard failsafe behavior, and a more appropriate real-time control protocol.

## Ground Station: `mainapp_V3.py`

`mainapp_V3.py` does the following:

- Uses `pygame` for Logitech wheel/pedal input.
- Assumes the ESP32 is reachable at `192.168.4.2`.
- Assumes joystick index `0` exists.
- Uses axis `0` for steering, axis `2` for throttle, and axis `1` for clutch/reverse.
- Maps throttle and clutch/reverse to `0..255`, then computes `drive = throttle - clutch`.
- Applies a drive deadzone of `12` to prevent creeping.
- Scales steering input by `1.5`, clamps to `-1.0..1.0`, then maps steering to `120..60` degrees.
- Sends `/throttle?value=<drive>` only when drive changes by at least `8`.
- Sends `/steer?value=<angle>` only when steering changes by at least `2` degrees.
- Sleeps for `20 ms` per loop.

Important behavior:

- `requests.get()` is synchronous, so a single thread does wait for each request to finish or time out before moving on.
- However, it does not reuse a persistent `requests.Session`, so each send can create a new HTTP/TCP connection.
- With a `20 ms` loop delay, short HTTP timeouts, and separate throttle/steer endpoints, the laptop can create rapid connection churn against the ESP32.
- The function returns only `True` or `False`, so failures are invisible during operation.
- `last_drive` and `last_angle` update only after successful sends, which is reasonable, but it also means an unreachable ESP32 can cause repeated retry pressure whenever the input remains changed.

## ESP32 Firmware: `motor.ino`

The combined ESP32 sketch uses:

- `WiFi.h`
- `WebServer.h`
- `ESP32Servo.h`
- Servo output on pin `13`.
- TB6612FNG motor driver pins: `PWMA=25`, `AIN1=26`, `AIN2=27`, `STBY=14`.
- HTTP endpoints for `/steer`, `/throttle`, `/stop`, and `/status`.

Known firmware issue:

- `motor.ino` contains two `handleRoot()` functions with the same signature. It must be cleaned up before it can compile reliably as the active combined firmware.

Endpoint behavior:

- `/steer` clamps steering to `60..120`, writes the servo angle, prints to serial, then responds `OK`.
- `/throttle` clamps drive to `-255..255`, controls motor direction/speed, prints to serial, then responds with the current throttle.
- `/stop` stops the motor and prints `STOP`.
- `/status` currently reports only throttle.

## Assessment Of Suggested Issues

Your friend's AI identified two important areas. The direction is right, but the first issue needs precise wording.

### 1. HTTP/TCP Bottleneck In `mainapp_V3.py`

Mostly right.

The script is not literally launching new `requests.get()` calls before previous calls return, because the code is single-threaded and `requests.get()` blocks. The practical issue is still real: every steering or throttle send can create a new short-lived HTTP/TCP connection, and that happens inside a loop designed to run every `20 ms`.

Why this can fail:

- ESP32 `WebServer` is simple and single-threaded.
- HTTP/TCP has connection setup and teardown overhead.
- Steering and throttle are separate HTTP transactions.
- Very short timeouts, `0.05 s` for steering and `0.08 s` for throttle, can mark a request failed during brief Wi-Fi or server stalls.
- Without persistent sessions or a streaming protocol, the system depends on many small HTTP requests succeeding quickly.

Result:

- Rapid command changes can overload or stall the ESP32 web server.
- Missed requests can make steering or throttle appear inconsistent.
- Failures are hidden because `mainapp_V3.py` returns `False` without logging the exception.

### 2. Blocking `Serial.print()` / `Serial.println()` In ESP32 Handlers

Plausible and worth fixing.

`motor.ino` prints inside the HTTP endpoint handlers. Because `WebServer` is handled by `server.handleClient()` in the main loop, anything slow inside a handler delays the next client request.

Why this matters:

- Serial printing can block or slow down if the serial buffer fills or the USB serial connection is slow/unread.
- The ESP32 handles web requests on a simple single-threaded loop.
- A delayed handler means incoming steering/throttle requests wait longer or time out on the Python side.

Result:

- Debug logging inside high-frequency control endpoints can contribute to dropped or delayed commands.
- For demo builds, endpoint handlers should do the minimum work needed to update state and respond.

## Stability Risks

- No onboard command timeout. If the host script stops or Wi-Fi drops, the ESP32 does not automatically stop the motor.
- `mainapp_V3.py` hard-codes the ESP32 IP as `192.168.4.2`.
- The firmware shown in `motor.ino` uses station mode with hard-coded SSID `LWK_Network`, while the `192.168.4.2` address suggests the team may also have tested an ESP32 access-point layout. This mismatch must be resolved.
- The host sends steering and throttle separately, so the ESP32 can receive one without the other.
- Some scripts swallow exceptions silently, which hides the real failure during demos.
- Axis mapping is not automatically validated, so a different laptop, OS, driver, or wheel mode can change behavior.
- HTTP request timeouts are very short. That can keep the loop responsive, but it can also turn brief network jitter into missed commands.
- The `/status` endpoint reports throttle only, not steering, Wi-Fi state, last command age, or failsafe state.

## Recommended Solutions

### 1. Software Protocol Upgrade: Move From HTTP/TCP To UDP

This is the best technical fix for real-time control.

Recommended direction:

- Send one repeated UDP packet containing steering, throttle/reverse, timestamp or sequence number, and optional enable/failsafe flags.
- Send at a steady rate such as `20..50 Hz`.
- On ESP32, accept the newest packet and ignore stale packets.
- Stop the motor if no valid packet arrives within about `250 ms`.

Why this helps:

- UDP avoids TCP connection setup and teardown.
- Lost packets do not block newer commands.
- Steering and throttle arrive together as one coherent control state.
- The control loop becomes closer to how games and RC control streams behave: always apply the newest frame.

### 2. Network Layout Stabilization

Use the laptop or a dedicated router as the stable network host when possible.

Recommended direction:

- Prefer a dedicated booth router or laptop-hosted hotspot for the demo network.
- Reserve a static DHCP lease for the ESP32, or configure a known static IP.
- Make the ground-station script verify `/status` before enabling control.

Important note:

- `motor.ino` currently shows the ESP32 joining `LWK_Network` as a Wi-Fi station, not creating its own hotspot.
- If the team has another firmware version where the ESP32 acts as the hotspot, moving the network host role to the laptop/router is a good idea.
- If the ESP32 already joins a router, the priority is to make that router dedicated and the ESP32 IP deterministic.

### 3. Hardware Antenna Optimization

This can help, but it is lower priority than software stability for the current booth/diorama setup.

Recommended direction:

- Keep the ESP32 antenna clear of batteries, motor wiring, metal chassis parts, and the ground plane.
- Mount the antenna higher on the vehicle body if practical.
- Use an ESP32 module with a proper external 2.4 GHz antenna connector if the current board has poor placement.
- Use an omnidirectional 2.4 GHz antenna rather than a directional antenna unless the car path is fixed.

Why this is lower priority now:

- The revised setup places the diorama close to the control booth and ground station.
- The observed failure pattern sounds more like setup/protocol instability than pure range loss.
- Antenna improvements will not fix missing failsafes, bad IP assumptions, blocking handlers, or hidden request failures.

## Recommended Stabilization Work

1. Treat `RCcar/mainapp_V3.py` as the only active Python ground-station file.
2. Mark `mainapp_V1.py` and `mainapp_V2.py` as deprecated, or move them into an archive folder.
3. Clean `motor.ino` so it compiles as the single active combined firmware.
4. Remove or rate-limit `Serial.print()` calls inside high-frequency HTTP handlers.
5. Add an ESP32 command watchdog. If no valid command arrives within about `250 ms`, stop the motor.
6. Add a richer `/status` response with throttle, steering angle, Wi-Fi IP, uptime, last command age, and failsafe state.
7. Add ground-station startup checks for joystick detection, axis mapping, ESP32 reachability, `/status`, `/stop`, and steering center.
8. Log every failed request during demos instead of silently returning `False`.
9. Use a dedicated router/laptop hotspot with a known ESP32 IP.
10. Move from separate HTTP requests to one UDP control stream when the team is ready to revise the protocol.

## Range Priority

Range was previously documented as a major concern, but the current setup places the diorama near the control booth and ground station. That makes repeatability, startup reliability, protocol stability, and failsafe behavior more important than long-distance wireless optimization.
