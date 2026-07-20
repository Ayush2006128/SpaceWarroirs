import pygame

from game.constants import BLACK, BLUE, RED, WHITE, YELLOW


def draw_button(surface, rect, label, font, mouse_pos, variant="primary"):
    """Draw a reusable arcade-style menu button."""
    hovered = rect.collidepoint(mouse_pos)
    if variant == "danger":
        frame_color = YELLOW if hovered else RED
        fill_color = (82, 24, 42) if hovered else (48, 16, 31)
    else:
        frame_color = YELLOW if hovered else BLUE
        fill_color = (30, 34, 75) if hovered else (18, 22, 48)

    pygame.draw.rect(surface, (4, 6, 18), rect.move(5, 5))
    pygame.draw.rect(surface, frame_color, rect, 3)
    inner_rect = rect.inflate(-10, -10)
    pygame.draw.rect(surface, fill_color, inner_rect)
    pygame.draw.rect(surface, frame_color, inner_rect, 1)

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
