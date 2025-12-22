import pygame
import random
import time
from data_manager import DataManager

class TemporalProductionTest:
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

        # Test parameters
        self.durations = [30, 60, 90]
        self.trials_per_duration = 5
        self.trial_list = []
        self.current_trial = 0
        self.results = []

        # Generate trial list
        for duration in self.durations:
            for _ in range(self.trials_per_duration):
                self.trial_list.append(duration)
        random.shuffle(self.trial_list)

        # State management
        self.state = 'instructions'  # instructions, timing, feedback, rest
        self.target_duration = None
        self.start_time = None
        self.produced_duration = None
        self.rest_start_time = None

    def run(self):
        clock = pygame.time.Clock()

        while self.running and self.current_trial < len(self.trial_list):
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
                            # Start timing
                            self.target_duration = self.trial_list[self.current_trial]
                            self.start_time = current_time
                            self.state = 'timing'

                        elif self.state == 'timing':
                            # Stop timing
                            self.produced_duration = current_time - self.start_time
                            error = self.produced_duration - self.target_duration
                            percent_error = (error / self.target_duration) * 100

                            # Record result
                            trial_data = {
                                'trial_number': self.current_trial + 1,
                                'target_duration_s': self.target_duration,
                                'produced_duration_s': self.produced_duration,
                                'error_s': error,
                                'percent_error': percent_error,
                                'start_timestamp': self.start_time,
                                'end_timestamp': current_time
                            }
                            self.results.append(trial_data)

                            # Show feedback
                            self.state = 'feedback'

                        elif self.state == 'feedback':
                            # Move to rest period
                            self.state = 'rest'
                            self.rest_start_time = current_time

            # Auto-advance from rest to next trial
            if self.state == 'rest':
                if current_time - self.rest_start_time >= 2.0:  # 2 second rest
                    self.current_trial += 1
                    self.state = 'instructions'
                    self.produced_duration = None

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
        mean_percent_error = sum(abs(r['percent_error']) for r in self.results) / len(self.results)
        errors = [r['error_s'] for r in self.results]
        mean_error = sum(errors) / len(errors)

        # By duration
        by_duration = {}
        for duration in self.durations:
            duration_trials = [r for r in self.results if r['target_duration_s'] == duration]
            if duration_trials:
                produced_durations = [r['produced_duration_s'] for r in duration_trials]
                errors = [r['error_s'] for r in duration_trials]
                mean_produced = sum(produced_durations) / len(produced_durations)
                mean_error_dur = sum(errors) / len(errors)

                # Calculate coefficient of variation
                if mean_produced > 0:
                    std_dev = (sum((p - mean_produced) ** 2 for p in produced_durations) / len(produced_durations)) ** 0.5
                    cv = std_dev / mean_produced
                else:
                    cv = 0

                by_duration[f'{duration}s'] = {
                    'mean_produced_s': mean_produced,
                    'mean_error_s': mean_error_dur,
                    'coefficient_of_variation': cv,
                    'trial_count': len(duration_trials)
                }

        # Calculate overall variability
        all_produced = [r['produced_duration_s'] for r in self.results]
        overall_mean = sum(all_produced) / len(all_produced)
        overall_std = (sum((p - overall_mean) ** 2 for p in all_produced) / len(all_produced)) ** 0.5
        overall_cv = overall_std / overall_mean if overall_mean > 0 else 0

        score = {
            'total_trials': len(self.results),
            'mean_absolute_percent_error': mean_percent_error,
            'mean_error_s': mean_error,
            'overall_coefficient_of_variation': overall_cv,
            'by_duration': by_duration,
            'trials': self.results
        }

        return score

    def save_data(self, score):
        """Save test data"""
        if not score:
            return

        data = {
            "test_type": "temporal_production",
            **score
        }

        try:
            data_manager = DataManager()
            filepath = data_manager.save_test_data('temporal_production', data)
            print(f"Temporal Production test data saved to {filepath}")
        except Exception as e:
            print(f"Error saving Temporal Production test data: {e}")

    def draw(self):
        """Draw the test UI"""
        self.screen.fill(self.WHITE)

        # Title
        title_text = self.font.render("Temporal Production", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.x = 20
        title_rect.y = 20
        self.screen.blit(title_text, title_rect)

        # Trial counter
        trial_text = self.font.render(f"Trial: {self.current_trial + 1}/{len(self.trial_list)}", True, self.BLACK)
        trial_rect = trial_text.get_rect()
        trial_rect.x = self.screen.get_width() - 200
        trial_rect.y = 20
        self.screen.blit(trial_text, trial_rect)

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        if self.state == 'instructions':
            # Show instructions
            target_text = self.large_font.render(f"Target: {self.trial_list[self.current_trial]} seconds", True, self.BLUE)
            target_rect = target_text.get_rect()
            target_rect.center = (center_x, center_y - 60)
            self.screen.blit(target_text, target_rect)

            instruction1 = self.font.render("Press SPACE to START", True, self.BLACK)
            instruction1_rect = instruction1.get_rect()
            instruction1_rect.center = (center_x, center_y + 20)
            self.screen.blit(instruction1, instruction1_rect)

            instruction2 = self.small_font.render("Press SPACE again when you think the time has passed", True, self.BLACK)
            instruction2_rect = instruction2.get_rect()
            instruction2_rect.center = (center_x, center_y + 60)
            self.screen.blit(instruction2, instruction2_rect)

        elif self.state == 'timing':
            # Blank screen with minimal info
            timing_text = self.font.render("Timing...", True, self.BLUE)
            timing_rect = timing_text.get_rect()
            timing_rect.center = (center_x, center_y)
            self.screen.blit(timing_text, timing_rect)

            instruction = self.small_font.render("Press SPACE when you think the time is up", True, self.BLACK)
            instruction_rect = instruction.get_rect()
            instruction_rect.center = (center_x, center_y + 60)
            self.screen.blit(instruction, instruction_rect)

        elif self.state == 'feedback':
            # Show results
            target_text = self.font.render(f"Target: {self.target_duration}s", True, self.BLACK)
            target_rect = target_text.get_rect()
            target_rect.center = (center_x, center_y - 80)
            self.screen.blit(target_text, target_rect)

            produced_text = self.font.render(f"Your time: {self.produced_duration:.1f}s", True, self.BLUE)
            produced_rect = produced_text.get_rect()
            produced_rect.center = (center_x, center_y - 30)
            self.screen.blit(produced_text, produced_rect)

            error = self.produced_duration - self.target_duration
            error_color = self.GREEN if abs(error) < 3 else self.BLACK
            error_text = self.font.render(f"Error: {error:+.1f}s ({(error/self.target_duration)*100:+.1f}%)", True, error_color)
            error_rect = error_text.get_rect()
            error_rect.center = (center_x, center_y + 20)
            self.screen.blit(error_text, error_rect)

            continue_text = self.small_font.render("Press SPACE to continue", True, self.BLACK)
            continue_rect = continue_text.get_rect()
            continue_rect.center = (center_x, center_y + 80)
            self.screen.blit(continue_text, continue_rect)

        elif self.state == 'rest':
            # Brief rest period
            rest_text = self.font.render("Rest...", True, self.BLACK)
            rest_rect = rest_text.get_rect()
            rest_rect.center = (center_x, center_y)
            self.screen.blit(rest_text, rest_rect)

        # Previous trial result (bottom)
        if len(self.results) > 0 and self.state == 'instructions':
            prev_trial = self.results[-1]
            prev_text = self.small_font.render(
                f"Previous: {prev_trial['produced_duration_s']:.1f}s (target: {prev_trial['target_duration_s']}s)",
                True, self.BLACK
            )
            prev_rect = prev_text.get_rect()
            prev_rect.centerx = center_x
            prev_rect.y = self.screen.get_height() - 40
            self.screen.blit(prev_text, prev_rect)

def run_temporal_production(screen, font):
    """Module-level runner function"""
    test = TemporalProductionTest(screen, font)
    return test.run()
