import time
import pygame

def measure_frame_timing(screen, fill=(0, 0, 0), frames=48, warmup=12):
    """Measure the display's achieved flip rate.

    Returns (hz, jitter_ms). This is only the true refresh rate if the display
    was created with vsync; without it flip() returns immediately and this
    reports how fast the CPU can draw instead. Jitter is the standard deviation
    of the frame intervals - a well-behaved vsynced display sits under ~1ms.
    """
    for _ in range(warmup):
        screen.fill(fill)
        pygame.display.flip()

    intervals = []
    prev = time.perf_counter()
    for _ in range(frames):
        screen.fill(fill)
        pygame.display.flip()
        now = time.perf_counter()
        intervals.append(now - prev)
        prev = now

    mean = sum(intervals) / len(intervals)
    if mean <= 0:
        return 0.0, 0.0
    variance = sum((i - mean) ** 2 for i in intervals) / len(intervals)
    return 1.0 / mean, variance ** 0.5 * 1000
