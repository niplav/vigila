import pygame
import time
from data_manager import DataManager

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

class AudioFusionFlickerTest:
    """Auditory flutter fusion threshold, by an ascending method of limits.

    Each level is a pre-rendered amplitude-modulated noise burst. The previous
    approach toggled a looping tone on and off from the 60fps main loop, which
    cannot exceed one toggle per frame: every nominal frequency above 30Hz came
    out as 30Hz of clicks, and the reported threshold was fiction. Rendering the
    modulation into the sample buffer removes the frame rate from the picture -
    at the mixer's sample rate any flutter rate of interest is exact.

    Noise rather than a pure tone is the carrier: modulating a 440Hz tone at
    flutter rates produces audible sidebands at 440 +/- f, so the listener ends
    up judging tone quality instead of flutter.
    """

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

        # Flutter rates to step through, slowest first
        self.frequencies = [5, 7, 10, 13, 16, 20, 25, 30, 35, 40, 45, 50,
                            56, 63, 70, 78, 87, 96, 106, 117, 129, 142, 156]
        self.level_idx = 0
        self.level_duration = 1.6  # seconds per burst
        self.level_start_time = None
        self.burst_cache = {}

        # State management
        self.state = 'instructions'  # instructions, flickering, result, rest
        self.trial_start_time = None
        self.rest_start_time = None
        self.detected_frequency = None
        self.previous_frequency = None
        self.detection_time = None

        # Audio setup
        self.audio_available = False
        self.sample_rate = 22050
        self.channel = None

        if NUMPY_AVAILABLE:
            try:
                if pygame.mixer.get_init() is None:
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                # Generate at whatever rate the mixer actually runs at, otherwise
                # the modulation plays back at the wrong rate
                self.sample_rate = pygame.mixer.get_init()[0]
                pygame.mixer.set_num_channels(2)
                self.channel = pygame.mixer.Channel(0)
                self.audio_available = True
            except Exception as e:
                print(f"Audio initialization failed: {e}")
                self.audio_available = False

    def _generate_burst(self, flutter_hz):
        """Noise burst, 100% square-wave amplitude modulated at flutter_hz"""
        if flutter_hz in self.burst_cache:
            return self.burst_cache[flutter_hz]

        sr = self.sample_rate
        n = int(self.level_duration * sr)
        rng = np.random.default_rng()

        carrier = rng.standard_normal(n) * 0.12
        np.clip(carrier, -1.0, 1.0, out=carrier)

        # Square envelope, then smoothed so the transitions do not click.
        # The smoothing window scales with the modulation period so it stays a
        # small fraction of a cycle even at the fastest rates.
        period = sr / flutter_hz
        envelope = ((np.arange(n) % period) < period / 2).astype(np.float64)

        ramp = max(1, min(int(0.0015 * sr), int(period / 8)))
        kernel = np.hanning(2 * ramp + 1)
        kernel /= kernel.sum()
        envelope = np.convolve(envelope, kernel, mode='same')

        wave = carrier * envelope

        # Overall fade in/out so the burst itself does not click
        fade = min(int(0.01 * sr), n // 2)
        if fade > 0:
            wave[:fade] *= np.linspace(0, 1, fade)
            wave[-fade:] *= np.linspace(1, 0, fade)

        samples = (wave * 32767).astype(np.int16)
        stereo = np.zeros((n, 2), dtype=np.int16)
        stereo[:, 0] = samples
        stereo[:, 1] = samples

        sound = pygame.sndarray.make_sound(stereo)
        self.burst_cache[flutter_hz] = sound
        return sound

    def _wait_for_dismiss(self, lines):
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
                rect.y = 160 + i * 36
                self.screen.blit(text, rect)
            pygame.display.flip()
            clock.tick(60)

    def _play_level(self):
        sound = self._generate_burst(self.frequencies[self.level_idx])
        self.channel.play(sound, loops=-1)

    def _stop_audio(self):
        if self.channel:
            self.channel.stop()

    def _start_trial(self, current_time):
        self.state = 'flickering'
        self.trial_start_time = current_time
        self.level_idx = 0
        self.level_start_time = current_time
        self._play_level()

    def _record_detection(self, current_time):
        self._stop_audio()
        frequency = self.frequencies[self.level_idx]
        self.detected_frequency = frequency
        self.previous_frequency = self.frequencies[self.level_idx - 1] if self.level_idx > 0 else None
        self.detection_time = current_time - self.trial_start_time

        self.valid_trials.append({
            'trial_number': self.current_trial + 1,
            'threshold_hz': frequency,
            'bracket_low_hz': self.previous_frequency,
            'bracket_high_hz': frequency,
            'detection_time_s': self.detection_time,
            'discarded': False,
            'timestamp': current_time
        })
        self.state = 'result'

    def _discard_trial(self, current_time, reason):
        self._stop_audio()
        self.discarded_trials.append({
            'trial_number': self.current_trial + 1,
            'threshold_hz': self.frequencies[self.level_idx],
            'detection_time_s': current_time - self.trial_start_time,
            'discarded': True,
            'timestamp': current_time,
            'reason': reason
        })
        self.state = 'instructions'

    def run(self):
        clock = pygame.time.Clock()

        if not self.audio_available:
            reason = "numpy is not installed" if not NUMPY_AVAILABLE else "the mixer could not be opened"
            print(f"Audio Fusion Flicker: audio unavailable ({reason}), aborting")
            self._wait_for_dismiss([
                "Audio not available - test cannot run.",
                "",
                f"Reason: {reason}.",
            ])
            return {}

        while self.running and self.current_trial < self.max_trials:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._stop_audio()
                    self.running = False
                    break

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._stop_audio()
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
                if current_time - self.level_start_time >= self.level_duration:
                    if self.level_idx + 1 >= len(self.frequencies):
                        self._discard_trial(current_time, 'max_frequency_reached')
                    else:
                        self.level_idx += 1
                        self.level_start_time = current_time
                        self._play_level()

            if self.state == 'rest':
                if current_time - self.rest_start_time >= 2.0:
                    self.state = 'instructions'

            if self.state == 'instructions' and len(self.valid_trials) >= self.min_trials:
                break

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        self._stop_audio()

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

        return {
            'mean_threshold_hz': mean_threshold,
            'std_threshold_hz': std_threshold,
            'valid_trials': len(self.valid_trials),
            'discarded_trials': len(self.discarded_trials),
            'sample_rate_hz': self.sample_rate,
            'carrier': 'white_noise',
            'modulation': 'square_100pct',
            'trials': self.valid_trials,
            'discarded': self.discarded_trials
        }

    def save_data(self, score):
        """Save test data"""
        if not score:
            return

        data = {
            "test_type": "audio_fusion_flicker",
            **score
        }

        try:
            data_manager = DataManager()
            filepath = data_manager.save_test_data('audio_fusion_flicker', data)
            print(f"Audio Fusion Flicker test data saved to {filepath}")
        except Exception as e:
            print(f"Error saving Audio Fusion Flicker test data: {e}")

    def draw(self):
        """Draw the test UI"""
        self.screen.fill(self.WHITE)

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        title_text = self.font.render("Audio Fusion Flicker Frequency", True, self.BLACK)
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
                (self.font, "A pulsing noise will step faster every", self.BLACK, -40),
                (self.font, f"{self.level_duration:.1f}s. Press SPACE when it sounds", self.BLACK, -5),
                (self.font, "STEADY rather than pulsing.", self.BLACK, 30),
                (self.small_font, f"Testing {self.frequencies[0]}-{self.frequencies[-1]} Hz", self.GRAY, 75),
                (self.small_font, "Press SPACE to start", self.BLUE, 110),
            ]
            for render_font, text, color, offset in lines:
                surface = render_font.render(text, True, color)
                rect = surface.get_rect()
                rect.center = (center_x, center_y + offset)
                self.screen.blit(surface, rect)

        elif self.state == 'flickering':
            listen_text = self.large_font.render("Listen", True, self.BLUE)
            listen_rect = listen_text.get_rect()
            listen_rect.center = (center_x, center_y - 40)
            self.screen.blit(listen_text, listen_rect)

            # Deliberately no frequency readout: seeing the number biases the call
            instruction = self.font.render("SPACE when it sounds STEADY", True, self.BLACK)
            instruction_rect = instruction.get_rect()
            instruction_rect.center = (center_x, center_y + 30)
            self.screen.blit(instruction, instruction_rect)

            hint = self.small_font.render("R to discard and restart this trial", True, self.RED)
            hint_rect = hint.get_rect()
            hint_rect.center = (center_x, center_y + 90)
            self.screen.blit(hint, hint_rect)

        elif self.state == 'result':
            result_text = self.large_font.render(f"{self.detected_frequency:.0f} Hz", True, self.BLUE)
            result_rect = result_text.get_rect()
            result_rect.center = (center_x, center_y - 50)
            self.screen.blit(result_text, result_rect)

            if self.previous_frequency:
                bracket = self.small_font.render(
                    f"between {self.previous_frequency} and {self.detected_frequency} Hz",
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

def run_audio_fusion_flicker(screen, font):
    """Module-level runner function"""
    test = AudioFusionFlickerTest(screen, font)
    return test.run()
