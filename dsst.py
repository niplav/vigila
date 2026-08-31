import pygame
import random
import time
from data_manager import DataManager

class DigitSymbolSubstitutionTest:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        self.running = True
        self.test_duration = 90  # seconds
        self.start_time = None
        self.current_symbols = []
        self.current_responses = []
        self.current_position = 0
        self.total_completed = 0
        self.correct_count = 0

        # New tracking for response times and error patterns
        self.response_times = []  # List of response times in seconds
        self.error_patterns = []  # List of (expected_symbol, entered_digit, correct_digit) tuples
        self.symbol_start_time = None  # Time when current symbol was presented
        self.response_count = 0  # Total responses recorded (for backspace tracking)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)

        self.symbol_map = {}
        symbols=['-', 'T', '#', 'O', 'H', 'L', '^', 'X', '=']
        random.shuffle(symbols)
        for i in range(1, 10):
            self.symbol_map[i]=symbols[i-1]

        # Generate first set of symbols
        self.generate_new_symbols()

    def generate_new_symbols(self):
        """Generate 6 random symbols for the current round"""
        self.current_symbols = [self.symbol_map[random.randint(1, 9)] for _ in range(6)]
        self.current_responses = [None] * 6
        self.current_position = 0
        self.symbol_start_time = time.time()  # Start timing for first symbol

    def run(self):
        clock = pygame.time.Clock()
        self.start_time = time.time()

        while self.running:
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            # Check if time is up
            if elapsed_time >= self.test_duration:
                self.running = False
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        break

                    # Handle digit input
                    elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                        digit_key = event.key - pygame.K_0
                        if digit_key in self.symbol_map and self.current_position < 6:
                            # Record response time
                            response_time = time.time() - self.symbol_start_time
                            self.response_times.append(response_time)
                            self.response_count += 1

                            # Record the response
                            self.current_responses[self.current_position] = digit_key

                            # Check if correct and track error patterns
                            current_symbol = self.current_symbols[self.current_position]
                            correct_digit = None
                            for d, s in self.symbol_map.items():
                                if s == current_symbol:
                                    correct_digit = d
                                    break

                            if self.symbol_map[digit_key] == current_symbol:
                                self.correct_count += 1
                            else:
                                # Record error pattern: (expected_symbol, entered_digit, correct_digit)
                                self.error_patterns.append((current_symbol, digit_key, correct_digit))

                            self.current_position += 1

                            # Start timing for next symbol (if not at end)
                            if self.current_position < 6:
                                self.symbol_start_time = time.time()

                            # If all 6 are filled, generate new symbols
                            if self.current_position >= 6:
                                self.total_completed += 6
                                self.generate_new_symbols()

                    # Allow backspace to go back
                    elif event.key == pygame.K_BACKSPACE:
                        if self.current_position > 0:
                            self.current_position -= 1

                            # Only remove data if there was actually a response at this position
                            if self.current_responses[self.current_position] is not None:
                                # Check if it was correct before removing
                                current_symbol = self.current_symbols[self.current_position]
                                was_correct = (self.symbol_map[self.current_responses[self.current_position]] == current_symbol)

                                # Clear the response
                                self.current_responses[self.current_position] = None

                                # Remove the corresponding response time
                                if self.response_times and self.response_count > 0:
                                    self.response_times.pop()
                                    self.response_count -= 1

                                # Adjust correct count if this was correct
                                if was_correct:
                                    self.correct_count -= 1
                                else:
                                    # Remove the corresponding error pattern
                                    if self.error_patterns:
                                        self.error_patterns.pop()

                            # Restart timing for current symbol
                            self.symbol_start_time = time.time()

            self.draw(elapsed_time)
            pygame.display.flip()
            clock.tick(60)

        score = self.calculate_score()
        self.save_data(score)
        return score

    def draw(self, elapsed_time):
        self.screen.fill(self.WHITE)

        # Title
        title_text = self.font.render("Digit Symbol Substitution Test", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen.get_width() // 2
        title_rect.y = 10
        self.screen.blit(title_text, title_rect)

        # Time remaining and score
        time_left = max(0, self.test_duration - elapsed_time)
        time_text = self.font.render(f"Time: {time_left:.1f}s", True, self.BLACK)
        time_rect = time_text.get_rect()
        time_rect.right = self.screen.get_width() - 20
        time_rect.y = 10
        self.screen.blit(time_text, time_rect)

        score_text = self.font.render(f"Score: {self.correct_count}/{self.total_completed}", True, self.BLACK)
        score_rect = score_text.get_rect()
        score_rect.x = 20
        score_rect.y = 10
        self.screen.blit(score_text, score_rect)

        # Current symbols (middle of screen)
        symbols_y = self.screen.get_height() // 2 - 30
        symbol_width = 80
        start_x = self.screen.get_width() // 2 - (6 * symbol_width) // 2

        for i, symbol in enumerate(self.current_symbols):
            x = start_x + i * symbol_width

            # Highlight current position
            if i == self.current_position:
                pygame.draw.rect(self.screen, self.BLUE, (x-5, symbols_y-5, symbol_width-10, 60), 3)

            # Draw symbol
            symbol_text = self.large_font.render(symbol, True, self.BLACK)
            symbol_rect = symbol_text.get_rect()
            symbol_rect.centerx = x + symbol_width // 2
            symbol_rect.y = symbols_y
            self.screen.blit(symbol_text, symbol_rect)

            # Draw user response if any
            if self.current_responses[i] is not None:
                response_color = self.BLACK
                if symbol == self.symbol_map[self.current_responses[i]]:
                    response_color = self.GREEN
                else:
                    response_color = self.RED

                digit_text = self.font.render(str(self.current_responses[i]), True, response_color)
                digit_rect = digit_text.get_rect()
                digit_rect.centerx = x + symbol_width // 2
                digit_rect.y = symbols_y + 40
                self.screen.blit(digit_text, digit_rect)

        # Symbol reference (bottom of screen)
        ref_y = self.screen.get_height() - 120
        ref_text = self.small_font.render("Reference (Symbol above, Key below):", True, self.BLACK)
        ref_rect = ref_text.get_rect()
        ref_rect.centerx = self.screen.get_width() // 2
        ref_rect.y = ref_y
        self.screen.blit(ref_text, ref_rect)

        # Draw reference pairs
        ref_start_x = self.screen.get_width() // 2 - (9 * 70) // 2
        for i, (digit, symbol) in enumerate(self.symbol_map.items()):
            x = ref_start_x + i * 70
            y = ref_y + 25

            # Draw symbol
            symbol_text = self.font.render(symbol, True, self.BLACK)
            symbol_rect = symbol_text.get_rect()
            symbol_rect.centerx = x + 35
            symbol_rect.y = y
            self.screen.blit(symbol_text, symbol_rect)

            # Draw digit
            digit_text = self.small_font.render(str(digit), True, self.BLACK)
            digit_rect = digit_text.get_rect()
            digit_rect.centerx = x + 35
            digit_rect.y = y + 35
            self.screen.blit(digit_text, digit_rect)

            # Draw box around pair
            pygame.draw.rect(self.screen, self.BLACK, (x + 5, y, 60, 55), 1)

        # Instructions
        instructions = [
            "Type the digit (1-9) that corresponds to each symbol",
            "Backspace to go back, ESC to quit"
        ]
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.BLACK)
            text_rect = text.get_rect()
            text_rect.centerx = self.screen.get_width() // 2
            text_rect.y = 50 + i * 20
            self.screen.blit(text, text_rect)

    def calculate_score(self):
        total_attempted = self.total_completed + self.current_position

        return {
            'correct_count': self.correct_count,
            'total_attempted': total_attempted,
            'accuracy': self.correct_count / total_attempted if total_attempted > 0 else 0
        }

    def save_data(self, score):
        # Nothing was attempted (e.g. aborted immediately) - don't write an empty record
        if score['total_attempted'] == 0:
            return

        # Calculate response time statistics
        response_time_stats = {}
        if self.response_times:
            response_time_stats = {
                "mean_response_time": sum(self.response_times) / len(self.response_times),
                "min_response_time": min(self.response_times),
                "max_response_time": max(self.response_times),
                "total_responses": len(self.response_times)
            }

        # Analyze error patterns
        error_analysis = {}
        if self.error_patterns:
            # Count frequency of each type of error
            symbol_confusion_matrix = {}
            for expected_symbol, entered_digit, correct_digit in self.error_patterns:
                key = f"{expected_symbol}→{entered_digit}"
                if key not in symbol_confusion_matrix:
                    symbol_confusion_matrix[key] = 0
                symbol_confusion_matrix[key] += 1

            error_analysis = {
                "total_errors": len(self.error_patterns),
                "symbol_confusion_matrix": symbol_confusion_matrix,
                "most_confused_symbols": sorted(symbol_confusion_matrix.items(),
                                              key=lambda x: x[1], reverse=True)[:5]
            }

        # Prepare data (backwards compatible - new fields are optional)
        data = {
            "test_type": "digit_symbol_substitution_test",
            "duration_seconds": self.test_duration,
            "correct_count": score['correct_count'],
            "total_attempted": score['total_attempted'],
            "accuracy": score['accuracy'],
            "symbol_map": self.symbol_map,
            # New optional fields for enhanced analysis
            "response_times": self.response_times,
            "response_time_stats": response_time_stats,
            "error_patterns": self.error_patterns,
            "error_analysis": error_analysis
        }

        # Save to file using DataManager
        try:
            data_manager = DataManager()
            filepath = data_manager.save_test_data('dsst', data)
            print(f"DSST data saved to {filepath}")
        except Exception as e:
            print(f"Error saving DSST data: {e}")

def run_dsst(screen, font):
    dsst = DigitSymbolSubstitutionTest(screen, font)
    return dsst.run()