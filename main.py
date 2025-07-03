import pygame
import sys
from pvt import run_pvt
from dsst import run_dsst
from digit_span import run_digit_span
from stanford_sleepiness import run_stanford_sleepiness_scale

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
GRAY = (128, 128, 128)

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

def main():
    clock = pygame.time.Clock()
    running = True

    # Button properties - 2x2 grid
    button_width = 150
    button_height = 50
    button_spacing = 20

    # Calculate grid positions
    grid_width = 2 * button_width + button_spacing
    grid_height = 2 * button_height + button_spacing
    grid_start_x = SCREEN_WIDTH // 2 - grid_width // 2
    grid_start_y = SCREEN_HEIGHT // 2 - grid_height // 2 + 20

    # Top row
    pvt_button_x = grid_start_x
    pvt_button_y = grid_start_y

    dsst_button_x = grid_start_x + button_width + button_spacing
    dsst_button_y = grid_start_y

    # Bottom row
    digit_span_button_x = grid_start_x
    digit_span_button_y = grid_start_y + button_height + button_spacing

    sss_button_x = grid_start_x + button_width + button_spacing
    sss_button_y = grid_start_y + button_height + button_spacing

    # Exit button properties
    exit_button_x = SCREEN_WIDTH // 2 - button_width // 2
    exit_button_y = grid_start_y + grid_height + 30

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

        # Draw exit button
        draw_button(screen, "Exit", exit_button_x, exit_button_y, button_width, button_height, GRAY, WHITE)

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()