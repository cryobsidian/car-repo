# Testing Plan

## Test Sequence

Start with controlled bench tests before driving the car.

## 1. Input Read Test

Goal: confirm the ground station can read the wheel and pedals.

Steps:

1. Connect the Logitech wheel and pedals over USB.
2. Run a simple input polling script.
3. Turn the wheel left and right.
4. Press accelerator and brake pedals.
5. Confirm values update smoothly.

Pass criteria:

- Steering value reaches left, center, and right.
- Pedal values reach released and fully pressed states.
- No input axis is inverted unless intentionally mapped that way.

## 2. Packet Send/Receive Test

Goal: confirm the ground station can send values to the onboard board.

Steps:

1. Put both devices on the same Wi-Fi network.
2. Send UDP packets at a fixed rate.
3. Print received values on the onboard board.
4. Move wheel and pedals while watching received output.

Pass criteria:

- Onboard board receives packets continuously.
- Values match user input.
- Packet updates continue without noticeable pauses at close range.

## 3. PWM Output Test

Goal: confirm the onboard board can drive servo/ESC signals safely.

Steps:

1. Test steering servo with wheels off the ground.
2. Calibrate center, minimum, and maximum steering positions.
3. Test ESC or motor driver with drive wheels lifted.
4. Verify neutral output before enabling throttle.

Pass criteria:

- Servo responds predictably.
- Throttle does not activate unexpectedly.
- Failsafe returns throttle to neutral or zero.

## 4. Close-Range Drive Test

Goal: confirm the full control loop works at short range.

Steps:

1. Drive at low speed in an open area.
2. Test steering, acceleration, braking, and failsafe.
3. Record latency and any packet drops.

Pass criteria:

- Car is controllable.
- No runaway behavior occurs.
- FPV video is usable if included in the test.

## 5. Range Test

Goal: identify the reliable operating distance.

Steps:

1. Start close to the ground station.
2. Increase distance in fixed increments.
3. Test line-of-sight first.
4. Repeat with walls or obstacles if safe.
5. Record where control or FPV becomes unacceptable.

Pass criteria:

- Team records the maximum comfortable control distance.
- Team records whether failure is due to Wi-Fi disconnect, packet loss, latency, or FPV video quality.

## 6. FPV Experience Test

Goal: confirm the driver experience is usable.

Steps:

1. Drive while using the FPV headset.
2. Observe lag, freezing, and frame drops.
3. Compare close range and longer range.
4. Check whether video issues happen before or after control issues.

Pass criteria:

- FPV feed remains usable at the target driving distance.
- Driver can react safely to steering and throttle changes.
