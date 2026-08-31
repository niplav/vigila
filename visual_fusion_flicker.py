import pygame
import time
from data_manager import DataManager
from display_timing import measure_frame_timing

class VisualFusionFlickerTest:
    """Critical flicker fusion frequency, measured by an ascending method of limits.

    The stimulus alternates black/white on a fixed number of display frames, so
    the only renderable frequencies are refresh/p for integer p >= 2. Sampling a
    sine wave at the frame rate - the previous approach - cannot work: above
    refresh/2 the waveform aliases, so raising the nominal frequency makes the
    apparent flicker slower rather than faster, and the reported number is an
    artifact. Because refresh/2 is the hard ceiling, a 60Hz panel tops out at
    30Hz, well under a typical CFF of 40-60Hz, and the test refuses to run.
    """

    MIN_USABLE_MAX_HZ = 45.0  # need headroom above a plausible CFF
    MAX_PLAUSIBLE_REFRESH_HZ = 250.0  # anything faster means vsync is not active

    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        self.running = True

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.RED = (220, 50, 50)
        self.GRAY = (200, 200, 200)

        # Test parameters
        self.min_trials = 4
        self.max_trials = 10
        self.current_trial = 0
        self.valid_trials = []
        self.discarded_trials = []

        # Measured on the first frame of run()
        self.refresh_hz = 0.0
        self.jitter_ms = 0.0
        self.levels = []  # (frame_period, frequency_hz), slowest first

        # Each level is shown for this long before stepping up
        self.level_duration = 2.5
        self.level_idx = 0
        self.level_start_time = None
        self.frame_in_cycle = 0

        # State management
        self.state = 'instructions'  # instructions, flickering, result, rest
        self.trial_start_time = None
        self.rest_start_time = None
        self.detected_frequency = None
        self.previous_frequency = None
        self.detection_time = None

    def _build_levels(self):
        """Renderable frequencies from ~5Hz up to refresh/2, slowest first"""
        levels = []
        p = 2
        while self.refresh_hz / p >= 5.0:
            levels.append((p, self.refresh_hz / p))
            p += 1
        levels.reverse()
        return levels

    def _wait_for_dismiss(self, lines):
        """Show a blocking message until the user presses something"""
        clock = pygame.time.Clock()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False

            self.screen.fill(self.WHITE)
            for i, line in enumerate(lines):
                text = self.font.render(line, True, self.BLACK)
                rect = text.get_rect()
                rect.centerx = self.screen.get_width() // 2
                rect.y = 140 + i * 36
                self.screen.blit(text, rect)
            pygame.display.flip()
            clock.tick(60)

    def _current_level(self):
        return self.levels[self.level_idx]

    def _start_trial(self, current_time):
        self.state = 'flickering'
        self.trial_start_time = current_time
        self.level_idx = 0
        self.level_start_time = current_time
        self.frame_in_cycle = 0

    def _record_detection(self, current_time):
        _, frequency = self._current_level()
        self.detected_frequency = frequency
        self.previous_frequency = self.levels[self.level_idx - 1][1] if self.level_idx > 0 else None
        self.detection_time = current_time - self.trial_start_time

        self.valid_trials.append({
            'trial_number': self.current_trial + 1,
            'threshold_hz': frequency,
            'frame_period': self._current_level()[0],
            # The threshold lies between the last level still seen as flickering
            # and this one; the gap is the resolution the display allows.
            'bracket_low_hz': self.previous_frequency,
            'bracket_high_hz': frequency,
            'detection_time_s': self.detection_time,
            'discarded': False,
            'timestamp': current_time
        })
        self.state = 'result'

    def _discard_trial(self, current_time, reason):
        _, frequency = self._current_level()
        self.discarded_trials.append({
            'trial_number': self.current_trial + 1,
            'threshold_hz': frequency,
            'detection_time_s': current_time - self.trial_start_time,
            'discarded': True,
            'timestamp': current_time,
            'reason': reason
        })
        self.state = 'instructions'

    def run(self):
        clock = pygame.time.Clock()

        # Measure what the display actually does before trusting frame counts
        self.refresh_hz, self.jitter_ms = measure_frame_timing(self.screen, fill=self.WHITE)
        max_hz = self.refresh_hz / 2
        print(f"Visual Fusion Flicker: measured {self.refresh_hz:.1f} Hz "
              f"(jitter {self.jitter_ms:.2f} ms), max renderable flicker {max_hz:.1f} Hz")

        if max_hz < self.MIN_USABLE_MAX_HZ:
            self._wait_for_dismiss([
                "Display too slow for this test.",
                "",
                f"Measured refresh: {self.refresh_hz:.0f} Hz",
                f"Highest renderable flicker: {max_hz:.0f} Hz",
                f"Critical flicker fusion needs at least {self.MIN_USABLE_MAX_HZ:.0f} Hz.",
                "",
                "Move the window to a high-refresh monitor",
                "and set that mode (xrandr --rate).",
            ])
            return {}

        # A rate no monitor runs at means flip() is not syncing to scanout, so
        # frame counting says nothing about what was actually displayed.
        if self.refresh_hz > self.MAX_PLAUSIBLE_REFRESH_HZ or self.jitter_ms > 3.0:
            self._wait_for_dismiss([
                "Cannot measure flicker: vsync is not active.",
                "",
                f"Measured flip rate: {self.refresh_hz:.0f} Hz",
                f"Frame jitter: {self.jitter_ms:.2f} ms",
                "",
                "Frame-locked stimuli need vsync to be",
                "meaningful. Check SDL_RENDER_VSYNC=1.",
            ])
            return {}

        self.levels = self._build_levels()

        while self.running and self.current_trial < self.max_trials:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        break

                    elif event.key == pygame.K_SPACE:
                        if self.state == 'instructions':
                            self._start_trial(current_time)

                        elif self.state == 'flickering':
                            self._record_detection(current_time)

                        elif self.state == 'result':
                            self.state = 'rest'
                            self.rest_start_time = current_time
                            self.current_trial += 1

                    elif event.key == pygame.K_r:
                        if self.state == 'flickering':
                            self._discard_trial(current_time, 'user_restart')

            if self.state == 'flickering':
                # Step up to the next frequency once this level has had its time
                if current_time - self.level_start_time >= self.level_duration:
                    if self.level_idx + 1 >= len(self.levels):
                        self._discard_trial(current_time, 'max_frequency_reached')
                    else:
                        self.level_idx += 1
                        self.level_start_time = current_time
                        self.frame_in_cycle = 0

            # Auto-advance from rest
            if self.state == 'rest':
                if current_time - self.rest_start_time >= 2.0:
                    self.state = 'instructions'

            # Enough valid trials collected
            if self.state == 'instructions' and len(self.valid_trials) >= self.min_trials:
                break

            self.draw()
            pygame.display.flip()

            if self.state == 'flickering':
                # Frame-locked: advance one display frame per loop, no software cap
                self.frame_in_cycle = (self.frame_in_cycle + 1) % self._current_level()[0]
            else:
                clock.tick(60)

        score = self.calculate_score()
        self.save_data(score)
        return score

    def calculate_score(self):
        """Calculate test statistics"""
        if not self.valid_trials:
            return {}

        thresholds = [t['threshold_hz'] for t in self.valid_trials]
        mean_threshold = sum(thresholds) / len(thresholds)

        if len(thresholds) > 1:
            variance = sum((t - mean_threshold) ** 2 for t in thresholds) / len(thresholds)
            std_threshold = variance ** 0.5
        else:
            std_threshold = 0

        # Coarsest gap between adjacent renderable levels around the threshold
        brackets = [t['bracket_low_hz'] for t in self.valid_trials if t['bracket_low_hz']]
        resolution = max((t['bracket_high_hz'] - t['bracket_low_hz'])
                         for t in self.valid_trials if t['bracket_low_hz']) if brackets else None

        return {
            'mean_threshold_hz': mean_threshold,
            'std_threshold_hz': std_threshold,
            'valid_trials': len(self.valid_trials),
            'discarded_trials': len(self.discarded_trials),
            # Frequencies are quantised to refresh/p, so record what the display
            # was actually doing and how coarse the steps were.
            'measured_refresh_hz': self.refresh_hz,
            'frame_jitter_ms': self.jitter_ms,
            'frequency_resolution_hz': resolution,
            'trials': self.valid_trials,
            'discarded': self.discarded_trials
        }

    def save_data(self, score):
        """Save test data"""
        if not score:
            return

        data = {
            "test_type": "visual_fusion_flicker",
            **score
        }

        try:
            data_manager = DataManager()
            filepath = data_manager.save_test_data('visual_fusion_flicker', data)
            print(f"Visual Fusion Flicker test data saved to {filepath}")
        except Exception as e:
            print(f"Error saving Visual Fusion Flicker test data: {e}")

    def draw(self):
        """Draw the test UI"""
        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        if self.state == 'flickering':
            # Nothing but the square: any static chrome gives away the flicker
            # by contrast, and redrawing text every frame costs frame time.
            frame_period, _ = self._current_level()
            on_frames = (frame_period + 1) // 2
            lit = self.frame_in_cycle < on_frames

            self.screen.fill(self.BLACK)
            square = pygame.Rect(0, 0, 300, 300)
            square.center = (center_x, center_y)
            pygame.draw.rect(self.screen, self.WHITE if lit else self.BLACK, square)
            pygame.draw.rect(self.screen, self.GRAY, square, 1)

            hint = self.small_font.render("SPACE when SOLID     R to restart", True, self.GRAY)
            hint_rect = hint.get_rect()
            hint_rect.center = (center_x, self.screen.get_height() - 30)
            self.screen.blit(hint, hint_rect)
            return

        self.screen.fill(self.WHITE)

        # Title
        title_text = self.font.render("Visual Fusion Flicker Frequency", True, self.BLACK)
        self.screen.blit(title_text, (20, 20))

        trial_text = self.small_font.render(
            f"Trial: {self.current_trial + 1}  |  Valid: {len(self.valid_trials)}/{self.min_trials}",
            True, self.BLACK
        )
        trial_rect = trial_text.get_rect()
        trial_rect.right = self.screen.get_width() - 20
        trial_rect.y = 20
        self.screen.blit(trial_text, trial_rect)

        if self.state == 'instructions':
            lines = [
                (self.large_font, "Ready", self.BLUE, -110),
                (self.font, "A square will flicker, stepping faster every", self.BLACK, -40),
                (self.font, f"{self.level_duration:.1f}s. Press SPACE when it looks SOLID.", self.BLACK, -5),
                (self.small_font, f"Display: {self.refresh_hz:.0f} Hz, "
                                  f"testing {self.levels[0][1]:.1f}-{self.levels[-1][1]:.1f} Hz",
                 self.GRAY, 45),
                (self.small_font, "Press SPACE to start", self.BLUE, 85),
            ]
            for render_font, text, color, offset in lines:
                surface = render_font.render(text, True, color)
                rect = surface.get_rect()
                rect.center = (center_x, center_y + offset)
                self.screen.blit(surface, rect)

        elif self.state == 'result':
            result_text = self.large_font.render(f"{self.detected_frequency:.1f} Hz", True, self.BLUE)
            result_rect = result_text.get_rect()
            result_rect.center = (center_x, center_y - 50)
            self.screen.blit(result_text, result_rect)

            if self.previous_frequency:
                bracket = self.small_font.render(
                    f"between {self.previous_frequency:.1f} and {self.detected_frequency:.1f} Hz",
                    True, self.GRAY)
                bracket_rect = bracket.get_rect()
                bracket_rect.center = (center_x, center_y + 5)
                self.screen.blit(bracket, bracket_rect)

            continue_text = self.small_font.render("Press SPACE to continue", True, self.BLACK)
            continue_rect = continue_text.get_rect()
            continue_rect.center = (center_x, center_y + 70)
            self.screen.blit(continue_text, continue_rect)

        elif self.state == 'rest':
            rest_text = self.font.render("Rest...", True, self.BLACK)
            rest_rect = rest_text.get_rect()
            rest_rect.center = (center_x, center_y)
            self.screen.blit(rest_text, rest_rect)

        # Running mean
        if self.valid_trials and self.state in ('instructions', 'rest'):
            thresholds = [t['threshold_hz'] for t in self.valid_trials]
            stats_text = self.small_font.render(
                f"Mean threshold: {sum(thresholds) / len(thresholds):.1f} Hz (n={len(thresholds)})",
                True, self.BLACK
            )
            stats_rect = stats_text.get_rect()
            stats_rect.centerx = center_x
            stats_rect.y = self.screen.get_height() - 40
            self.screen.blit(stats_text, stats_rect)

def run_visual_fusion_flicker(screen, font):
    """Module-level runner function"""
    test = VisualFusionFlickerTest(screen, font)
    return test.run()
