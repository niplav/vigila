import pygame
import random
import time
import sys
import json
import os
from datetime import datetime

class PsychomotorVigilanceTask:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.running = True
        self.reaction_times = []
        self.trial_count = 0
        self.max_trials = 10
        self.waiting_for_stimulus = False
        self.stimulus_start_time = 0
        self.stimulus_shown = False
        self.wait_start_time = 0

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)

        # Stimulus wait time (2-10 seconds)
        self.next_stimulus_delay = random.uniform(2.0, 10.0)

    def run(self):
        clock = pygame.time.Clock()
        self.wait_start_time = time.time()

        while self.running and self.trial_count < self.max_trials:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return self.reaction_times

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.stimulus_shown:
                            # Calculate reaction time
                            reaction_time = (time.time() - self.stimulus_start_time) * 1000
                            self.reaction_times.append(reaction_time)
                            self.trial_count += 1

                            # Reset for next trial
                            self.stimulus_shown = False
                            self.waiting_for_stimulus = False
                            self.next_stimulus_delay = random.uniform(2.0, 10.0)
                            self.wait_start_time = time.time()

                        elif not self.waiting_for_stimulus:
                            # Premature response
                            pass

                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return self.reaction_times

            # Check if it's time to show stimulus
            if not self.stimulus_shown and not self.waiting_for_stimulus:
                if time.time() - self.wait_start_time >= self.next_stimulus_delay:
                    self.stimulus_shown = True
                    self.stimulus_start_time = time.time()

            # Draw screen
            self.draw()
            pygame.display.flip()
            clock.tick(60)

        self.save_data()
        return self.reaction_times

    def save_data(self):
        if not self.reaction_times:
            return

        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pvt_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)

        # Prepare data
        data = {
            "test_type": "psychomotor_vigilance_task",
            "timestamp": datetime.now().isoformat(),
            "trial_count": len(self.reaction_times),
            "reaction_times_ms": self.reaction_times,
            "mean_rt_ms": sum(self.reaction_times) / len(self.reaction_times),
            "min_rt_ms": min(self.reaction_times),
            "max_rt_ms": max(self.reaction_times)
        }

        # Save to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"PVT data saved to {filepath}")

    def draw(self):
        self.screen.fill(self.WHITE)

        # Title
        title_text = self.font.render("Psychomotor Vigilance Task", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen.get_width() // 2
        title_rect.y = 50
        self.screen.blit(title_text, title_rect)

        # Instructions
        if self.trial_count == 0:
            instructions = [
                "Press SPACE as quickly as possible when you see the red circle",
                "Do NOT press before the circle appears",
                "ESC to quit"
            ]
            for i, instruction in enumerate(instructions):
                text = self.font.render(instruction, True, self.BLACK)
                text_rect = text.get_rect()
                text_rect.centerx = self.screen.get_width() // 2
                text_rect.y = 150 + i * 30
                self.screen.blit(text, text_rect)

        # Trial counter
        trial_text = self.font.render(f"Trial: {self.trial_count + 1}/{self.max_trials}", True, self.BLACK)
        trial_rect = trial_text.get_rect()
        trial_rect.x = 20
        trial_rect.y = 20
        self.screen.blit(trial_text, trial_rect)

        # Show stimulus (red circle) or waiting message
        if self.stimulus_shown:
            pygame.draw.circle(self.screen, self.RED,
                             (self.screen.get_width() // 2, self.screen.get_height() // 2), 50)

            prompt_text = self.font.render("PRESS SPACE NOW!", True, self.RED)
            prompt_rect = prompt_text.get_rect()
            prompt_rect.centerx = self.screen.get_width() // 2
            prompt_rect.y = self.screen.get_height() // 2 + 80
            self.screen.blit(prompt_text, prompt_rect)
        else:
            wait_text = self.font.render("Wait for the red circle...", True, self.BLACK)
            wait_rect = wait_text.get_rect()
            wait_rect.centerx = self.screen.get_width() // 2
            wait_rect.y = self.screen.get_height() // 2
            self.screen.blit(wait_text, wait_rect)

        # Show recent reaction times
        if self.reaction_times:
            recent_text = self.font.render(f"Last RT: {self.reaction_times[-1]:.0f}ms", True, self.BLACK)
            recent_rect = recent_text.get_rect()
            recent_rect.x = 20
            recent_rect.y = 50
            self.screen.blit(recent_text, recent_rect)

            if len(self.reaction_times) > 1:
                avg_rt = sum(self.reaction_times) / len(self.reaction_times)
                avg_text = self.font.render(f"Avg RT: {avg_rt:.0f}ms", True, self.BLACK)
                avg_rect = avg_text.get_rect()
                avg_rect.x = 20
                avg_rect.y = 80
                self.screen.blit(avg_text, avg_rect)

def run_pvt(screen, font):
    pvt = PsychomotorVigilanceTask(screen, font)
    return pvt.run()