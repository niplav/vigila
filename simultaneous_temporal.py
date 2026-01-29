import pygame
import random
import time
from data_manager import DataManager

class SimultaneousTemporalTest:
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
        self.RED = (220, 50, 50)

        # Test parameters
        self.num_trials = 4  # 4 trials instead of 3-5
        self.target_duration = 30  # Always 30 seconds
        self.current_trial = 0
        self.results = []

        # State management
        self.state = 'instructions'  # instructions, dual_task, feedback, rest
        self.trial_start_time = None
        self.trial_end_time = None

        # Subtraction task state
        self.starting_number = None
        self.current_number = None
        self.current_input = ""
        self.subtractions = []
        self.subtraction_count = 0

    def _start_trial(self):
        """Start a new trial"""
        # Generate random 3-digit starting number
        self.starting_number = random.randint(800, 999)
        self.current_number = self.starting_number
        self.current_input = ""
        self.subtractions = []
        self.subtraction_count = 0
        self.trial_start_time = time.time()
        self.state = 'dual_task'

    def run(self):
        clock = pygame.time.Clock()

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
                            # Start trial
                            self._start_trial()

                        elif self.state == 'dual_task':
                            # User signals 30s elapsed
                            self.trial_end_time = current_time
                            elapsed_time = self.trial_end_time - self.trial_start_time
                            time_error = elapsed_time - self.target_duration
                            percent_error = (time_error / self.target_duration) * 100

                            # Calculate subtraction accuracy
                            correct_subtractions = sum(1 for s in self.subtractions if s['correct'])
                            subtraction_accuracy = correct_subtractions / len(self.subtractions) if self.subtractions else 0

                            # Calculate mean subtraction interval
                            if len(self.subtractions) > 1:
                                intervals = []
                                for i in range(1, len(self.subtractions)):
                                    interval = self.subtractions[i]['timestamp'] - self.subtractions[i-1]['timestamp']
                                    intervals.append(interval)
                                mean_interval = sum(intervals) / len(intervals)
                            else:
                                mean_interval = 0

                            # Record result
                            trial_data = {
                                'trial_number': self.current_trial + 1,
                                'target_duration_s': self.target_duration,
                                'estimated_duration_s': elapsed_time,
                                'time_error_s': time_error,
                                'time_percent_error': percent_error,
                                'starting_number': self.starting_number,
                                'subtractions': self.subtractions.copy(),
                                'total_subtractions': len(self.subtractions),
                                'correct_subtractions': correct_subtractions,
                                'subtraction_accuracy': subtraction_accuracy,
                                'mean_subtraction_interval_s': mean_interval
                            }
                            self.results.append(trial_data)

                            self.state = 'feedback'

                        elif self.state == 'feedback':
                            # Move to rest or next trial
                            self.current_trial += 1
                            if self.current_trial < self.num_trials:
                                self.state = 'rest'
                                self.rest_start_time = current_time
                            else:
                                self.running = False

                    # Handle number input during dual task
                    elif self.state == 'dual_task':
                        if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                            digit = str(event.key - pygame.K_0)
                            if len(self.current_input) < 3:
                                self.current_input += digit

                        elif event.key == pygame.K_BACKSPACE:
                            if self.current_input:
                                self.current_input = self.current_input[:-1]

                        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            if self.current_input:
                                # Process subtraction
                                entered_number = int(self.current_input)
                                expected_number = self.current_number - 7
                                correct = (entered_number == expected_number)

                                subtraction_data = {
                                    'sequence_number': len(self.subtractions) + 1,
                                    'previous_number': self.current_number,
                                    'expected': expected_number,
                                    'entered': entered_number,
                                    'correct': correct,
                                    'timestamp': current_time
                                }
                                self.subtractions.append(subtraction_data)

                                # Move to next number (use entered number, not expected)
                                # This allows continuation even if they make an error
                                self.current_number = entered_number
                                self.current_input = ""

            # Auto-advance from rest
            if self.state == 'rest':
                if current_time - self.rest_start_time >= 2.0:  # 2 second rest
                    self.state = 'instructions'

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

        # Time estimation statistics
        time_errors = [r['time_error_s'] for r in self.results]
        mean_time_error = sum(time_errors) / len(time_errors)
        abs_time_errors = [abs(e) for e in time_errors]
        mean_abs_time_error = sum(abs_time_errors) / len(abs_time_errors)

        # Subtraction statistics
        all_subtractions = sum(r['total_subtractions'] for r in self.results)
        all_correct = sum(r['correct_subtractions'] for r in self.results)
        overall_subtraction_accuracy = all_correct / all_subtractions if all_subtractions > 0 else 0

        mean_subtractions_per_trial = all_subtractions / len(self.results)

        # Calculate time variability
        if len(time_errors) > 1:
            mean_te = sum(time_errors) / len(time_errors)
            variance = sum((e - mean_te) ** 2 for e in time_errors) / len(time_errors)
            time_variability = variance ** 0.5
        else:
            time_variability = 0

        score = {
            'total_trials': len(self.results),
            'target_duration_s': self.target_duration,
            'mean_time_error_s': mean_time_error,
            'mean_absolute_time_error_s': mean_abs_time_error,
            'time_variability_s': time_variability,
            'mean_subtractions_per_trial': mean_subtractions_per_trial,
            'overall_subtraction_accuracy': overall_subtraction_accuracy,
            'total_subtractions': all_subtractions,
            'total_correct_subtractions': all_correct,
            'trials': self.results
        }

        return score

    def save_data(self, score):
        """Save test data"""
        if not score:
            return

        data = {
            "test_type": "simultaneous_temporal_processing",
            **score
        }

        try:
            data_manager = DataManager()
            filepath = data_manager.save_test_data('simultaneous_temporal', data)
            print(f"Simultaneous Temporal Processing test data saved to {filepath}")
        except Exception as e:
            print(f"Error saving Simultaneous Temporal Processing test data: {e}")

    def draw(self):
        """Draw the test UI"""
        self.screen.fill(self.WHITE)

        # Title
        title_text = self.font.render("Simultaneous Temporal Processing", True, self.BLACK)
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

        if self.state == 'instructions':
            instruction1 = self.large_font.render("Dual Task", True, self.BLUE)
            instruction1_rect = instruction1.get_rect()
            instruction1_rect.center = (center_x, center_y - 100)
            self.screen.blit(instruction1, instruction1_rect)

            instruction2 = self.font.render("1. Estimate when 30 seconds have passed", True, self.BLACK)
            instruction2_rect = instruction2.get_rect()
            instruction2_rect.center = (center_x, center_y - 30)
            self.screen.blit(instruction2, instruction2_rect)

            instruction3 = self.font.render("2. WHILE doing serial 7s subtraction", True, self.BLACK)
            instruction3_rect = instruction3.get_rect()
            instruction3_rect.center = (center_x, center_y + 10)
            self.screen.blit(instruction3, instruction3_rect)

            instruction4 = self.small_font.render("Type 3-digit answers, press ENTER to submit", True, self.BLACK)
            instruction4_rect = instruction4.get_rect()
            instruction4_rect.center = (center_x, center_y + 60)
            self.screen.blit(instruction4, instruction4_rect)

            instruction5 = self.small_font.render("Press SPACE when you think 30 seconds have elapsed", True, self.BLUE)
            instruction5_rect = instruction5.get_rect()
            instruction5_rect.center = (center_x, center_y + 90)
            self.screen.blit(instruction5, instruction5_rect)

            start_text = self.small_font.render("Press SPACE to start", True, self.BLUE)
            start_rect = start_text.get_rect()
            start_rect.center = (center_x, center_y + 130)
            self.screen.blit(start_text, start_rect)

        elif self.state == 'dual_task':
            # Show current number
            number_text = self.large_font.render(str(self.current_number), True, self.BLACK)
            number_rect = number_text.get_rect()
            number_rect.center = (center_x, center_y - 80)
            self.screen.blit(number_text, number_rect)

            # Show input prompt
            prompt_text = self.font.render("Subtract 7:", True, self.BLACK)
            prompt_rect = prompt_text.get_rect()
            prompt_rect.center = (center_x - 100, center_y)
            self.screen.blit(prompt_text, prompt_rect)

            # Show current input
            input_display = self.current_input + "_" * (3 - len(self.current_input))
            input_text = self.large_font.render(input_display, True, self.BLUE)
            input_rect = input_text.get_rect()
            input_rect.center = (center_x + 70, center_y)
            self.screen.blit(input_text, input_rect)

            # Show subtraction count
            count_text = self.small_font.render(f"Subtractions completed: {len(self.subtractions)}", True, self.BLACK)
            count_rect = count_text.get_rect()
            count_rect.center = (center_x, center_y + 70)
            self.screen.blit(count_text, count_rect)

            # Show last result
            if self.subtractions:
                last_sub = self.subtractions[-1]
                if last_sub['correct']:
                    result_color = self.GREEN
                    result_text_str = "\u2713 Correct"
                else:
                    result_color = self.RED
                    result_text_str = f"\u2717 Wrong (expected {last_sub['expected']})"

                result_text = self.small_font.render(result_text_str, True, result_color)
                result_rect = result_text.get_rect()
                result_rect.center = (center_x, center_y + 100)
                self.screen.blit(result_text, result_rect)

            # Instruction
            instruction = self.small_font.render("Press SPACE when 30 seconds have elapsed", True, self.BLUE)
            instruction_rect = instruction.get_rect()
            instruction_rect.center = (center_x, self.screen.get_height() - 60)
            self.screen.blit(instruction, instruction_rect)

            # ESC to quit
            esc_text = self.small_font.render("ESC to quit", True, self.BLACK)
            esc_rect = esc_text.get_rect()
            esc_rect.center = (center_x, self.screen.get_height() - 30)
            self.screen.blit(esc_text, esc_rect)

        elif self.state == 'feedback':
            if self.results:
                last_result = self.results[-1]

                # Show time estimation results
                time_text = self.large_font.render(f"{last_result['estimated_duration_s']:.1f}s", True, self.BLUE)
                time_rect = time_text.get_rect()
                time_rect.center = (center_x, center_y - 100)
                self.screen.blit(time_text, time_rect)

                target_text = self.font.render(f"Target: {last_result['target_duration_s']}s", True, self.BLACK)
                target_rect = target_text.get_rect()
                target_rect.center = (center_x, center_y - 50)
                self.screen.blit(target_text, target_rect)

                error_color = self.GREEN if abs(last_result['time_error_s']) < 5 else self.BLACK
                error_text = self.font.render(
                    f"Error: {last_result['time_error_s']:+.1f}s ({last_result['time_percent_error']:+.1f}%)",
                    True, error_color
                )
                error_rect = error_text.get_rect()
                error_rect.center = (center_x, center_y - 10)
                self.screen.blit(error_text, error_rect)

                # Show subtraction results
                sub_text = self.font.render(
                    f"Subtractions: {last_result['correct_subtractions']}/{last_result['total_subtractions']} " +
                    f"({last_result['subtraction_accuracy']*100:.0f}%)",
                    True, self.BLACK
                )
                sub_rect = sub_text.get_rect()
                sub_rect.center = (center_x, center_y + 40)
                self.screen.blit(sub_text, sub_rect)

                # Continue
                continue_text = self.small_font.render("Press SPACE to continue", True, self.BLACK)
                continue_rect = continue_text.get_rect()
                continue_rect.center = (center_x, center_y + 100)
                self.screen.blit(continue_text, continue_rect)

        elif self.state == 'rest':
            rest_text = self.font.render("Rest...", True, self.BLACK)
            rest_rect = rest_text.get_rect()
            rest_rect.center = (center_x, center_y)
            self.screen.blit(rest_text, rest_rect)

def run_simultaneous_temporal(screen, font):
    """Module-level runner function"""
    test = SimultaneousTemporalTest(screen, font)
    return test.run()
