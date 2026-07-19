import pygame

from game.constants import BLACK, BLUE, GREEN, RED, WHITE, YELLOW


def draw_centered_text(surface, text, font, color, center_x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, y))
    surface.blit(text_surface, text_rect)


def draw_button(surface, rect, label, font, mouse_pos):
    color = BLUE if rect.collidepoint(mouse_pos) else WHITE
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=8)
    text_surface = font.render(label, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_init_screen(surface, title_font, button_font, mouse_pos, start_rect, quit_rect):
    center_x = surface.get_width() // 2
    draw_centered_text(surface, "SPACE WARRIORS", title_font, WHITE, center_x, 170)
    draw_centered_text(
        surface, "Press Enter or click Start", button_font, YELLOW, center_x, 240
    )
    draw_button(surface, start_rect, "Start Game", button_font, mouse_pos)
    draw_button(surface, quit_rect, "Quit", button_font, mouse_pos)


def draw_game_over_screen(
    surface, title_font, button_font, mouse_pos, score, restart_rect, quit_rect
):
    center_x = surface.get_width() // 2
    draw_centered_text(surface, "GAME OVER", title_font, RED, center_x, 170)
    draw_centered_text(
        surface, f"Final Score: {score}", button_font, WHITE, center_x, 240
    )
    draw_button(surface, restart_rect, "Restart", button_font, mouse_pos)
    draw_button(surface, quit_rect, "Quit", button_font, mouse_pos)


def draw_win_screen(
    surface, title_font, button_font, mouse_pos, score, restart_rect, quit_rect
):
    center_x = surface.get_width() // 2
    draw_centered_text(surface, "YOU WIN!", title_font, GREEN, center_x, 170)
    draw_centered_text(
        surface, f"Final Score: {score}", button_font, WHITE, center_x, 240
    )
    draw_button(surface, restart_rect, "Play Again", button_font, mouse_pos)
    draw_button(surface, quit_rect, "Quit", button_font, mouse_pos)
