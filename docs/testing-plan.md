# Testing Plan

## Test Sequence

Start with controlled bench tests before driving the car.

The current priority is repeatability. A sponsor demo should pass the same setup checklist every time before the car is placed in front of visitors.

## 0. Demo Readiness Checklist

Goal: catch the stability failures that made one sponsor demo work and another fail.

Steps:

1. Power the ESP32 and confirm it connects to the expected Wi-Fi network.
2. Confirm the ESP32 IP address.
3. Open `/status` from the ground-station laptop.
4. Connect the Logitech wheel and confirm `pygame` detects it.
5. Confirm the expected axis mapping for steering, throttle, and reverse/brake.
6. Send `/stop` and verify the motor is stopped before enabling control.
7. Start the ground-station script and confirm steering and throttle logs update.
8. Stop the ground-station script and verify the onboard failsafe stops the motor.

Pass criteria:

- The checklist passes three times in a row from a cold start.
- The team can recover from a failed checklist step without guessing.
- The motor never runs before the operator intentionally enables control.

## 1. Input Read Test

Goal: confirm the ground station can read the wheel and pedals.

Steps:

1. Connect the Logitech wheel and pedals over USB.
2. Run a simple input polling script.
3. Turn the wheel left and right.
4. Press accelerator and brake/reverse pedals.
5. Confirm values update smoothly.

Pass criteria:

- Steering value reaches left, center, and right.
- Pedal values reach released and fully pressed states.
- No input axis is inverted unless intentionally mapped that way.

## 2. Command Send/Receive Test

Goal: confirm the ground station can send values to the ESP32.

Steps:

1. Put both devices on the same Wi-Fi network or connect the laptop to the ESP32 access point.
2. Confirm `/status` responds before running the control loop.
3. Send `/steer?value=90` and confirm the servo centers.
4. Send `/throttle?value=0` and confirm the motor is stopped.
5. Send small steering and throttle changes while watching ESP32 serial logs.

Pass criteria:

- ESP32 receives commands continuously.
- Values match user input.
- Failed HTTP requests or packet drops are visible in logs.
- Close-range updates continue without noticeable pauses.

## 3. PWM Output Test

Goal: confirm the onboard board can drive servo and motor signals safely.

Steps:

1. Test steering servo with wheels off the ground.
2. Calibrate center, minimum, and maximum steering positions.
3. Test motor driver with drive wheels lifted.
4. Verify neutral output before enabling throttle.
5. Stop the ground-station script and confirm failsafe behavior.

Pass criteria:

- Servo responds predictably.
- Throttle does not activate unexpectedly.
- Failsafe returns throttle to zero or neutral.

## 4. Close-Range Drive Test

Goal: confirm the full control loop works at the intended booth-to-diorama distance.

Steps:

1. Drive at low speed in an open area.
2. Test steering, acceleration, braking/reverse, and failsafe.
3. Record latency and any request failures.

Pass criteria:

- Car is controllable.
- No runaway behavior occurs.
- FPV video is usable if included in the test.

## 5. Range Test

Goal: identify margin beyond the expected booth-to-diorama distance.

This is lower priority than stability because the diorama will be close to the control booth and ground station.

Steps:

1. Start at the real expected demo distance.
2. Increase distance only after short-range stability is repeatable.
3. Test line-of-sight first.
4. Repeat with obstacles only if it matches the real setup.
5. Record where control or FPV becomes unacceptable.

Pass criteria:

- Team records the maximum comfortable control distance.
- Team records whether failure is due to Wi-Fi disconnect, request failures, latency, motor output, or FPV quality.

## 6. FPV Experience Test

Goal: confirm the driver experience is usable.

Steps:

1. Drive while using the FPV headset.
2. Observe lag, freezing, and frame drops.
3. Compare close range and the real demo distance.
4. Check whether video issues happen before or after control issues.

Pass criteria:

- FPV feed remains usable at the target driving distance.
- Driver can react safely to steering and throttle changes.

## 7. Repeated Sponsor-Demo Simulation

Goal: reproduce the real failure mode: one setup works, another setup later fails.

Steps:

1. Shut everything down fully.
2. Start from the printed/demo checklist.
3. Run a short control test.
4. Shut everything down again.
5. Repeat at least five times.
6. Change only one variable per run if a failure occurs.

Pass criteria:

- Five consecutive setup cycles pass.
- Any failure has a logged cause: Wi-Fi, IP, joystick, Python process, ESP32 firmware, motor driver, power, or FPV.
