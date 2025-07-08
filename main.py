import pygame
import sys
from data_manager import DataManager
from pvt import run_pvt
from dsst import run_dsst
from digit_span import run_digit_span
from stanford_sleepiness import run_stanford_sleepiness_scale
from subjective_feelings import run_subjective_feelings

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
GRAY = (128, 128, 128)
RED = (220, 20, 60)

# Create the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Orexin Data Collection Tool")

# Font
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 48)

def draw_button(surface, text, x, y, width, height, color, text_color):
    """Draw a button with text"""
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, BLACK, (x, y, width, height), 2)

    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x + width // 2, y + height // 2)
    surface.blit(text_surface, text_rect)

    return pygame.Rect(x, y, width, height)

# Initialize data manager
data_manager = DataManager()

def show_error_message(screen, font, title_font, error_msg):
    """Display error message and exit button"""
    screen.fill((255, 255, 255))
    
    # Draw error title
    error_title = title_font.render("Error", True, (255, 0, 0))
    error_rect = error_title.get_rect()
    error_rect.centerx = 400
    error_rect.y = 150
    screen.blit(error_title, error_rect)
    
    # Draw error message (word wrap)
    words = error_msg.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < 600:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        lines.append(current_line.strip())
    
    y_offset = 220
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.centerx = 400
        text_rect.y = y_offset
        screen.blit(text_surface, text_rect)
        y_offset += 30
    
    # Draw exit button
    exit_button_rect = pygame.Rect(325, y_offset + 30, 150, 50)
    pygame.draw.rect(screen, (128, 128, 128), exit_button_rect)
    pygame.draw.rect(screen, (0, 0, 0), exit_button_rect, 2)
    
    exit_text = font.render("Exit", True, (255, 255, 255))
    exit_text_rect = exit_text.get_rect()
    exit_text_rect.center = exit_button_rect.center
    screen.blit(exit_text, exit_text_rect)
    
    pygame.display.flip()
    return exit_button_rect

def main():
    # Check data setup before starting
    error_msg = data_manager.check_data_setup()
    if error_msg:
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        exit_button_rect = show_error_message(screen, font, title_font, error_msg)
                        if exit_button_rect.collidepoint(pygame.mouse.get_pos()):
                            running = False
            
            show_error_message(screen, font, title_font, error_msg)
            clock.tick(60)
        
        pygame.quit()
        sys.exit(1)
    
    clock = pygame.time.Clock()
    running = True

    # Button properties - 2x3 grid
    button_width = 140
    button_height = 50
    button_spacing = 20

    # Calculate grid positions (2 columns, 3 rows)
    grid_width = 2 * button_width + button_spacing
    grid_height = 3 * button_height + 2 * button_spacing
    grid_start_x = SCREEN_WIDTH // 2 - grid_width // 2
    grid_start_y = SCREEN_HEIGHT // 2 - grid_height // 2 + 20

    # Top row
    pvt_button_x = grid_start_x
    pvt_button_y = grid_start_y

    dsst_button_x = grid_start_x + button_width + button_spacing
    dsst_button_y = grid_start_y

    # Middle row
    digit_span_button_x = grid_start_x
    digit_span_button_y = grid_start_y + button_height + button_spacing

    sss_button_x = grid_start_x + button_width + button_spacing
    sss_button_y = grid_start_y + button_height + button_spacing

    # Bottom row
    feelings_button_x = grid_start_x
    feelings_button_y = grid_start_y + 2 * (button_height + button_spacing)

    exit_button_x = grid_start_x + button_width + button_spacing
    exit_button_y = grid_start_y + 2 * (button_height + button_spacing)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    pvt_button_rect = pygame.Rect(pvt_button_x, pvt_button_y, button_width, button_height)
                    dsst_button_rect = pygame.Rect(dsst_button_x, dsst_button_y, button_width, button_height)
                    digit_span_button_rect = pygame.Rect(digit_span_button_x, digit_span_button_y, button_width, button_height)
                    sss_button_rect = pygame.Rect(sss_button_x, sss_button_y, button_width, button_height)
                    feelings_button_rect = pygame.Rect(feelings_button_x, feelings_button_y, button_width, button_height)
                    exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, button_width, button_height)

                    if pvt_button_rect.collidepoint(mouse_pos):
                        print("Starting Psychomotor Vigilance Task...")
                        reaction_times = run_pvt(screen, font)
                        print(f"PVT completed. Reaction times: {reaction_times}")
                        print(f"Average reaction time: {sum(reaction_times)/len(reaction_times):.1f}ms" if reaction_times else "No data collected")

                    elif dsst_button_rect.collidepoint(mouse_pos):
                        print("Starting Digit Symbol Substitution Test...")
                        score = run_dsst(screen, font)
                        print(f"DSST completed. Score: {score['correct_count']}/{score['total_attempted']} ({score['accuracy']*100:.1f}%)")

                    elif digit_span_button_rect.collidepoint(mouse_pos):
                        print("Starting Digit Span Test...")
                        score = run_digit_span(screen, font)
                        print(f"Digit Span completed. Forward: {score['forward_span']}, Backward: {score['backward_span']}, Total: {score['total_span']}")

                    elif sss_button_rect.collidepoint(mouse_pos):
                        print("Starting Stanford Sleepiness Scale...")
                        rating = run_stanford_sleepiness_scale(screen, font)
                        if rating:
                            print(f"Stanford Sleepiness Scale completed. Rating: {rating}/7")
                        else:
                            print("Stanford Sleepiness Scale cancelled")

                    elif feelings_button_rect.collidepoint(mouse_pos):
                        print("Starting Subjective Feelings Assessment...")
                        feeling_text = run_subjective_feelings(screen, font)
                        if feeling_text:
                            print(f"Subjective Feelings completed. Text: '{feeling_text}'")
                        else:
                            print("Subjective Feelings cancelled")

                    elif exit_button_rect.collidepoint(mouse_pos):
                        running = False

        # Fill screen with white background
        screen.fill(WHITE)

        # Draw title
        title_text = title_font.render("Orexin Data Collection", True, BLACK)
        title_rect = title_text.get_rect()
        title_rect.centerx = SCREEN_WIDTH // 2
        title_rect.y = 150
        screen.blit(title_text, title_rect)

        # Draw subtitle
        subtitle_text = font.render("Psychological Testing Suite", True, GRAY)
        subtitle_rect = subtitle_text.get_rect()
        subtitle_rect.centerx = SCREEN_WIDTH // 2
        subtitle_rect.y = 200
        screen.blit(subtitle_text, subtitle_rect)

        # Draw PVT button
        draw_button(screen, "Start PVT", pvt_button_x, pvt_button_y, button_width, button_height, BLUE, WHITE)

        # Draw DSST button
        draw_button(screen, "Start DSST", dsst_button_x, dsst_button_y, button_width, button_height, BLUE, WHITE)

        # Draw Digit Span button
        draw_button(screen, "Digit Span", digit_span_button_x, digit_span_button_y, button_width, button_height, BLUE, WHITE)

        # Draw SSS button
        draw_button(screen, "Sleepiness", sss_button_x, sss_button_y, button_width, button_height, BLUE, WHITE)

        # Draw Feelings button
        draw_button(screen, "Feelings", feelings_button_x, feelings_button_y, button_width, button_height, BLUE, WHITE)

        # Draw exit button (different color on the right)
        draw_button(screen, "Exit", exit_button_x, exit_button_y, button_width, button_height, RED, WHITE)

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()