import pygame
import random
import time
import json
import os
from datetime import datetime

class DigitSpanTest:
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
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (128, 128, 128)

        # Test parameters
        self.current_span = 3  # Start with 3 digits
        self.max_span = 9
        self.trials_per_span = 2
        self.current_trial = 0
        self.forward_span = 0
        self.backward_span = 0
        self.testing_forward = True

        # Current test state
        self.current_sequence = []
        self.user_input = []
        self.phase = "instructions"  # instructions, showing, input, feedback
        self.sequence_index = 0
        self.digit_display_time = 1.0  # 1 second per digit
        self.digit_start_time = 0
        self.feedback_start_time = 0
        self.feedback_duration = 1.5
        self.last_correct = False
        self.consecutive_failures = 0

        # Results tracking
        self.results = {
            'forward_trials': [],
            'backward_trials': []
        }

        self.generate_sequence()

    def generate_sequence(self):
        """Generate a random sequence of digits"""
        self.current_sequence = [random.randint(0, 9) for _ in range(self.current_span)]
        self.user_input = []
        self.sequence_index = 0

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return self.calculate_final_score()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return self.calculate_final_score()

                    elif self.phase == "instructions":
                        if event.key == pygame.K_SPACE:
                            self.phase = "showing"
                            self.sequence_index = 0
                            self.digit_start_time = current_time

                    elif self.phase == "input":
                        if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                            digit = event.key - pygame.K_0
                            self.user_input.append(digit)

                            # Check if input is complete
                            if len(self.user_input) >= self.current_span:
                                self.check_answer()
                                self.phase = "feedback"
                                self.feedback_start_time = current_time

                        elif event.key == pygame.K_BACKSPACE:
                            if self.user_input:
                                self.user_input.pop()

                        elif event.key == pygame.K_RETURN:
                            if self.user_input:
                                # Pad with zeros if needed
                                while len(self.user_input) < self.current_span:
                                    self.user_input.append(0)
                                self.check_answer()
                                self.phase = "feedback"
                                self.feedback_start_time = current_time

                    elif self.phase == "feedback":
                        if event.key == pygame.K_SPACE:
                            self.next_trial()

            # Handle automatic phase transitions
            if self.phase == "showing":
                if current_time - self.digit_start_time >= self.digit_display_time:
                    self.sequence_index += 1
                    if self.sequence_index >= len(self.current_sequence):
                        self.phase = "input"
                    else:
                        self.digit_start_time = current_time

            elif self.phase == "feedback":
                if current_time - self.feedback_start_time >= self.feedback_duration:
                    self.next_trial()

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        score = self.calculate_final_score()
        self.save_data(score)
        return score

    def check_answer(self):
        """Check if the user's answer is correct"""
        if self.testing_forward:
            correct_sequence = self.current_sequence
        else:
            correct_sequence = self.current_sequence[::-1]  # Reverse for backward span

        self.last_correct = self.user_input == correct_sequence

        # Record the trial
        trial_data = {
            'span': self.current_span,
            'sequence': self.current_sequence.copy(),
            'user_input': self.user_input.copy(),
            'correct': self.last_correct,
            'forward': self.testing_forward
        }

        if self.testing_forward:
            self.results['forward_trials'].append(trial_data)
        else:
            self.results['backward_trials'].append(trial_data)

    def next_trial(self):
        """Move to the next trial"""
        self.current_trial += 1

        if self.last_correct:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1

        # Check if we need to change span length
        if self.current_trial >= self.trials_per_span:
            self.current_trial = 0

            # If got at least one correct, move to next span
            if self.testing_forward:
                trials_this_span = [t for t in self.results['forward_trials'] if t['span'] == self.current_span]
            else:
                trials_this_span = [t for t in self.results['backward_trials'] if t['span'] == self.current_span]

            got_one_correct = any(t['correct'] for t in trials_this_span)

            if got_one_correct:
                if self.testing_forward:
                    self.forward_span = self.current_span
                else:
                    self.backward_span = self.current_span

                self.current_span += 1

                if self.current_span > self.max_span:
                    if self.testing_forward:
                        # Switch to backward testing
                        self.testing_forward = False
                        self.current_span = 3
                        self.consecutive_failures = 0
                    else:
                        # Test complete
                        self.running = False
                        return
            else:
                # Failed both trials at this span
                if self.testing_forward:
                    # Switch to backward testing
                    self.testing_forward = False
                    self.current_span = 3
                    self.consecutive_failures = 0
                else:
                    # Test complete
                    self.running = False
                    return

        # Generate new sequence
        self.generate_sequence()
        self.phase = "instructions"

    def draw(self):
        self.screen.fill(self.WHITE)

        # Title
        title = "Forward Digit Span" if self.testing_forward else "Backward Digit Span"
        title_text = self.font.render(title, True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen.get_width() // 2
        title_rect.y = 20
        self.screen.blit(title_text, title_rect)

        # Current span info
        span_text = self.small_font.render(f"Span: {self.current_span} | Trial: {self.current_trial + 1}/{self.trials_per_span}", True, self.BLACK)
        span_rect = span_text.get_rect()
        span_rect.x = 20
        span_rect.y = 20
        self.screen.blit(span_text, span_rect)

        # Scores
        score_text = self.small_font.render(f"Forward: {self.forward_span} | Backward: {self.backward_span}", True, self.BLACK)
        score_rect = score_text.get_rect()
        score_rect.x = self.screen.get_width() - 200
        score_rect.y = 20
        self.screen.blit(score_text, score_rect)

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        if self.phase == "instructions":
            instructions = [
                "You will see a sequence of digits.",
                "Remember them in order.",
                ""
            ]

            if self.testing_forward:
                instructions.append("Type them back in the SAME order.")
            else:
                instructions.append("Type them back in REVERSE order.")

            instructions.extend([
                "",
                "Press SPACE to start",
                "BACKSPACE to delete, ENTER to submit",
                "ESC to quit"
            ])

            for i, instruction in enumerate(instructions):
                text = self.font.render(instruction, True, self.BLACK)
                text_rect = text.get_rect()
                text_rect.centerx = center_x
                text_rect.y = center_y - 100 + i * 30
                self.screen.blit(text, text_rect)

        elif self.phase == "showing":
            # Show current digit
            if self.sequence_index < len(self.current_sequence):
                digit = str(self.current_sequence[self.sequence_index])
                digit_text = self.large_font.render(digit, True, self.BLACK)
                digit_rect = digit_text.get_rect()
                digit_rect.center = (center_x, center_y)
                self.screen.blit(digit_text, digit_rect)

                # Progress indicator
                progress_text = self.small_font.render(f"{self.sequence_index + 1}/{len(self.current_sequence)}", True, self.GRAY)
                progress_rect = progress_text.get_rect()
                progress_rect.centerx = center_x
                progress_rect.y = center_y + 60
                self.screen.blit(progress_text, progress_rect)

        elif self.phase == "input":
            # Show input prompt
            direction = "forward" if self.testing_forward else "backward"
            prompt_text = self.font.render(f"Enter digits in {direction} order:", True, self.BLACK)
            prompt_rect = prompt_text.get_rect()
            prompt_rect.centerx = center_x
            prompt_rect.y = center_y - 60
            self.screen.blit(prompt_text, prompt_rect)

            # Show user input
            input_str = " ".join(str(d) for d in self.user_input)
            if len(input_str) == 0:
                input_str = "_"
            input_text = self.large_font.render(input_str, True, self.BLACK)
            input_rect = input_text.get_rect()
            input_rect.centerx = center_x
            input_rect.y = center_y
            self.screen.blit(input_text, input_rect)

            # Show expected length
            length_text = self.small_font.render(f"Expected length: {self.current_span}", True, self.GRAY)
            length_rect = length_text.get_rect()
            length_rect.centerx = center_x
            length_rect.y = center_y + 60
            self.screen.blit(length_text, length_rect)

        elif self.phase == "feedback":
            # Show result
            if self.last_correct:
                result_text = self.font.render("Correct!", True, self.GREEN)
            else:
                result_text = self.font.render("Incorrect", True, self.RED)
            result_rect = result_text.get_rect()
            result_rect.centerx = center_x
            result_rect.y = center_y - 60
            self.screen.blit(result_text, result_rect)

            # Show correct answer
            if self.testing_forward:
                correct_sequence = self.current_sequence
            else:
                correct_sequence = self.current_sequence[::-1]

            correct_str = " ".join(str(d) for d in correct_sequence)
            correct_text = self.font.render(f"Correct: {correct_str}", True, self.BLACK)
            correct_rect = correct_text.get_rect()
            correct_rect.centerx = center_x
            correct_rect.y = center_y - 20
            self.screen.blit(correct_text, correct_rect)

            # Show user answer
            user_str = " ".join(str(d) for d in self.user_input)
            user_text = self.font.render(f"Your answer: {user_str}", True, self.BLACK)
            user_rect = user_text.get_rect()
            user_rect.centerx = center_x
            user_rect.y = center_y + 20
            self.screen.blit(user_text, user_rect)

            # Next trial prompt
            next_text = self.small_font.render("Press SPACE to continue", True, self.GRAY)
            next_rect = next_text.get_rect()
            next_rect.centerx = center_x
            next_rect.y = center_y + 80
            self.screen.blit(next_text, next_rect)

    def calculate_final_score(self):
        """Calculate the final digit span scores"""
        return {
            'forward_span': self.forward_span,
            'backward_span': self.backward_span,
            'total_span': self.forward_span + self.backward_span,
            'forward_trials': len(self.results['forward_trials']),
            'backward_trials': len(self.results['backward_trials'])
        }

    def save_data(self, score):
        """Save test results to JSON file"""
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"digit_span_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)

        # Prepare data
        data = {
            "test_type": "digit_span",
            "timestamp": datetime.now().isoformat(),
            "forward_span": score['forward_span'],
            "backward_span": score['backward_span'],
            "total_span": score['total_span'],
            "forward_trials": self.results['forward_trials'],
            "backward_trials": self.results['backward_trials']
        }

        # Save to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Digit span data saved to {filepath}")

def run_digit_span(screen, font):
    digit_span = DigitSpanTest(screen, font)
    return digit_span.run()