import pygame
import random
import time
from data_manager import DataManager

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

class TemporalReproductionTest:
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
        self.GREEN = (50, 200, 50)
        self.ORANGE = (255, 140, 0)

        # Test parameters
        self.num_trials = 10
        self.current_trial = 0
        self.results = []

        # Generate random stimulus durations (5-30 seconds, uniform distribution)
        self.stimulus_durations = [random.uniform(5.0, 30.0) for _ in range(self.num_trials)]

        # State management
        self.state = 'get_ready'  # get_ready, playing, pause, instructions, reproducing, feedback, rest
        self.state_start_time = None
        self.stimulus_start_time = None
        self.stimulus_end_time = None
        self.reproduction_start_time = None
        self.reproduction_end_time = None
        self.current_duration = None
        self.current_sound = None
        self.space_pressed = False

        # Initialize audio if available
        self.audio_available = False
        if NUMPY_AVAILABLE:
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.audio_available = True
            except Exception as e:
                print(f"Audio initialization failed: {e}")
                self.audio_available = False

    def _generate_tone(self, duration_s, frequency=440):
        """Generate a sine wave tone"""
        if not NUMPY_AVAILABLE:
            return None

        sample_rate = 22050
        samples = int(duration_s * sample_rate)
        t = np.linspace(0, duration_s, samples)
        wave = np.sin(2 * np.pi * frequency * t)

        # Apply fade in/out to avoid clicks
        fade_samples = int(0.01 * sample_rate)  # 10ms fade
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        wave[:fade_samples] *= fade_in
        wave[-fade_samples:] *= fade_out

        # Convert to 16-bit integers
        wave = (wave * 32767).astype(np.int16)

        # Create stereo
        stereo = np.zeros((samples, 2), dtype=np.int16)
        stereo[:, 0] = wave
        stereo[:, 1] = wave

        return pygame.sndarray.make_sound(stereo)

    def run(self):
        clock = pygame.time.Clock()
        self.state = 'get_ready'
        self.state_start_time = time.time()

        while self.running and self.current_trial < self.num_trials:
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
                            # Start reproduction
                            self.space_pressed = True
                            self.reproduction_start_time = current_time
                            self.state = 'reproducing'

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        if self.state == 'reproducing' and self.space_pressed:
                            # Stop reproduction
                            self.reproduction_end_time = current_time
                            reproduced_duration = self.reproduction_end_time - self.reproduction_start_time
                            error = reproduced_duration - self.current_duration
                            percent_error = (error / self.current_duration) * 100

                            # Record result
                            trial_data = {
                                'trial_number': self.current_trial + 1,
                                'stimulus_duration_s': self.current_duration,
                                'reproduced_duration_s': reproduced_duration,
                                'error_s': error,
                                'percent_error': percent_error,
                                'absolute_error_s': abs(error),
                                'stimulus_start_time': self.stimulus_start_time,
                                'stimulus_end_time': self.stimulus_end_time,
                                'reproduction_start_time': self.reproduction_start_time,
                                'reproduction_end_time': self.reproduction_end_time
                            }
                            self.results.append(trial_data)

                            self.space_pressed = False
                            self.state = 'feedback'
                            self.state_start_time = current_time

            # State machine updates
            if self.state == 'get_ready':
                if current_time - self.state_start_time >= 1.0:  # 1 second
                    # Start playing tone
                    self.current_duration = self.stimulus_durations[self.current_trial]

                    if self.audio_available:
                        self.current_sound = self._generate_tone(self.current_duration)
                        if self.current_sound:
                            self.current_sound.play()

                    self.stimulus_start_time = current_time
                    self.stimulus_end_time = current_time + self.current_duration
                    self.state = 'playing'
                    self.state_start_time = current_time

            elif self.state == 'playing':
                if current_time >= self.stimulus_end_time:
                    # Tone finished, pause briefly
                    self.state = 'pause'
                    self.state_start_time = current_time

            elif self.state == 'pause':
                if current_time - self.state_start_time >= 1.0:  # 1 second pause
                    # Show reproduction instructions
                    self.state = 'instructions'
                    self.state_start_time = current_time

            elif self.state == 'feedback':
                if current_time - self.state_start_time >= 3.0:  # 3 seconds feedback
                    # Rest period
                    self.state = 'rest'
                    self.state_start_time = current_time

            elif self.state == 'rest':
                if current_time - self.state_start_time >= 2.0:  # 2 seconds rest
                    # Next trial
                    self.current_trial += 1
                    if self.current_trial < self.num_trials:
                        self.state = 'get_ready'
                        self.state_start_time = current_time

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        score = self.calculate_score()
        self.save_data(score)
        return score

    def calculate_score(self):
        """Calculate test statistics"""
        if not self.results:
            return {}

        # Overall statistics
        mean_absolute_error = sum(r['absolute_error_s'] for r in self.results) / len(self.results)
        mean_percent_error = sum(r['percent_error'] for r in self.results) / len(self.results)

        # Calculate correlation and regression
        stimulus_durs = [r['stimulus_duration_s'] for r in self.results]
        reproduced_durs = [r['reproduced_duration_s'] for r in self.results]

        if len(stimulus_durs) > 1:
            # Calculate correlation
            mean_stim = sum(stimulus_durs) / len(stimulus_durs)
            mean_repro = sum(reproduced_durs) / len(reproduced_durs)

            numerator = sum((s - mean_stim) * (r - mean_repro) for s, r in zip(stimulus_durs, reproduced_durs))
            denom_s = sum((s - mean_stim) ** 2 for s in stimulus_durs) ** 0.5
            denom_r = sum((r - mean_repro) ** 2 for r in reproduced_durs) ** 0.5

            correlation = numerator / (denom_s * denom_r) if (denom_s * denom_r) > 0 else 0

            # Calculate regression slope and intercept
            if denom_s > 0:
                slope = numerator / (denom_s ** 2)
                intercept = mean_repro - slope * mean_stim
            else:
                slope = 0
                intercept = 0
        else:
            correlation = 0
            slope = 0
            intercept = 0

        score = {
            'total_trials': len(self.results),
            'mean_absolute_error_s': mean_absolute_error,
            'mean_percent_error': mean_percent_error,
            'correlation_stimulus_reproduction': correlation,
            'slope_regression': slope,
            'intercept_regression': intercept,
            'audio_available': self.audio_available,
            'trials': self.results
        }

        return score

    def save_data(self, score):
        """Save test data"""
        if not score:
            return

        data = {
            "test_type": "temporal_reproduction",
            **score
        }

        try:
            data_manager = DataManager()
            filepath = data_manager.save_test_data('temporal_reproduction', data)
            print(f"Temporal Reproduction test data saved to {filepath}")
        except Exception as e:
            print(f"Error saving Temporal Reproduction test data: {e}")

    def draw(self):
        """Draw the test UI"""
        self.screen.fill(self.WHITE)

        # Title
        title_text = self.font.render("Temporal Reproduction", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.x = 20
        title_rect.y = 20
        self.screen.blit(title_text, title_rect)

        # Trial counter
        trial_text = self.font.render(f"Trial: {self.current_trial + 1}/{self.num_trials}", True, self.BLACK)
        trial_rect = trial_text.get_rect()
        trial_rect.x = self.screen.get_width() - 200
        trial_rect.y = 20
        self.screen.blit(trial_text, trial_rect)

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        if not self.audio_available:
            # Warning if audio not available
            warning_text = self.font.render("Audio not available - test cannot run", True, (255, 0, 0))
            warning_rect = warning_text.get_rect()
            warning_rect.center = (center_x, center_y)
            self.screen.blit(warning_text, warning_rect)
            return

        if self.state == 'get_ready':
            ready_text = self.large_font.render("Get Ready...", True, self.BLUE)
            ready_rect = ready_text.get_rect()
            ready_rect.center = (center_x, center_y)
            self.screen.blit(ready_text, ready_rect)

        elif self.state == 'playing':
            # Show tone playing indicator
            playing_text = self.large_font.render("\u266A Tone Playing \u266A", True, self.BLUE)
            playing_rect = playing_text.get_rect()
            playing_rect.center = (center_x, center_y - 30)
            self.screen.blit(playing_text, playing_rect)

            instruction = self.small_font.render("Listen carefully to the duration", True, self.BLACK)
            instruction_rect = instruction.get_rect()
            instruction_rect.center = (center_x, center_y + 40)
            self.screen.blit(instruction, instruction_rect)

        elif self.state == 'pause':
            pause_text = self.font.render("...", True, self.BLACK)
            pause_rect = pause_text.get_rect()
            pause_rect.center = (center_x, center_y)
            self.screen.blit(pause_text, pause_rect)

        elif self.state == 'instructions':
            instruction1 = self.large_font.render("REPRODUCE", True, self.BLUE)
            instruction1_rect = instruction1.get_rect()
            instruction1_rect.center = (center_x, center_y - 40)
            self.screen.blit(instruction1, instruction1_rect)

            instruction2 = self.font.render("Press and HOLD SPACE", True, self.BLACK)
            instruction2_rect = instruction2.get_rect()
            instruction2_rect.center = (center_x, center_y + 20)
            self.screen.blit(instruction2, instruction2_rect)

            instruction3 = self.small_font.render("for the same duration as the tone", True, self.BLACK)
            instruction3_rect = instruction3.get_rect()
            instruction3_rect.center = (center_x, center_y + 50)
            self.screen.blit(instruction3, instruction3_rect)

        elif self.state == 'reproducing':
            # Do NOT show elapsed time (per user preference)
            repro_text = self.large_font.render("Reproducing...", True, self.GREEN)
            repro_rect = repro_text.get_rect()
            repro_rect.center = (center_x, center_y - 30)
            self.screen.blit(repro_text, repro_rect)

            instruction = self.small_font.render("Release SPACE when done", True, self.BLACK)
            instruction_rect = instruction.get_rect()
            instruction_rect.center = (center_x, center_y + 40)
            self.screen.blit(instruction, instruction_rect)

        elif self.state == 'feedback':
            # Show results
            if self.results:
                last_result = self.results[-1]

                stimulus_text = self.font.render(f"Stimulus: {last_result['stimulus_duration_s']:.1f}s", True, self.BLACK)
                stimulus_rect = stimulus_text.get_rect()
                stimulus_rect.center = (center_x, center_y - 70)
                self.screen.blit(stimulus_text, stimulus_rect)

                repro_text = self.font.render(f"Your reproduction: {last_result['reproduced_duration_s']:.1f}s", True, self.BLUE)
                repro_rect = repro_text.get_rect()
                repro_rect.center = (center_x, center_y - 20)
                self.screen.blit(repro_text, repro_rect)

                error_color = self.GREEN if abs(last_result['error_s']) < 2 else self.BLACK
                error_text = self.font.render(f"Error: {last_result['error_s']:+.1f}s ({last_result['percent_error']:+.1f}%)", True, error_color)
                error_rect = error_text.get_rect()
                error_rect.center = (center_x, center_y + 30)
                self.screen.blit(error_text, error_rect)

        elif self.state == 'rest':
            rest_text = self.font.render("Rest...", True, self.BLACK)
            rest_rect = rest_text.get_rect()
            rest_rect.center = (center_x, center_y)
            self.screen.blit(rest_text, rest_rect)

def run_temporal_reproduction(screen, font):
    """Module-level runner function"""
    test = TemporalReproductionTest(screen, font)
    return test.run()
