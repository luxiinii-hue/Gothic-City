"""Lerp, sine_wave, pulse helpers."""

import math


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def sine_wave(time: float, frequency: float, amplitude: float = 1.0,
              phase: float = 0.0) -> float:
    return amplitude * math.sin(2 * math.pi * frequency * time + phase)


def pulse(time: float, frequency: float, low: float = 0.0,
          high: float = 1.0) -> float:
    t = (math.sin(2 * math.pi * frequency * time) + 1.0) / 2.0
    return lerp(low, high, t)
