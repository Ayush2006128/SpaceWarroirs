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


def draw_toggle(surface, rect, label, is_on, font, mouse_pos):
    """Draw an arcade-style toggle switch with a label."""
    hovered = rect.collidepoint(mouse_pos)

    # Toggle track (the background pill shape)
    track_rect = pygame.Rect(rect.right - 80, rect.centery - 16, 64, 32)
    track_color = (30, 180, 80) if is_on else (80, 30, 40)
    track_border = (50, 220, 110) if is_on else (160, 50, 60)
    if hovered:
        track_color = (40, 200, 100) if is_on else (100, 40, 55)

    pygame.draw.rect(surface, track_color, track_rect, border_radius=16)
    pygame.draw.rect(surface, track_border, track_rect, 2, border_radius=16)

    # Knob
    knob_x = track_rect.right - 18 if is_on else track_rect.left + 18
    knob_color = WHITE if is_on else (140, 140, 140)
    pygame.draw.circle(surface, knob_color, (knob_x, track_rect.centery), 12)
    pygame.draw.circle(surface, track_border, (knob_x, track_rect.centery), 12, 2)

    # ON / OFF text inside track
    status_text = "ON" if is_on else "OFF"
    small_font = pygame.font.Font(None, 22)
    status_surface = small_font.render(status_text, True, WHITE)
    status_rect = status_surface.get_rect(center=track_rect.center)
    if is_on:
        status_rect.centerx = track_rect.centerx - 10
    else:
        status_rect.centerx = track_rect.centerx + 8
    surface.blit(status_surface, status_rect)

    # Label to the left of the toggle
    label_surface = font.render(label, True, YELLOW if hovered else WHITE)
    label_shadow = font.render(label, True, BLACK)
    label_rect = label_surface.get_rect(midleft=(rect.left + 15, rect.centery))
    surface.blit(label_shadow, label_rect.move(2, 2))
    surface.blit(label_surface, label_rect)

    return track_rect
