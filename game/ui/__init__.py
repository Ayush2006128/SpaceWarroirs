import pygame

from game.constants import BLACK, BLUE, GREEN, RED, WHITE, YELLOW


def draw_centered_text(surface, text, font, color, center_x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, y))
    surface.blit(text_surface, text_rect)


def draw_button(surface, rect, label, font, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)
    frame_color = YELLOW if hovered else BLUE
    fill_color = (30, 34, 75) if hovered else (18, 22, 48)

    # Offset shadow and squared, nested borders evoke the arcade cabinet UI.
    pygame.draw.rect(surface, (4, 6, 18), rect.move(5, 5))
    pygame.draw.rect(surface, frame_color, rect, 3)
    inner_rect = rect.inflate(-10, -10)
    pygame.draw.rect(surface, fill_color, inner_rect)
    pygame.draw.rect(surface, frame_color, inner_rect, 1)

    # Bright corner brackets give the frame a Space Invaders-style silhouette.
    corner_size = 10
    for x, y, x_dir, y_dir in (
        (rect.left + 4, rect.top + 4, 1, 1),
        (rect.right - 4, rect.top + 4, -1, 1),
        (rect.left + 4, rect.bottom - 4, 1, -1),
        (rect.right - 4, rect.bottom - 4, -1, -1),
    ):
        pygame.draw.line(surface, frame_color, (x, y), (x + x_dir * corner_size, y), 3)
        pygame.draw.line(surface, frame_color, (x, y), (x, y + y_dir * corner_size), 3)

    text_color = WHITE if not hovered else YELLOW
    text_surface = font.render(label, True, text_color)
    text_shadow = font.render(label, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_shadow, text_rect.move(2, 2))
    surface.blit(text_surface, text_rect)


def draw_init_screen(
    surface,
    title_font,
    button_font,
    mouse_pos,
    start_rect,
    quit_rect,
    asteroids,
    warp_progress=0,
):
    center_x = surface.get_width() // 2
    for asteroid in asteroids:
        x, y, size = asteroid["x"], asteroid["y"], asteroid["size"]
        if warp_progress:
            trail_length = int(size * (8 + warp_progress * 22))
            pygame.draw.line(
                surface,
                WHITE,
                (x - trail_length, y - trail_length * 0.72),
                (x, y),
                max(1, size // 3),
            )
        pygame.draw.polygon(
            surface,
            WHITE,
            [
                (x - size, y),
                (x - size // 3, y - size),
                (x + size, y - size // 3),
                (x + size // 2, y + size),
                (x - size // 2, y + size // 2),
            ],
        )

    draw_centered_text(surface, "SPACE WARRIORS", title_font, WHITE, center_x, 170)
    if warp_progress:
        draw_centered_text(surface, "WARP ENGAGED", button_font, YELLOW, center_x, 240)
        return
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
