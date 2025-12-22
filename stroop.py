import pygame
import random
import time
from data_manager import DataManager

class StroopTest:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.large_font = pygame.font.Font(None, 96)
        self.small_font = pygame.font.Font(None, 24)
        self.running = True

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (220, 50, 50)
        self.GREEN = (50, 200, 50)
        self.BLUE = (50, 100, 220)
        self.YELLOW = (220, 200, 50)
        self.GRAY = (150, 150, 150)

        # Color mappings
        self.color_names = ['RED', 'GREEN', 'BLUE', 'YELLOW']
        self.color_map = {
            'RED': self.RED,
            'GREEN': self.GREEN,
            'BLUE': self.BLUE,
            'YELLOW': self.YELLOW
        }
        self.key_map = {
            pygame.K_r: 'RED',
            pygame.K_g: 'GREEN',
            pygame.K_b: 'BLUE',
            pygame.K_y: 'YELLOW'
        }

        # Test parameters
        self.total_trials = 60
        self.current_trial = 0
        self.trials = []
        self.results = []

        # Current trial state
        self.current_word = None
        self.current_color = None
        self.trial_start_time = None
        self.showing_feedback = False
        self.feedback_start_time = None
        self.feedback_correct = False

        # Generate trials
        self._generate_trials()

    def _generate_trials(self):
        """Generate randomized list of trials (50% congruent, 50% incongruent)"""
        trials = []

        # Generate congruent trials
        for _ in range(self.total_trials // 2):
            word = random.choice(self.color_names)
            trials.append({'word': word, 'color': word, 'congruent': True})

        # Generate incongruent trials
        for _ in range(self.total_trials // 2):
            word = random.choice(self.color_names)
            colors = [c for c in self.color_names if c != word]
            color = random.choice(colors)
            trials.append({'word': word, 'color': color, 'congruent': False})

        # Shuffle trials
        random.shuffle(trials)
        self.trials = trials

    def _start_trial(self):
        """Start a new trial"""
        if self.current_trial < len(self.trials):
            trial = self.trials[self.current_trial]
            self.current_word = trial['word']
            self.current_color = trial['color']
            self.trial_start_time = time.time()

    def run(self):
        clock = pygame.time.Clock()
        self._start_trial()

        while self.running and self.current_trial < self.total_trials:
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        break

                    # Handle response only if not showing feedback
                    if not self.showing_feedback and event.key in self.key_map:
                        response = self.key_map[event.key]
                        reaction_time = (current_time - self.trial_start_time) * 1000
                        correct = (response == self.current_color)

                        # Record result
                        trial_data = {
                            'trial_number': self.current_trial + 1,
                            'word': self.current_word,
                            'color': self.current_color,
                            'congruent': self.trials[self.current_trial]['congruent'],
                            'response': response,
                            'correct': correct,
                            'reaction_time_ms': reaction_time,
                            'timestamp': current_time
                        }
                        self.results.append(trial_data)

                        # Show feedback
                        self.showing_feedback = True
                        self.feedback_start_time = current_time
                        self.feedback_correct = correct

            # Check if feedback period is over
            if self.showing_feedback:
                if current_time - self.feedback_start_time >= 0.2:  # 200ms feedback
                    self.showing_feedback = False
                    self.current_trial += 1
                    self._start_trial()

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

        correct_trials = [r for r in self.results if r['correct']]
        incorrect_trials = [r for r in self.results if not r['correct']]

        congruent_trials = [r for r in self.results if r['congruent']]
        incongruent_trials = [r for r in self.results if not r['congruent']]

        congruent_correct = [r for r in congruent_trials if r['correct']]
        incongruent_correct = [r for r in incongruent_trials if r['correct']]

        # Calculate mean RTs
        mean_rt_all = sum(r['reaction_time_ms'] for r in self.results) / len(self.results) if self.results else 0
        mean_rt_congruent = sum(r['reaction_time_ms'] for r in congruent_correct) / len(congruent_correct) if congruent_correct else 0
        mean_rt_incongruent = sum(r['reaction_time_ms'] for r in incongruent_correct) / len(incongruent_correct) if incongruent_correct else 0

        stroop_effect = mean_rt_incongruent - mean_rt_congruent

        # Error analysis
        error_patterns = {}
        for trial in incorrect_trials:
            error_key = f"{trial['word']}_{trial['color']}_as_{trial['response']}"
            error_patterns[error_key] = error_patterns.get(error_key, 0) + 1

        score = {
            'total_trials': len(self.results),
            'correct_count': len(correct_trials),
            'accuracy': len(correct_trials) / len(self.results) if self.results else 0,
            'mean_rt_ms': mean_rt_all,
            'mean_rt_congruent_ms': mean_rt_congruent,
            'mean_rt_incongruent_ms': mean_rt_incongruent,
            'stroop_effect_ms': stroop_effect,
            'congruent_trials': len(congruent_trials),
            'incongruent_trials': len(incongruent_trials),
            'congruent_accuracy': len(congruent_correct) / len(congruent_trials) if congruent_trials else 0,
            'incongruent_accuracy': len(incongruent_correct) / len(incongruent_trials) if incongruent_trials else 0,
            'error_patterns': error_patterns,
            'trials': self.results
        }

        return score

    def save_data(self, score):
        """Save test data"""
        if not score:
            return

        data = {
            "test_type": "stroop_test",
            **score
        }

        try:
            data_manager = DataManager()
            filepath = data_manager.save_test_data('stroop', data)
            print(f"Stroop test data saved to {filepath}")
        except Exception as e:
            print(f"Error saving Stroop test data: {e}")

    def draw(self):
        """Draw the test UI"""
        # Feedback flash or white background
        if self.showing_feedback:
            if self.feedback_correct:
                self.screen.fill(self.GREEN)
            else:
                self.screen.fill(self.RED)
        else:
            self.screen.fill(self.WHITE)

        # Title
        title_text = self.font.render("Stroop Test", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.x = 20
        title_rect.y = 20
        self.screen.blit(title_text, title_rect)

        # Trial counter
        trial_text = self.font.render(f"Trial: {self.current_trial + 1}/{self.total_trials}", True, self.BLACK)
        trial_rect = trial_text.get_rect()
        trial_rect.x = self.screen.get_width() - 200
        trial_rect.y = 20
        self.screen.blit(trial_text, trial_rect)

        # Show word in color (if not showing feedback)
        if not self.showing_feedback and self.current_word:
            word_surface = self.large_font.render(self.current_word, True, self.color_map[self.current_color])
            word_rect = word_surface.get_rect()
            word_rect.center = (self.screen.get_width() // 2, self.screen.get_height() // 2 - 50)
            self.screen.blit(word_surface, word_rect)

        # Instructions
        if not self.showing_feedback:
            instruction_text = self.small_font.render("Press the key matching the COLOR (not the word)", True, self.BLACK)
            instruction_rect = instruction_text.get_rect()
            instruction_rect.centerx = self.screen.get_width() // 2
            instruction_rect.y = self.screen.get_height() // 2 + 80
            self.screen.blit(instruction_text, instruction_rect)

            # Key legend
            legend_y = self.screen.get_height() // 2 + 120
            legend_text = self.small_font.render("R: Red    G: Green    B: Blue    Y: Yellow", True, self.BLACK)
            legend_rect = legend_text.get_rect()
            legend_rect.centerx = self.screen.get_width() // 2
            legend_rect.y = legend_y
            self.screen.blit(legend_text, legend_rect)

        # Statistics (bottom)
        if self.results:
            correct_count = sum(1 for r in self.results if r['correct'])
            accuracy = (correct_count / len(self.results)) * 100
            mean_rt = sum(r['reaction_time_ms'] for r in self.results) / len(self.results)

            stats_text = self.small_font.render(f"Accuracy: {accuracy:.1f}%    Avg RT: {mean_rt:.0f}ms", True, self.BLACK)
            stats_rect = stats_text.get_rect()
            stats_rect.centerx = self.screen.get_width() // 2
            stats_rect.y = self.screen.get_height() - 40
            self.screen.blit(stats_text, stats_rect)

def run_stroop(screen, font):
    """Module-level runner function"""
    test = StroopTest(screen, font)
    return test.run()
