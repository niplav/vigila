import os
import sys

# Ask SDL to sync flips to the display refresh. The frame-locked stimuli in the
# flicker and brief-detection tests are only accurate if this takes effect;
# without it flip() returns immediately and frame counts mean nothing.
os.environ.setdefault("SDL_RENDER_VSYNC", "1")

import pygame
from data_manager import DataManager
from pvt import run_pvt
from dsst import run_dsst
from digit_span import run_digit_span
from stanford_sleepiness import run_stanford_sleepiness_scale
from subjective_feelings import run_subjective_feelings
from stroop import run_stroop
from temporal_production import run_temporal_production
from temporal_reproduction import run_temporal_reproduction
from visual_fusion_flicker import run_visual_fusion_flicker
from audio_fusion_flicker import run_audio_fusion_flicker
from simultaneous_temporal import run_simultaneous_temporal
from brief_stimulus_detection import run_brief_stimulus_detection

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
LIGHT_BLUE = (100, 165, 215)
GRAY = (128, 128, 128)
RED = (220, 20, 60)
LIGHT_RED = (240, 60, 90)

# Create the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), vsync=1)
pygame.display.set_caption("Orexin Data Collection Tool")

# Font
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 24)

# Progressively smaller fonts, so a long button label can be shrunk to fit
button_fonts = [pygame.font.Font(None, size) for size in (36, 32, 28, 24, 20)]

# Initialize data manager
data_manager = DataManager()

# Menu layout - 3 columns
COLS = 3
BUTTON_WIDTH = 165
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20
GRID_START_X = SCREEN_WIDTH // 2 - (COLS * BUTTON_WIDTH + (COLS - 1) * BUTTON_SPACING) // 2
GRID_START_Y = 175

def summarize_pvt(rts):
    if not rts:
        return ["No trials completed."]
    valid = [rt for rt in rts if rt >= 100]
    lines = [
        f"Trials: {len(rts)}",
        f"Mean RT: {sum(valid) / len(valid):.0f} ms" if valid else "Mean RT: n/a",
        f"Fastest: {min(valid):.0f} ms    Slowest: {max(valid):.0f} ms" if valid else "",
        f"Lapses (>500ms): {sum(1 for rt in valid if rt > 500)}",
    ]
    if len(valid) < len(rts):
        lines.append(f"Anticipations (<100ms, excluded): {len(rts) - len(valid)}")
    return [l for l in lines if l]

def summarize_dsst(s):
    return [
        f"Correct: {s['correct_count']}/{s['total_attempted']}",
        f"Accuracy: {s['accuracy'] * 100:.1f}%",
    ]

def summarize_digit_span(s):
    return [
        f"Forward span: {s['forward_span']}",
        f"Backward span: {s['backward_span']}",
        f"Total: {s['total_span']}",
    ]

def summarize_sss(rating):
    return [f"Sleepiness rating: {rating}/7"]

def summarize_feelings(text):
    return [f"Recorded: {text[:60]}"]

def summarize_stroop(s):
    return [
        f"Accuracy: {s['accuracy'] * 100:.1f}%  ({s['correct_count']}/{s['total_trials']})",
        f"Mean RT congruent: {s['mean_rt_congruent_ms']:.0f} ms",
        f"Mean RT incongruent: {s['mean_rt_incongruent_ms']:.0f} ms",
        f"Stroop effect: {s['stroop_effect_ms']:+.0f} ms",
    ]

def summarize_temp_prod(s):
    lines = [
        f"Trials: {s['total_trials']}",
        f"Mean absolute error: {s['mean_absolute_percent_error']:.1f}%",
        f"Mean signed error: {s['mean_error_s']:+.1f} s",
    ]
    for dur, d in s['by_duration'].items():
        lines.append(f"  {dur}: produced {d['mean_produced_s']:.1f}s (CV {d['coefficient_of_variation']:.2f})")
    return lines

def summarize_temp_repro(s):
    return [
        f"Trials: {s['total_trials']}",
        f"Mean absolute error: {s['mean_absolute_error_s']:.1f} s",
        f"Mean signed error: {s['mean_percent_error']:+.1f}%",
        f"Slope: {s['slope_regression']:.2f}   r: {s['correlation_stimulus_reproduction']:.2f}",
    ]

def summarize_sim_temp(s):
    return [
        f"Trials: {s['total_trials']}",
        f"Mean time error: {s['mean_time_error_s']:+.1f} s (target {s['target_duration_s']}s)",
        f"Subtraction accuracy: {s['overall_subtraction_accuracy'] * 100:.1f}%",
        f"Subtractions per trial: {s['mean_subtractions_per_trial']:.1f}",
    ]

def summarize_flicker(s):
    lines = [
        f"Mean threshold: {s['mean_threshold_hz']:.1f} Hz (SD {s['std_threshold_hz']:.1f})",
        f"Valid trials: {s['valid_trials']}   Discarded: {s['discarded_trials']}",
    ]
    if s.get('measured_refresh_hz'):
        lines.append(f"Display: {s['measured_refresh_hz']:.0f} Hz, "
                     f"jitter {s['frame_jitter_ms']:.2f} ms")
    if s.get('frequency_resolution_hz'):
        lines.append(f"Step size at threshold: {s['frequency_resolution_hz']:.1f} Hz")
    return lines

def summarize_brief_stim(s):
    lines = []
    for blk, d in s.get('blocks', {}).items():
        threshold = d['estimated_threshold']
        bound = " (lower bound)" if d.get('threshold_is_lower_bound') else ""
        lines.append(f"{blk}: {threshold:.1f} {d['threshold_unit']}{bound}"
                     if threshold is not None else f"{blk}: no threshold")
        lines.append(f"  hits {d['hits']}/{d['n_signal_trials']}, "
                     f"false alarms {d['false_alarms']}/{d['n_catch_trials']}"
                     + (f", d'={d['d_prime']:.2f}" if d.get('d_prime') is not None else ""))
        if d.get('threshold_is_lower_bound'):
            lines.append(f"  staircase sat on its floor for {d['floor_pinned_trials']} trials")
    return lines

# label, shortcut key, runner, summary function
TESTS = [
    ("PVT", pygame.K_1, run_pvt, summarize_pvt),
    ("DSST", pygame.K_2, run_dsst, summarize_dsst),
    ("Digit Span", pygame.K_3, run_digit_span, summarize_digit_span),
    ("Sleepiness", pygame.K_4, run_stanford_sleepiness_scale, summarize_sss),
    ("Feelings", pygame.K_5, run_subjective_feelings, summarize_feelings),
    ("Stroop", pygame.K_6, run_stroop, summarize_stroop),
    ("Time Prod", pygame.K_7, run_temporal_production, summarize_temp_prod),
    ("Time Repro", pygame.K_8, run_temporal_reproduction, summarize_temp_repro),
    ("Dual Task", pygame.K_9, run_simultaneous_temporal, summarize_sim_temp),
    ("Visual Flicker", pygame.K_v, run_visual_fusion_flicker, summarize_flicker),
    ("Audio Flicker", pygame.K_a, run_audio_fusion_flicker, summarize_flicker),
    ("Brief Stim", pygame.K_b, run_brief_stimulus_detection, summarize_brief_stim),
]

def button_rect(i):
    """Screen rectangle for the i-th menu button"""
    col = i % COLS
    row = i // COLS
    x = GRID_START_X + col * (BUTTON_WIDTH + BUTTON_SPACING)
    y = GRID_START_Y + row * (BUTTON_HEIGHT + BUTTON_SPACING)
    return pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)

def exit_rect():
    """Exit sits in the last column of the row below the test grid"""
    rows = (len(TESTS) + COLS - 1) // COLS
    x = GRID_START_X + (COLS - 1) * (BUTTON_WIDTH + BUTTON_SPACING)
    y = GRID_START_Y + rows * (BUTTON_HEIGHT + BUTTON_SPACING)
    return pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)

def fit_font(text, max_width):
    """Largest of the button fonts whose rendering of text fits max_width"""
    for candidate in button_fonts:
        if candidate.size(text)[0] <= max_width:
            return candidate
    return button_fonts[-1]

def draw_button(rect, text, color, hover_color, shortcut=None):
    """Draw a button, lightened while the mouse is over it"""
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, hover_color if hovered else color, rect)
    pygame.draw.rect(screen, BLACK, rect, 3 if hovered else 2)

    # Leave room on both sides for the shortcut badge so the label stays centred
    padding = 34 if shortcut else 16
    label_font = fit_font(text, rect.width - padding)
    label = label_font.render(text, True, WHITE)
    label_rect = label.get_rect()
    label_rect.center = rect.center
    screen.blit(label, label_rect)

    if shortcut:
        key_label = small_font.render(shortcut, True, WHITE)
        screen.blit(key_label, (rect.x + 5, rect.y + 3))

def wrap_text(text, render_font, max_width):
    """Split text into lines that fit within max_width pixels"""
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if render_font.size(candidate)[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def show_message(title, lines, title_color=BLACK, button_text="OK"):
    """Blocking screen showing a title, some lines, and a dismiss button.

    Returns False if the window was closed, True otherwise.
    """
    clock = pygame.time.Clock()
    dismiss = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 80, 150, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                return True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if dismiss.collidepoint(pygame.mouse.get_pos()):
                    return True

        screen.fill(WHITE)

        heading = title_font.render(title, True, title_color)
        heading_rect = heading.get_rect()
        heading_rect.centerx = SCREEN_WIDTH // 2
        heading_rect.y = 60
        screen.blit(heading, heading_rect)

        y = 140
        for line in lines:
            for wrapped in wrap_text(line, font, SCREEN_WIDTH - 80):
                surface = font.render(wrapped, True, BLACK)
                rect = surface.get_rect()
                rect.centerx = SCREEN_WIDTH // 2
                rect.y = y
                screen.blit(surface, rect)
                y += 34

        draw_button(dismiss, button_text, GRAY, BLUE)

        hint = small_font.render("Press any key to continue", True, GRAY)
        hint_rect = hint.get_rect()
        hint_rect.centerx = SCREEN_WIDTH // 2
        hint_rect.y = SCREEN_HEIGHT - 25
        screen.blit(hint, hint_rect)

        pygame.display.flip()
        clock.tick(60)

def run_test(label, runner, summarize):
    """Run one test and show its results on screen.

    Returns False if the window was closed during the results screen.
    """
    print(f"Starting {label}...")
    try:
        result = runner(screen, font)
    except Exception as e:
        print(f"{label} failed: {e}")
        return show_message(f"{label} failed", [str(e)], title_color=RED)

    if not result:
        print(f"{label}: no data collected")
        return show_message(label, ["Cancelled - no data collected."], title_color=GRAY)

    lines = summarize(result)
    for line in lines:
        print(f"  {line}")
    return show_message(f"{label} complete", lines)

def draw_menu():
    screen.fill(WHITE)

    title = title_font.render("Orexin Data Collection", True, BLACK)
    title_rect = title.get_rect()
    title_rect.centerx = SCREEN_WIDTH // 2
    title_rect.y = 60
    screen.blit(title, title_rect)

    subtitle = font.render("Psychological Testing Suite", True, GRAY)
    subtitle_rect = subtitle.get_rect()
    subtitle_rect.centerx = SCREEN_WIDTH // 2
    subtitle_rect.y = 110
    screen.blit(subtitle, subtitle_rect)

    for i, (label, key, _, _) in enumerate(TESTS):
        draw_button(button_rect(i), label, BLUE, LIGHT_BLUE, pygame.key.name(key).upper())

    draw_button(exit_rect(), "Exit", RED, LIGHT_RED, "ESC")

    pygame.display.flip()

def main():
    # Check data setup before starting
    error_msg = data_manager.check_data_setup()
    if error_msg:
        show_message("Error", [error_msg], title_color=RED, button_text="Exit")
        pygame.quit()
        sys.exit(1)

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                else:
                    for label, key, runner, summarize in TESTS:
                        if event.key == key:
                            running = run_test(label, runner, summarize)
                            break

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if exit_rect().collidepoint(mouse_pos):
                    running = False
                else:
                    for i, (label, _, runner, summarize) in enumerate(TESTS):
                        if button_rect(i).collidepoint(mouse_pos):
                            running = run_test(label, runner, summarize)
                            break

        draw_menu()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
