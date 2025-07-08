import pygame
from data_manager import DataManager

class SubjectiveFeelingsTest:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.large_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        self.running = True
        self.input_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 500  # milliseconds
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (70, 130, 180)
        self.LIGHT_BLUE = (173, 216, 230)
        self.GREEN = (0, 255, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        
        # Text box properties
        self.text_box_width = 600
        self.text_box_height = 100
        self.text_box_x = (800 - self.text_box_width) // 2
        self.text_box_y = 300
        self.text_box_rect = pygame.Rect(self.text_box_x, self.text_box_y, self.text_box_width, self.text_box_height)
        
        # Button properties
        self.button_width = 120
        self.button_height = 40
        self.submit_button_x = self.text_box_x + self.text_box_width - self.button_width
        self.submit_button_y = self.text_box_y + self.text_box_height + 20
        self.cancel_button_x = self.text_box_x
        self.cancel_button_y = self.submit_button_y

    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            dt = clock.tick(60)
            self.cursor_timer += dt
            
            # Handle cursor blinking
            if self.cursor_timer >= self.cursor_blink_rate:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                    
                    elif event.key == pygame.K_RETURN:
                        if self.input_text.strip():
                            self.save_data(self.input_text.strip())
                            self.running = False
                            return self.input_text.strip()
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                        self.cursor_visible = True
                        self.cursor_timer = 0
                    
                    else:
                        # Add character to input if it's printable and not too long
                        if event.unicode.isprintable() and len(self.input_text) < 200:
                            self.input_text += event.unicode
                            self.cursor_visible = True
                            self.cursor_timer = 0
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Check submit button
                        submit_button_rect = pygame.Rect(self.submit_button_x, self.submit_button_y, self.button_width, self.button_height)
                        if submit_button_rect.collidepoint(mouse_pos):
                            if self.input_text.strip():
                                self.save_data(self.input_text.strip())
                                self.running = False
                                return self.input_text.strip()
                        
                        # Check cancel button
                        cancel_button_rect = pygame.Rect(self.cancel_button_x, self.cancel_button_y, self.button_width, self.button_height)
                        if cancel_button_rect.collidepoint(mouse_pos):
                            self.running = False
                            return None
                        
                        # Check text box click (focus)
                        if self.text_box_rect.collidepoint(mouse_pos):
                            self.cursor_visible = True
                            self.cursor_timer = 0
            
            self.draw()
        
        return None

    def draw(self):
        self.screen.fill(self.WHITE)
        
        # Title
        title_text = self.large_font.render("How Are You Feeling?", True, self.BLACK)
        title_rect = title_text.get_rect()
        title_rect.centerx = 400
        title_rect.y = 150
        self.screen.blit(title_text, title_rect)
        
        # Instructions
        instruction_text = self.font.render("Please describe how you're feeling right now:", True, self.BLACK)
        instruction_rect = instruction_text.get_rect()
        instruction_rect.centerx = 400
        instruction_rect.y = 220
        self.screen.blit(instruction_text, instruction_rect)
        
        # Text box
        pygame.draw.rect(self.screen, self.WHITE, self.text_box_rect)
        pygame.draw.rect(self.screen, self.BLACK, self.text_box_rect, 2)
        
        # Text input with word wrapping
        if self.input_text or self.cursor_visible:
            self.draw_text_with_cursor()
        else:
            # Placeholder text
            placeholder_text = self.small_font.render("Type here...", True, self.GRAY)
            placeholder_rect = placeholder_text.get_rect()
            placeholder_rect.x = self.text_box_x + 10
            placeholder_rect.y = self.text_box_y + 10
            self.screen.blit(placeholder_text, placeholder_rect)
        
        # Submit button
        submit_button_rect = pygame.Rect(self.submit_button_x, self.submit_button_y, self.button_width, self.button_height)
        submit_color = self.GREEN if self.input_text.strip() else self.GRAY
        pygame.draw.rect(self.screen, submit_color, submit_button_rect)
        pygame.draw.rect(self.screen, self.BLACK, submit_button_rect, 2)
        
        submit_text = self.font.render("Submit", True, self.WHITE)
        submit_text_rect = submit_text.get_rect()
        submit_text_rect.center = submit_button_rect.center
        self.screen.blit(submit_text, submit_text_rect)
        
        # Cancel button
        cancel_button_rect = pygame.Rect(self.cancel_button_x, self.cancel_button_y, self.button_width, self.button_height)
        pygame.draw.rect(self.screen, self.GRAY, cancel_button_rect)
        pygame.draw.rect(self.screen, self.BLACK, cancel_button_rect, 2)
        
        cancel_text = self.font.render("Cancel", True, self.WHITE)
        cancel_text_rect = cancel_text.get_rect()
        cancel_text_rect.center = cancel_button_rect.center
        self.screen.blit(cancel_text, cancel_text_rect)
        
        # Instructions at bottom
        instructions = [
            "Press Enter to submit, Escape to cancel",
            "Maximum 200 characters"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.GRAY)
            text_rect = text.get_rect()
            text_rect.centerx = 400
            text_rect.y = 500 + i * 25
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()

    def draw_text_with_cursor(self):
        """Draw text with word wrapping and cursor"""
        words = self.input_text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            text_width = self.font.size(test_line)[0]
            
            if text_width < self.text_box_width - 20:  # 20px padding
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.rstrip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.rstrip())
        
        # Draw text lines
        y_offset = self.text_box_y + 10
        line_height = self.font.get_height()
        
        for i, line in enumerate(lines):
            if y_offset + line_height > self.text_box_y + self.text_box_height - 10:
                break  # Don't overflow text box
            
            text_surface = self.font.render(line, True, self.BLACK)
            self.screen.blit(text_surface, (self.text_box_x + 10, y_offset))
            y_offset += line_height
        
        # Draw cursor
        if self.cursor_visible and len(lines) > 0:
            last_line = lines[-1] if lines else ""
            cursor_x = self.text_box_x + 10 + self.font.size(last_line)[0]
            cursor_y = self.text_box_y + 10 + (len(lines) - 1) * line_height
            
            if cursor_y + line_height <= self.text_box_y + self.text_box_height - 10:
                pygame.draw.line(self.screen, self.BLACK, 
                               (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + line_height), 2)

    def save_data(self, feeling_text):
        """Save the subjective feelings data"""
        data = {
            "test_type": "subjective_feelings",
            "feeling_text": feeling_text,
            "character_count": len(feeling_text)
        }
        
        try:
            data_manager = DataManager()
            filepath = data_manager.save_test_data('feelings', data)
            print(f"Subjective feelings data saved to {filepath}")
        except Exception as e:
            print(f"Error saving subjective feelings data: {e}")

def run_subjective_feelings(screen, font):
    feelings_test = SubjectiveFeelingsTest(screen, font)
    return feelings_test.run()