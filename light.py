#!/usr/bin/python3

import time
import math
import pigpio

# Setting of time interval for illumination in hours (e.g. 6.5 = 06:30)
sunrise = 6.0 
sunset  = 18.0 

# LED intensities (percent) for RGBWUVP — 0–100 %
led = [10, 30, 5, 100, 0, 10]

# Use sine wave illumination? (1=yes, 0=always max during day)
sin_l = 1

# GPIO PIN assignment
R = 4
B = 17
G = 18
W = 27
U = 22
P = 23

# Fast test mode — set simulated hour increments (0 for real clock)
fast_test = 0  # e.g. 0.1 for simulation

pi = pigpio.pi()

def LEDs(led, ilum):
    """Set duty cycle for each channel (0-100% per color * illumination curve)."""
    scale = lambda x: round(2.55 * ilum * x)
    pins = [R, G, B, W, U, P]

    for pin, pct in zip(pins, led):
        pi.set_PWM_dutycycle(pin, scale(pct))


def illum(hour, sin_mode):
    """Compute daylight intensity 0–1 based on time and sinusoidal or flat mode."""
    sunlen = sunset - sunrise
    noon = (sunrise + sunset) / 2

    # normalizing curve base
    B = math.cos(math.pi * (sunrise - noon) / 12)
    sun = math.cos(math.pi * (hour - noon) / 12) - B

    # normalized 0–1 sinusoid
    norm_light = sun / (1 - B)

    # binary day/night flag
    day = 1 if sunrise <= hour <= sunset else 0

    if sin_mode == 0:
        return day
    else:
        return max(0, day * norm_light)

  print("🌞 Illumination control started.")
print(f"Sunrise: {sunrise}h, Sunset: {sunset}h, Sinusoid: {sin_l}, Fast-step: {fast_test}")

# Ensure LEDs start OFF
LEDs([0,0,0,0,0,0,0], 1)
time.sleep(1)

hours = 0

while True:
    if fast_test == 0:
        now = time.localtime()
        hours = now.tm_hour + now.tm_min / 60 + now.tm_sec / 3600

    light = illum(hours, sin_l)
    LEDs(led, light)

    print(f"Time {hours:.2f}h | Light intensity: {light:.3f}")

    # increment time in simulation
    hours += fast_test
    if hours >= 24: hours = 0

    time.sleep(1 if fast_test else 5)
