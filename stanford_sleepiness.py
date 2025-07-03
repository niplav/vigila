import pygame
import json
import os
from datetime import datetime

class StanfordSleepinessScale:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        self.running = True
        self.selected_rating = None
        self.hovering_rating = None

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.LIGHT_BLUE = (173, 216, 230)
        self.GREEN = (0, 255, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)

        # Stanford Sleepiness Scale descriptions
        self.scale_descriptions = {
            1: "Feeling active, vital, alert, or wide awake",
            2: "Functioning at high levels, but not at peak; able to concentrate",
            3: "Awake, but relaxed; responsive but not fully alert",
            4: "Somewhat foggy, let down",
            5: "Foggy; losing interest in remaining awake; slowed down",
            6: "Sleepy, woozy, fighting sleep; prefer to lie down",
            7: "No longer fighting sleep, sleep onset soon; having dream-like thoughts"
        }

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None

                    # Handle number key selection
                    elif event.key >= pygame.K_1 and event.key <= pygame.K_7:
                        rating = event.key - pygame.K_0
                        self.selected_rating = rating
                        self.save_data(rating)
                        self.running = False
                        return rating

                    # Handle return key
                    elif event.key == pygame.K_RETURN:
                        if self.selected_rating is not None:
                            self.save_data(self.selected_rating)
                            self.running = False
                            return self.selected_rating

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()

                        # Check if clicked on a rating button
                        for rating in range(1, 8):
                            button_rect = self.get_rating_button_rect(rating)
                            if button_rect.collidepoint(mouse_pos):
                                self.selected_rating = rating
                                self.save_data(rating)
                                self.running = False
                                return rating

                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    self.hovering_rating = None

                    # Check if hovering over a rating button
                    for rating in range(1, 8):
                        button_rect = self.get_rating_button_rect(rating)
                        if button_rect.collidepoint(mouse_pos):
                            self.hovering_rating = rating
                            break

            self.draw()
            pygame.display.flip()
            clock.tick(60)

        return None

    def get_rating_button_rect(self, rating):
        """Get the rectangle for a rating button"""
        button_width = 60
        button_height = 50
        start_x = self.screen.get_width() // 2 - (7 * button_width + 6 * 10) // 2
        x = start_x + (rating - 1) * (button_width + 10)
        y = self.screen.get_height() // 2 + 50
        return pygame.Rect(x, y, button_width, button_height)

    def draw(self):
        self.screen.fill(self.WHITE)

        # Title
        title_text = self.large_font.render("Stanford Sleepiness Scale", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.centerx = self.screen.get_width() // 2
        title_rect.y = 30
        self.screen.blit(title_text, title_rect)

        # Instructions
        instruction_text = self.font.render("How do you feel right now?", True, self.BLACK)
        instruction_rect = instruction_text.get_rect()
        instruction_rect.centerx = self.screen.get_width() // 2
        instruction_rect.y = 100
        self.screen.blit(instruction_text, instruction_rect)

        # Rating buttons
        for rating in range(1, 8):
            button_rect = self.get_rating_button_rect(rating)

            # Determine button color
            if self.selected_rating == rating:
                button_color = self.GREEN
                text_color = self.WHITE
            elif self.hovering_rating == rating:
                button_color = self.LIGHT_BLUE
                text_color = self.BLACK
            else:
                button_color = self.LIGHT_GRAY
                text_color = self.BLACK

            # Draw button
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, self.BLACK, button_rect, 2)

            # Draw rating number
            number_text = self.large_font.render(str(rating), True, text_color)
            number_rect = number_text.get_rect()
            number_rect.center = button_rect.center
            self.screen.blit(number_text, number_rect)

        # Show description for hovered or selected rating
        display_rating = self.hovering_rating or self.selected_rating
        if display_rating:
            description = self.scale_descriptions[display_rating]

            # Split long descriptions into multiple lines
            words = description.split()
            lines = []
            current_line = []
            max_width = 600

            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = self.font.render(test_line, True, self.BLACK)
                if test_surface.get_width() <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)

            if current_line:
                lines.append(' '.join(current_line))

            # Draw description
            description_y = self.screen.get_height() // 2 + 120
            for i, line in enumerate(lines):
                desc_text = self.font.render(line, True, self.BLACK)
                desc_rect = desc_text.get_rect()
                desc_rect.centerx = self.screen.get_width() // 2
                desc_rect.y = description_y + i * 30
                self.screen.blit(desc_text, desc_rect)

        # Instructions at bottom
        bottom_instructions = [
            "Click a number or press 1-7 to select your rating",
            "Press ESC to cancel"
        ]

        for i, instruction in enumerate(bottom_instructions):
            text = self.small_font.render(instruction, True, self.GRAY)
            text_rect = text.get_rect()
            text_rect.centerx = self.screen.get_width() // 2
            text_rect.y = self.screen.get_height() - 60 + i * 25
            self.screen.blit(text, text_rect)

    def save_data(self, rating):
        """Save the sleepiness rating to JSON file"""
        # Create data directory if it doesn't exist
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sss_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)

        # Prepare data
        data = {
            "test_type": "stanford_sleepiness_scale",
            "timestamp": datetime.now().isoformat(),
            "rating": rating,
            "description": self.scale_descriptions[rating]
        }

        # Save to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Stanford Sleepiness Scale data saved to {filepath}")

def run_stanford_sleepiness_scale(screen, font):
    sss = StanfordSleepinessScale(screen, font)
    return sss.run()