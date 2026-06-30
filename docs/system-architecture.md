# System Architecture

## High-Level Design

```text
+----------------------+       USB        +----------------------+
| Logitech wheel/pedal | ----------------> | Ground station       |
| input device         |                   | laptop / host        |
+----------------------+                   +----------+-----------+
                                                      |
                                                      | Wi-Fi UDP packets
                                                      v
                                           +----------+-----------+
                                           | Onboard controller  |
                                           | ESP32 / Pi / Pico W |
                                           +----------+-----------+
                                                      |
                                                      | PWM
                             +------------------------+------------------------+
                             v                                                 v
                    +--------+---------+                              +--------+-------+
                    | Steering servo   |                              | ESC / driver   |
                    +------------------+                              +----------------+
```

The FPV video system runs alongside this control path:

```text
Camera / FPV transmitter on car -> DJI FPV headset / receiver
```

## Input Tier

The Logitech wheel does not directly control the car over Wi-Fi. It needs a host device, usually a laptop or a second Raspberry Pi, to read input over USB.

Expected host responsibilities:

- Detect the wheel and pedals.
- Poll steering and pedal values continuously.
- Normalize values into a small control payload.
- Send the newest payload to the car at a fixed update rate.

Common Python libraries for input polling include `pygame` and `inputs`.

## Transmission Tier

The control link should use lightweight packets over Wi-Fi.

Recommended first protocol: UDP.

Reason:

- UDP avoids waiting for retransmission of old data.
- For live control, the newest steering and throttle value is more useful than a delayed old value.
- Lost packets are acceptable if packets are sent frequently and the onboard controller has a timeout failsafe.

Example payload:

```json
{
  "steering": 0.45,
  "throttle": 0.80,
  "brake": 0.00
}
```

## Onboard Control Tier

The onboard controller listens for control packets, extracts values, and maps them to hardware outputs.

Expected onboard responsibilities:

- Connect to the control Wi-Fi network.
- Listen on a fixed UDP port.
- Parse steering, throttle, and brake values.
- Clamp values to safe limits.
- Convert normalized values to PWM commands.
- Stop or neutralize output if packets stop arriving.

## Actuation Tier

Standard RC-style components generally use PWM signals.

Typical RC PWM range:

- 1.0 ms: full left or reverse
- 1.5 ms: center or neutral
- 2.0 ms: full right or forward

The steering servo receives a PWM signal for wheel angle.

The ESC or motor driver receives throttle/brake commands. The onboard controller must not drive high motor current directly from GPIO pins.

## Board Choice

The planning doc mentions multiple possible boards:

- ESP32
- Raspberry Pi
- Raspberry Pi Pico W

The code direction currently sounds closest to MicroPython on ESP32 or Raspberry Pi Pico W because of references to `network`, `machine`, and `duty_u16`.

The team should choose one target before implementation, because the GPIO, PWM, Wi-Fi, and library APIs differ.
