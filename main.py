import pygame
import sys
from data_manager import DataManager
from pvt import run_pvt
from dsst import run_dsst
from digit_span import run_digit_span
from stanford_sleepiness import run_stanford_sleepiness_scale
from subjective_feelings import run_subjective_feelings
from stroop import run_stroop
from temporal_production import run_temporal_production
from temporal_reproduction import run_temporal_reproduction
from visual_fusion_flicker import run_visual_fusion_flicker
from audio_fusion_flicker import run_audio_fusion_flicker
from simultaneous_temporal import run_simultaneous_temporal

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

    # Button properties - 3x4 grid
    button_width = 165
    button_height = 50
    button_spacing = 20

    # Calculate grid positions (3 columns, 4 rows)
    grid_width = 3 * button_width + 2 * button_spacing
    grid_height = 4 * button_height + 3 * button_spacing
    grid_start_x = SCREEN_WIDTH // 2 - grid_width // 2
    grid_start_y = SCREEN_HEIGHT // 2 - grid_height // 2 + 60

    # Row 1
    pvt_button_x = grid_start_x
    pvt_button_y = grid_start_y

    dsst_button_x = grid_start_x + button_width + button_spacing
    dsst_button_y = grid_start_y

    digit_span_button_x = grid_start_x + 2 * (button_width + button_spacing)
    digit_span_button_y = grid_start_y

    # Row 2
    sss_button_x = grid_start_x
    sss_button_y = grid_start_y + button_height + button_spacing

    feelings_button_x = grid_start_x + button_width + button_spacing
    feelings_button_y = grid_start_y + button_height + button_spacing

    stroop_button_x = grid_start_x + 2 * (button_width + button_spacing)
    stroop_button_y = grid_start_y + button_height + button_spacing

    # Row 3
    temp_prod_button_x = grid_start_x
    temp_prod_button_y = grid_start_y + 2 * (button_height + button_spacing)

    temp_repro_button_x = grid_start_x + button_width + button_spacing
    temp_repro_button_y = grid_start_y + 2 * (button_height + button_spacing)

    sim_temp_button_x = grid_start_x + 2 * (button_width + button_spacing)
    sim_temp_button_y = grid_start_y + 2 * (button_height + button_spacing)

    # Row 4
    visual_flicker_button_x = grid_start_x
    visual_flicker_button_y = grid_start_y + 3 * (button_height + button_spacing)

    audio_flicker_button_x = grid_start_x + button_width + button_spacing
    audio_flicker_button_y = grid_start_y + 3 * (button_height + button_spacing)

    exit_button_x = grid_start_x + 2 * (button_width + button_spacing)
    exit_button_y = grid_start_y + 3 * (button_height + button_spacing)

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
                    stroop_button_rect = pygame.Rect(stroop_button_x, stroop_button_y, button_width, button_height)
                    temp_prod_button_rect = pygame.Rect(temp_prod_button_x, temp_prod_button_y, button_width, button_height)
                    temp_repro_button_rect = pygame.Rect(temp_repro_button_x, temp_repro_button_y, button_width, button_height)
                    sim_temp_button_rect = pygame.Rect(sim_temp_button_x, sim_temp_button_y, button_width, button_height)
                    visual_flicker_button_rect = pygame.Rect(visual_flicker_button_x, visual_flicker_button_y, button_width, button_height)
                    audio_flicker_button_rect = pygame.Rect(audio_flicker_button_x, audio_flicker_button_y, button_width, button_height)
                    exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, button_width, button_height)

                    if pvt_button_rect.collidepoint(mouse_pos):
                        print("Starting Psychomotor Vigilance Task...")
                        reaction_times = run_pvt(screen, font)
                        print(f"PVT completed. Reaction times: {reaction_times}")
                        if reaction_times:
                            avg_rt = sum(reaction_times) / len(reaction_times)
                            print(f"Average reaction time: {avg_rt:.1f}ms")
                        else:
                            print("No data collected")

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

                    elif stroop_button_rect.collidepoint(mouse_pos):
                        print("Starting Stroop Test...")
                        score = run_stroop(screen, font)
                        if score:
                            print(f"Stroop Test completed. Accuracy: {score['accuracy']*100:.1f}%, Stroop Effect: {score['stroop_effect_ms']:.1f}ms")

                    elif temp_prod_button_rect.collidepoint(mouse_pos):
                        print("Starting Temporal Production Test...")
                        score = run_temporal_production(screen, font)
                        if score:
                            print(f"Temporal Production completed. Mean error: {score['mean_absolute_percent_error']:.1f}%")

                    elif temp_repro_button_rect.collidepoint(mouse_pos):
                        print("Starting Temporal Reproduction Test...")
                        score = run_temporal_reproduction(screen, font)
                        if score:
                            print(f"Temporal Reproduction completed. Mean absolute error: {score['mean_absolute_error_s']:.1f}s")

                    elif sim_temp_button_rect.collidepoint(mouse_pos):
                        print("Starting Simultaneous Temporal Processing Test...")
                        score = run_simultaneous_temporal(screen, font)
                        if score:
                            print(f"Simultaneous Temporal completed. Time error: {score['mean_time_error_s']:.1f}s, Subtraction accuracy: {score['overall_subtraction_accuracy']*100:.1f}%")

                    elif visual_flicker_button_rect.collidepoint(mouse_pos):
                        print("Starting Visual Fusion Flicker Test...")
                        score = run_visual_fusion_flicker(screen, font)
                        if score:
                            print(f"Visual Fusion Flicker completed. Mean threshold: {score['mean_threshold_hz']:.1f} Hz")

                    elif audio_flicker_button_rect.collidepoint(mouse_pos):
                        print("Starting Audio Fusion Flicker Test...")
                        score = run_audio_fusion_flicker(screen, font)
                        if score:
                            print(f"Audio Fusion Flicker completed. Mean threshold: {score['mean_threshold_hz']:.1f} Hz")

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

        # Row 1
        draw_button(screen, "PVT", pvt_button_x, pvt_button_y, button_width, button_height, BLUE, WHITE)
        draw_button(screen, "DSST", dsst_button_x, dsst_button_y, button_width, button_height, BLUE, WHITE)
        draw_button(screen, "Digit Span", digit_span_button_x, digit_span_button_y, button_width, button_height, BLUE, WHITE)

        # Row 2
        draw_button(screen, "Sleepiness", sss_button_x, sss_button_y, button_width, button_height, BLUE, WHITE)
        draw_button(screen, "Feelings", feelings_button_x, feelings_button_y, button_width, button_height, BLUE, WHITE)
        draw_button(screen, "Stroop", stroop_button_x, stroop_button_y, button_width, button_height, BLUE, WHITE)

        # Row 3
        draw_button(screen, "Time Prod", temp_prod_button_x, temp_prod_button_y, button_width, button_height, BLUE, WHITE)
        draw_button(screen, "Time Repro", temp_repro_button_x, temp_repro_button_y, button_width, button_height, BLUE, WHITE)
        draw_button(screen, "Dual Task", sim_temp_button_x, sim_temp_button_y, button_width, button_height, BLUE, WHITE)

        # Row 4
        draw_button(screen, "Visual Flicker", visual_flicker_button_x, visual_flicker_button_y, button_width, button_height, BLUE, WHITE)
        draw_button(screen, "Audio Flicker", audio_flicker_button_x, audio_flicker_button_y, button_width, button_height, BLUE, WHITE)
        draw_button(screen, "Exit", exit_button_x, exit_button_y, button_width, button_height, RED, WHITE)

        # Update display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()