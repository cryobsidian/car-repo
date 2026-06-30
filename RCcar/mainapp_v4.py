from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass


DEFAULT_ESP32_IP = "192.168.4.2"

STEER_MIN = 60
STEER_CENTER = 90
STEER_MAX = 120

DRIVE_MIN = -255
DRIVE_MAX = 255
DRIVE_DEADZONE = 12

STEER_SEND_THRESHOLD = 2
DRIVE_SEND_THRESHOLD = 8

STATUS_TIMEOUT = 0.5
STOP_TIMEOUT = 0.3
CONTROL_TIMEOUT = 0.15

WARNING_INTERVAL = 1.0
DRY_RUN_PRINT_INTERVAL = 0.2

pygame = None
requests = None


@dataclass
class ControlState:
    wheel_raw: float
    throttle_raw: float
    clutch_raw: float
    throttle: int
    clutch: int
    drive: int
    angle: int


@dataclass
class SentState:
    angle: int | None = None
    drive: int | None = None


class WarningLimiter:
    def __init__(self, interval: float) -> None:
        self.interval = interval
        self.last_warning_by_key: dict[str, float] = {}

    def warn(self, key: str, message: str) -> None:
        now = time.monotonic()
        last_warning = self.last_warning_by_key.get(key, 0.0)
        if now - last_warning >= self.interval:
            print(f"WARNING: {message}")
            self.last_warning_by_key[key] = now


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Stable HTTP ground-station controller for the ESP32 RC car."
    )
    parser.add_argument("--ip", default=DEFAULT_ESP32_IP, help="ESP32 IP address.")
    parser.add_argument(
        "--joystick", type=int, default=0, help="Pygame joystick index to use."
    )
    parser.add_argument(
        "--loop-hz", type=float, default=30.0, help="Control loop rate in Hz."
    )
    parser.add_argument(
        "--steer-axis", type=int, default=0, help="Joystick axis for steering."
    )
    parser.add_argument(
        "--throttle-axis", type=int, default=2, help="Joystick axis for throttle."
    )
    parser.add_argument(
        "--clutch-axis",
        type=int,
        default=1,
        help="Joystick axis for clutch/reverse.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read joystick inputs and print mapped values without contacting ESP32.",
    )
    return parser.parse_args()


def load_pygame():
    global pygame
    if pygame is not None:
        return pygame

    try:
        import pygame as pygame_module
    except ImportError as exc:
        raise RuntimeError(
            "pygame is not installed. Install it in the demo Python environment "
            "before running the controller."
        ) from exc

    pygame = pygame_module
    return pygame


def load_requests():
    global requests
    if requests is not None:
        return requests

    try:
        import requests as requests_module
    except ImportError as exc:
        raise RuntimeError(
            "requests is not installed. Install it in the demo Python environment "
            "before running the controller."
        ) from exc

    requests = requests_module
    return requests


def map_range(x: float, in_min: float, in_max: float, out_min: int, out_max: int) -> int:
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def clamp(v: int | float, min_v: int | float, max_v: int | float) -> int | float:
    return max(min_v, min(v, max_v))


def init_joystick(joystick_index: int):
    pygame_module = load_pygame()
    pygame_module.init()
    pygame_module.joystick.init()

    joystick_count = pygame_module.joystick.get_count()
    if joystick_count == 0:
        raise RuntimeError("No joystick found. Connect the Logitech wheel first.")

    if joystick_index < 0 or joystick_index >= joystick_count:
        raise RuntimeError(
            f"Joystick index {joystick_index} is invalid. "
            f"Detected {joystick_count} joystick(s)."
        )

    joystick = pygame_module.joystick.Joystick(joystick_index)
    joystick.init()
    return joystick


def validate_axis(name: str, axis_index: int, axis_count: int) -> None:
    if axis_index < 0 or axis_index >= axis_count:
        raise RuntimeError(
            f"{name} axis {axis_index} is invalid for joystick with {axis_count} axes."
        )


def print_startup_info(args: argparse.Namespace, joystick) -> None:
    axis_count = joystick.get_numaxes()
    print("Joystick ready")
    print(f"  Name: {joystick.get_name()}")
    print(f"  Axes: {axis_count}")
    print("Axis mapping")
    print(f"  Steering axis: {args.steer_axis}")
    print(f"  Throttle axis: {args.throttle_axis}")
    print(f"  Clutch/reverse axis: {args.clutch_axis}")
    print(f"Control loop: {args.loop_hz:.1f} Hz")
    if args.dry_run:
        print("Dry run: ESP32 requests are disabled")
    else:
        print(f"ESP32 target: http://{args.ip}")


def request_get(
    session,
    base_url: str,
    endpoint: str,
    *,
    timeout: float,
    warning_limiter: WarningLimiter,
    params: dict[str, int] | None = None,
):
    requests_module = load_requests()
    url = f"{base_url}{endpoint}"
    try:
        response = session.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except requests_module.RequestException as exc:
        warning_limiter.warn(endpoint, f"GET {endpoint} failed: {exc}")
        return None


def check_esp32_ready(session, base_url: str, warning_limiter: WarningLimiter) -> None:
    print("Checking ESP32 readiness...")

    status = request_get(
        session,
        base_url,
        "/status",
        timeout=STATUS_TIMEOUT,
        warning_limiter=warning_limiter,
    )
    if status is None:
        raise RuntimeError("ESP32 /status check failed. Verify IP and Wi-Fi.")
    print(f"  /status OK: {status.text.strip()}")

    stop = request_get(
        session,
        base_url,
        "/stop",
        timeout=STOP_TIMEOUT,
        warning_limiter=warning_limiter,
    )
    if stop is None:
        raise RuntimeError("ESP32 /stop check failed. Motor safety is not confirmed.")
    print("  /stop OK")

    steer = request_get(
        session,
        base_url,
        "/steer",
        params={"value": STEER_CENTER},
        timeout=CONTROL_TIMEOUT,
        warning_limiter=warning_limiter,
    )
    if steer is None:
        raise RuntimeError("ESP32 steering center check failed.")
    print(f"  Steering centered at {STEER_CENTER}")


def read_controls(joystick, args: argparse.Namespace) -> ControlState:
    pygame.event.pump()

    wheel_raw = joystick.get_axis(args.steer_axis)
    throttle_raw = joystick.get_axis(args.throttle_axis)
    clutch_raw = joystick.get_axis(args.clutch_axis)

    throttle = map_range(throttle_raw, 1.0, -1.0, 0, DRIVE_MAX)
    clutch = map_range(clutch_raw, 1.0, -1.0, 0, DRIVE_MAX)
    throttle = int(clamp(throttle, 0, DRIVE_MAX))
    clutch = int(clamp(clutch, 0, DRIVE_MAX))

    drive = int(clamp(throttle - clutch, DRIVE_MIN, DRIVE_MAX))
    if abs(drive) < DRIVE_DEADZONE:
        drive = 0

    scaled_wheel = clamp(wheel_raw * 1.5, -1.0, 1.0)
    angle = map_range(float(scaled_wheel), -1.0, 1.0, STEER_MAX, STEER_MIN)
    angle = int(clamp(angle, STEER_MIN, STEER_MAX))

    return ControlState(
        wheel_raw=wheel_raw,
        throttle_raw=throttle_raw,
        clutch_raw=clutch_raw,
        throttle=throttle,
        clutch=clutch,
        drive=drive,
        angle=angle,
    )


def send_control_if_changed(
    session,
    base_url: str,
    controls: ControlState,
    sent_state: SentState,
    warning_limiter: WarningLimiter,
) -> None:
    if sent_state.drive is None or abs(controls.drive - sent_state.drive) >= DRIVE_SEND_THRESHOLD:
        response = request_get(
            session,
            base_url,
            "/throttle",
            params={"value": controls.drive},
            timeout=CONTROL_TIMEOUT,
            warning_limiter=warning_limiter,
        )
        if response is not None:
            sent_state.drive = controls.drive
            print(
                f"Drive={controls.drive:4d} "
                f"Throttle={controls.throttle:3d} "
                f"Clutch={controls.clutch:3d}"
            )

    if sent_state.angle is None or abs(controls.angle - sent_state.angle) >= STEER_SEND_THRESHOLD:
        response = request_get(
            session,
            base_url,
            "/steer",
            params={"value": controls.angle},
            timeout=CONTROL_TIMEOUT,
            warning_limiter=warning_limiter,
        )
        if response is not None:
            sent_state.angle = controls.angle
            print(f"Steer={controls.angle:3d} WheelRaw={controls.wheel_raw:.3f}")


def safe_stop(
    session,
    base_url: str,
    warning_limiter: WarningLimiter,
    *,
    dry_run: bool,
) -> None:
    if dry_run or session is None:
        return

    print("Sending safe shutdown commands...")
    request_get(
        session,
        base_url,
        "/throttle",
        params={"value": 0},
        timeout=CONTROL_TIMEOUT,
        warning_limiter=warning_limiter,
    )
    request_get(
        session,
        base_url,
        "/steer",
        params={"value": STEER_CENTER},
        timeout=CONTROL_TIMEOUT,
        warning_limiter=warning_limiter,
    )
    request_get(
        session,
        base_url,
        "/stop",
        timeout=STOP_TIMEOUT,
        warning_limiter=warning_limiter,
    )


def run_dry_loop(joystick, args: argparse.Namespace, loop_delay: float) -> None:
    print("Starting dry-run loop. Press Ctrl+C to stop.")
    next_tick = time.monotonic()
    last_print = 0.0

    while True:
        controls = read_controls(joystick, args)
        now = time.monotonic()
        if now - last_print >= DRY_RUN_PRINT_INTERVAL:
            print(
                f"WheelRaw={controls.wheel_raw: .3f} "
                f"ThrottleRaw={controls.throttle_raw: .3f} "
                f"ClutchRaw={controls.clutch_raw: .3f} "
                f"Steer={controls.angle:3d} "
                f"Throttle={controls.throttle:3d} "
                f"Clutch={controls.clutch:3d} "
                f"Drive={controls.drive:4d}"
            )
            last_print = now

        next_tick += loop_delay
        time.sleep(max(0.0, next_tick - time.monotonic()))


def run_control_loop(
    session,
    joystick,
    args: argparse.Namespace,
    base_url: str,
    warning_limiter: WarningLimiter,
    loop_delay: float,
) -> None:
    print("Starting control loop. Press Ctrl+C to stop.")
    next_tick = time.monotonic()
    sent_state = SentState()

    while True:
        controls = read_controls(joystick, args)
        send_control_if_changed(session, base_url, controls, sent_state, warning_limiter)

        next_tick += loop_delay
        time.sleep(max(0.0, next_tick - time.monotonic()))


def main() -> int:
    args = parse_args()
    if args.loop_hz <= 0:
        print("ERROR: --loop-hz must be greater than 0")
        return 2

    warning_limiter = WarningLimiter(WARNING_INTERVAL)
    session = None
    base_url = f"http://{args.ip}"

    try:
        joystick = init_joystick(args.joystick)
        axis_count = joystick.get_numaxes()
        validate_axis("Steering", args.steer_axis, axis_count)
        validate_axis("Throttle", args.throttle_axis, axis_count)
        validate_axis("Clutch/reverse", args.clutch_axis, axis_count)
        print_startup_info(args, joystick)

        loop_delay = 1.0 / args.loop_hz

        if args.dry_run:
            run_dry_loop(joystick, args, loop_delay)
        else:
            requests_module = load_requests()
            session = requests_module.Session()
            check_esp32_ready(session, base_url, warning_limiter)
            run_control_loop(session, joystick, args, base_url, warning_limiter, loop_delay)

    except KeyboardInterrupt:
        print("\nControl loop interrupted by operator.")
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1
    finally:
        safe_stop(session, base_url, warning_limiter, dry_run=args.dry_run)
        if session is not None:
            session.close()
        if pygame is not None:
            pygame.quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
