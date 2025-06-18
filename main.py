import pygame
import sys
from pvt import run_pvt

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

    # Button properties
    button_width = 200
    button_height = 60
    start_button_x = SCREEN_WIDTH // 2 - button_width // 2
    start_button_y = SCREEN_HEIGHT // 2 - button_height // 2

    # Exit button properties
    exit_button_x = SCREEN_WIDTH // 2 - button_width // 2
    exit_button_y = SCREEN_HEIGHT // 2 + button_height + 20

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    start_button_rect = pygame.Rect(start_button_x, start_button_y, button_width, button_height)
                    exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, button_width, button_height)

                    if start_button_rect.collidepoint(mouse_pos):
                        print("Starting Psychomotor Vigilance Task...")
                        reaction_times = run_pvt(screen, font)
                        print(f"PVT completed. Reaction times: {reaction_times}")
                        print(f"Average reaction time: {sum(reaction_times)/len(reaction_times):.1f}ms" if reaction_times else "No data collected")

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

        # Draw start button
        draw_button(screen, "Start PVT", start_button_x, start_button_y, button_width, button_height, BLUE, WHITE)

        # Draw exit button
        draw_button(screen, "Exit", exit_button_x, exit_button_y, button_width, button_height, GRAY, WHITE)

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()