# Custom illumination unit for Chara braunii cultivation

From the publication

### Optimized protocols for the laboratory maintenance and functional testing of *Chara braunii*

Authors: Katarina Kurtović, Jan Petrášek and Stanislav Vosolsobě

Charles University, Department of Experimental Plant Biology

Code desigh: Stanislav Vosolsobě

Contact: vosolsob@natur.cuni.cz

This is Raspberry PI script which enables a regulation of a custom LED panel for the cultivation of *Chara braunii*.

The regulation is based on PWM regulation. The setup enables to control "sunrise" and "sunset" times; illumination intensity can be regulated sharply (on/off), or according to sinusoidal curve, which mimics the natural light intensity.

## Import of libraries

The library `pigpio` is important for the 

```python
#!/usr/bin/python3

import time
import math
import pigpio

# =======================
# USER PARAMETERS
# =======================

sunrise = 6.0    # hour of sunrise (e.g. 6.0 = 06:00)
sunset  = 18.0   # hour of sunset (e.g. 18.0 = 18:00)

# LED intensities (percent) for RGBWUVPA — 0–100 %
led = [10, 30, 5, 100, 0, 10]

# Use sinusoidal daylight cycle? (1=yes, 0=always max during day)
sin_l = 1

# Fast test mode — set simulated hour increments (0 for real clock)
fast_test = 0  # e.g. 0.1 for simulation

# =======================
# GPIO PIN ASSIGNMENT
# =======================

R = 12
G = 25
B = 22
W = 23
U = 5
P = 6
A = 24

pi = pigpio.pi()

# =======================
# FUNCTIONS
# =======================

def LEDs(led, ilum):
    """Set duty cycle for each channel (0-100% per color * illumination curve)."""
    scale = lambda x: round(2.55 * ilum * x)
    pins = [R, G, B, W, U, P, A]

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

# =======================
# MAIN LOOP
# =======================

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

