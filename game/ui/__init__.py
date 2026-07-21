import pygame

from game.constants import GREEN, RED, WHITE, YELLOW
from game.ui.buttons import draw_button, draw_toggle


def draw_centered_text(surface, text, font, color, center_x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, y))
    surface.blit(text_surface, text_rect)


def draw_screen_asteroids(surface, asteroids):
    for asteroid in asteroids:
        x, y, size = asteroid["x"], asteroid["y"], asteroid["size"]
        color = asteroid["color"]
        if asteroid["shape"] == "teardrop":
            points = [
                (x, y - size),
                (x + size * 0.7, y + size * 0.3),
                (x, y + size),
                (x - size * 0.7, y + size * 0.3),
            ]
        elif asteroid["shape"] == "diamond":
            points = [(x, y - size), (x + size, y), (x, y + size), (x - size, y)]
        elif asteroid["shape"] == "triangle":
            points = [(x, y - size), (x + size, y + size), (x - size, y + size)]
        else:
            points = [
                (x - size, y),
                (x - size * 0.3, y - size),
                (x + size, y - size * 0.3),
                (x + size * 0.5, y + size),
                (x - size * 0.6, y + size * 0.5),
            ]
        pygame.draw.polygon(surface, color, points)


def draw_init_screen(
    surface,
    title_font,
    button_font,
    subtitle_font,
    mouse_pos,
    start_rect,
    options_rect,
    quit_rect,
    asteroids,
    warp_progress=0,
    level=1,
    high_score=0,
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

    draw_centered_text(surface, "SPACE WARRIORS", title_font, WHITE, center_x, 120)
    if high_score > 0:
        draw_centered_text(surface, f"HIGH SCORE: {high_score}", subtitle_font, (100, 255, 100), center_x, 165)
    
    if level > 1:
        draw_centered_text(surface, f"LEVEL {level}", subtitle_font, YELLOW, center_x, 200)

    if warp_progress:
        draw_centered_text(surface, "WARP ENGAGED", subtitle_font, YELLOW, center_x, 235)
        return
    draw_centered_text(
        surface, "Press Enter or click Start", subtitle_font, YELLOW, center_x, 235
    )
    draw_button(surface, start_rect, "Start Game", button_font, mouse_pos)
    draw_button(surface, options_rect, "Options", button_font, mouse_pos)
    draw_button(surface, quit_rect, "Quit", button_font, mouse_pos, variant="danger")


def draw_game_over_screen(
    surface, title_font, button_font, subtitle_font, mouse_pos, score, restart_rect, options_rect, quit_rect, asteroids, level=1
):
    center_x = surface.get_width() // 2
    draw_screen_asteroids(surface, asteroids)
    draw_centered_text(surface, "GAME OVER", title_font, RED, center_x, 140)
    draw_centered_text(surface, f"LEVEL {level}", subtitle_font, WHITE, center_x, 195)
    draw_centered_text(
        surface, f"Final Score: {score}", subtitle_font, WHITE, center_x, 240
    )
    draw_button(surface, restart_rect, "Restart", button_font, mouse_pos)
    draw_button(surface, options_rect, "Options", button_font, mouse_pos)
    draw_button(surface, quit_rect, "Quit", button_font, mouse_pos, variant="danger")


def draw_win_screen(
    surface, title_font, button_font, subtitle_font, mouse_pos, score, restart_rect, options_rect, quit_rect, asteroids, level=1
):
    center_x = surface.get_width() // 2
    draw_screen_asteroids(surface, asteroids)
    draw_centered_text(surface, "YOU WIN!", title_font, GREEN, center_x, 140)
    draw_centered_text(surface, f"NEXT: LEVEL {level + 1}", subtitle_font, YELLOW, center_x, 195)
    draw_centered_text(
        surface, f"Final Score: {score}", subtitle_font, WHITE, center_x, 240
    )
    draw_button(surface, restart_rect, "Next Level", button_font, mouse_pos)
    draw_button(surface, options_rect, "Options", button_font, mouse_pos)
    draw_button(surface, quit_rect, "Quit", button_font, mouse_pos, variant="danger")


def draw_options_screen(
    surface,
    title_font,
    button_font,
    mouse_pos,
    back_rect,
    toggle_rects,
    options,
    level=1,
    minus_rect=None,
    plus_rect=None,
    reset_rect=None,
    highest_level=1
):
    center_x = surface.get_width() // 2
    draw_centered_text(surface, "OPTIONS", title_font, YELLOW, center_x, 80)

    labels = ["Music", "Sound FX", "Mouse Ctrl"]
    keys = ["music", "sfx", "mouse_ctrl"]
    for i, (label, key) in enumerate(zip(labels, keys)):
        draw_toggle(
            surface,
            toggle_rects[i],
            label,
            options[key],
            button_font,
            mouse_pos,
        )

    if minus_rect and plus_rect and reset_rect:
        draw_centered_text(surface, "Start Level", button_font, WHITE, center_x, minus_rect.top - 20)
        draw_button(surface, minus_rect, "-", button_font, mouse_pos)
        draw_centered_text(surface, str(level), button_font, YELLOW, center_x, minus_rect.centery)
        draw_button(surface, plus_rect, "+", button_font, mouse_pos)
        draw_button(surface, reset_rect, "Reset", button_font, mouse_pos, variant="danger")

    draw_button(surface, back_rect, "Back", button_font, mouse_pos)
