import pygame

pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Name:", joystick.get_name())

while True:
    pygame.event.pump()

    steering = joystick.get_axis(0)   # ???
    throttle = joystick.get_axis(2)   # ??
    brake = joystick.get_axis(3)      # ??

    print(f"Steering: {steering:.2f}, Throttle: {throttle:.2f}, Brake: {brake:.2f}")