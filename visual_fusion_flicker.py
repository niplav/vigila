import pygame
import time
import math
from data_manager import DataManager

class VisualFusionFlickerTest:
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

        # Flicker parameters
        self.start_frequency = 5.0  # Hz
        self.max_frequency = 60.0  # Hz (capped at 60 for safety)
        self.frequency_increase_rate = 1.0  # Hz per second
        self.current_frequency = self.start_frequency

        # State management
        self.state = 'instructions'  # instructions, flickering, result, rest
        self.trial_start_time = None
        self.flicker_time = 0  # Continuous time for sinusoidal flicker
        self.detected_frequency = None
        self.detection_time = None

    def run(self):
        clock = pygame.time.Clock()

        while self.running and self.current_trial < self.max_trials:
            current_time = time.time()
            dt = clock.get_time() / 1000.0  # Delta time in seconds

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
                            # Start trial
                            self.state = 'flickering'
                            self.trial_start_time = current_time
                            self.current_frequency = self.start_frequency
                            self.flicker_time = 0

                        elif self.state == 'flickering':
                            # User detected fusion
                            self.detected_frequency = self.current_frequency
                            self.detection_time = current_time - self.trial_start_time

                            trial_data = {
                                'trial_number': self.current_trial + 1,
                                'threshold_hz': self.detected_frequency,
                                'detection_time_s': self.detection_time,
                                'discarded': False,
                                'timestamp': current_time
                            }
                            self.valid_trials.append(trial_data)

                            self.state = 'result'

                        elif self.state == 'result':
                            # Move to rest
                            self.state = 'rest'
                            self.rest_start_time = current_time
                            self.current_trial += 1

                    elif event.key == pygame.K_r:
                        if self.state == 'flickering':
                            # Restart/discard trial
                            trial_data = {
                                'trial_number': self.current_trial + 1,
                                'threshold_hz': self.current_frequency,
                                'detection_time_s': current_time - self.trial_start_time,
                                'discarded': True,
                                'timestamp': current_time
                            }
                            self.discarded_trials.append(trial_data)

                            # Restart trial (don't increment counter)
                            self.state = 'instructions'

            # Update flicker
            if self.state == 'flickering':
                # Increase frequency over time
                elapsed = current_time - self.trial_start_time
                self.current_frequency = min(
                    self.start_frequency + (self.frequency_increase_rate * elapsed),
                    self.max_frequency
                )

                # Update continuous flicker time for sinusoidal modulation
                self.flicker_time += dt

                # Auto-end if we reach max frequency
                if self.current_frequency >= self.max_frequency:
                    # Consider this a failed trial
                    trial_data = {
                        'trial_number': self.current_trial + 1,
                        'threshold_hz': self.max_frequency,
                        'detection_time_s': current_time - self.trial_start_time,
                        'discarded': True,
                        'timestamp': current_time,
                        'reason': 'max_frequency_reached'
                    }
                    self.discarded_trials.append(trial_data)
                    self.state = 'instructions'

            # Auto-advance from rest
            if self.state == 'rest':
                if current_time - self.rest_start_time >= 2.0:  # 2 second rest
                    self.state = 'instructions'

            # Check if we have enough valid trials
            if len(self.valid_trials) >= self.min_trials and self.state == 'instructions':
                if self.current_trial >= self.min_trials:
                    # We can end the test
                    break

            self.draw()
            pygame.display.flip()
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

        # Calculate standard deviation
        if len(thresholds) > 1:
            variance = sum((t - mean_threshold) ** 2 for t in thresholds) / len(thresholds)
            std_threshold = variance ** 0.5
        else:
            std_threshold = 0

        score = {
            'test_type': 'visual_fusion_flicker',
            'mean_threshold_hz': mean_threshold,
            'std_threshold_hz': std_threshold,
            'valid_trials': len(self.valid_trials),
            'discarded_trials': len(self.discarded_trials),
            'trials': self.valid_trials,
            'discarded': self.discarded_trials
        }

        return score

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
        self.screen.fill(self.WHITE)

        # Title
        title_text = self.font.render("Visual Fusion Flicker Frequency", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.x = 20
        title_rect.y = 20
        self.screen.blit(title_text, title_rect)

        # Trial counter
        trial_text = self.small_font.render(
            f"Trial: {self.current_trial + 1}  |  Valid: {len(self.valid_trials)}/{self.min_trials}",
            True, self.BLACK
        )
        trial_rect = trial_text.get_rect()
        trial_rect.x = self.screen.get_width() - 280
        trial_rect.y = 20
        self.screen.blit(trial_text, trial_rect)

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        if self.state == 'instructions':
            instruction1 = self.large_font.render("Ready", True, self.BLUE)
            instruction1_rect = instruction1.get_rect()
            instruction1_rect.center = (center_x, center_y - 80)
            self.screen.blit(instruction1, instruction1_rect)

            instruction2 = self.font.render("A square will flicker at increasing speed", True, self.BLACK)
            instruction2_rect = instruction2.get_rect()
            instruction2_rect.center = (center_x, center_y - 10)
            self.screen.blit(instruction2, instruction2_rect)

            instruction3 = self.font.render("Press SPACE when it appears SOLID (fused)", True, self.BLACK)
            instruction3_rect = instruction3.get_rect()
            instruction3_rect.center = (center_x, center_y + 30)
            self.screen.blit(instruction3, instruction3_rect)

            start_text = self.small_font.render("Press SPACE to start", True, self.BLUE)
            start_rect = start_text.get_rect()
            start_rect.center = (center_x, center_y + 80)
            self.screen.blit(start_text, start_rect)

        elif self.state == 'flickering':
            # Draw flickering square with sinusoidal brightness
            square_size = 300
            square_rect = pygame.Rect(0, 0, square_size, square_size)
            square_rect.center = (center_x, center_y - 30)

            # Calculate sinusoidal brightness (0 to 1)
            brightness = (math.sin(2 * math.pi * self.current_frequency * self.flicker_time) + 1) / 2
            # Convert to grayscale color (0-255)
            gray_value = int(brightness * 255)
            square_color = (gray_value, gray_value, gray_value)

            pygame.draw.rect(self.screen, square_color, square_rect)
            pygame.draw.rect(self.screen, self.GRAY, square_rect, 2)  # Border

            # Instructions
            instruction = self.small_font.render("Press SPACE when it looks SOLID", True, self.BLACK)
            instruction_rect = instruction.get_rect()
            instruction_rect.center = (center_x, center_y + 220)
            self.screen.blit(instruction, instruction_rect)

            # Restart button indicator
            restart_button = pygame.Rect(center_x - 100, center_y + 250, 200, 40)
            pygame.draw.rect(self.screen, self.RED, restart_button)
            restart_text = self.small_font.render("Press R to Restart", True, self.WHITE)
            restart_text_rect = restart_text.get_rect()
            restart_text_rect.center = restart_button.center
            self.screen.blit(restart_text, restart_text_rect)

        elif self.state == 'result':
            result_text = self.large_font.render(f"{self.detected_frequency:.1f} Hz", True, self.BLUE)
            result_rect = result_text.get_rect()
            result_rect.center = (center_x, center_y - 40)
            self.screen.blit(result_text, result_rect)

            detection_text = self.font.render(f"Detection time: {self.detection_time:.1f}s", True, self.BLACK)
            detection_rect = detection_text.get_rect()
            detection_rect.center = (center_x, center_y + 20)
            self.screen.blit(detection_text, detection_rect)

            continue_text = self.small_font.render("Press SPACE to continue", True, self.BLACK)
            continue_rect = continue_text.get_rect()
            continue_rect.center = (center_x, center_y + 70)
            self.screen.blit(continue_text, continue_rect)

        elif self.state == 'rest':
            rest_text = self.font.render("Rest...", True, self.BLACK)
            rest_rect = rest_text.get_rect()
            rest_rect.center = (center_x, center_y)
            self.screen.blit(rest_text, rest_rect)

        # Show statistics if we have valid trials
        if len(self.valid_trials) > 0 and self.state in ['instructions', 'rest']:
            thresholds = [t['threshold_hz'] for t in self.valid_trials]
            mean_threshold = sum(thresholds) / len(thresholds)

            stats_text = self.small_font.render(
                f"Mean threshold: {mean_threshold:.1f} Hz (n={len(self.valid_trials)})",
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
