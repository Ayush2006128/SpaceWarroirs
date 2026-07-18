import pygame
import sys
from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    BLACK,
    GREEN,
    RED,
    WHITE,
    YELLOW,
    BLUE,
)
from sound import SoundEngine


# ==========================================
# GAME CLASSES
# ==========================================
class Player:
    def __init__(self):
        self.width = 40
        self.height = 20
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 6
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, dx):
        self.x += dx * self.speed
        # Keep player on screen
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect)
        # Add a little cannon on top
        pygame.draw.rect(surface, GREEN, (self.x + 15, self.y - 10, 10, 10))


class Enemy:
    def __init__(self, x, y):
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)
        # Alien eyes
        pygame.draw.rect(surface, BLACK, (self.rect.x + 5, self.rect.y + 5, 5, 5))
        pygame.draw.rect(surface, BLACK, (self.rect.x + 20, self.rect.y + 5, 5, 5))


class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 15)
        self.speed = 10

    def move(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)


# ==========================================
# UI HELPERS
# ==========================================
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


# ==========================================
# MAIN GAME LOOP
# ==========================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Warriors")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 50)
    title_font = pygame.font.Font(None, 70)
    button_font = pygame.font.Font(None, 42)

    # Initialize our custom numpy audio from sound.py
    audio = SoundEngine()

    # States
    STATE_INIT = "init"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"
    STATE_WIN = "win"
    game_state = STATE_INIT

    player = None
    bullets = []
    enemies = []
    enemy_speed = 2
    enemy_drop = 30
    enemy_direction = 1
    score = 0

    def spawn_enemies():
        enemies.clear()
        for row in range(4):
            for col in range(10):
                x = 50 + col * 60
                y = 50 + row * 50
                enemies.append(Enemy(x, y))

    def reset_game():
        nonlocal player, bullets, enemy_speed, enemy_direction, score
        player = Player()
        bullets = []
        enemy_speed = 2
        enemy_direction = 1
        score = 0
        spawn_enemies()

    # Shared menu buttons
    start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 300, 200, 55)
    restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 300, 240, 55)
    quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 380, 200, 55)

    running = True

    score_pos = (10, 10)

    while running:
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        # 1. Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == STATE_INIT:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = STATE_PLAYING
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_rect.collidepoint(event.pos):
                        reset_game()
                        game_state = STATE_PLAYING
                    elif quit_rect.collidepoint(event.pos):
                        running = False

            elif game_state in (STATE_GAME_OVER, STATE_WIN):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = STATE_PLAYING
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_rect.collidepoint(event.pos):
                        reset_game()
                        game_state = STATE_PLAYING
                    elif quit_rect.collidepoint(event.pos):
                        running = False

            elif game_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    bullets.append(
                        Bullet(player.x + player.width // 2 - 2, player.y - 10)
                    )
                    audio.play_shoot()

        if game_state == STATE_PLAYING:
            score_text = font.render(f"SCORE: {score}", True, WHITE)
            sc_rect = score_text.get_rect(topleft=score_pos)
            screen.blit(score_text, sc_rect)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_l] or keys[pygame.K_d]:
                player.move(-1)
            if keys[pygame.K_RIGHT] or keys[pygame.K_h] or keys[pygame.K_a]:
                player.move(1)

            # 2. Update Bullets
            for bullet in bullets[:]:
                bullet.move()
                if bullet.rect.y < 0:
                    bullets.remove(bullet)

            # 3. Update Enemies
            move_down = False
            for enemy in enemies:
                enemy.rect.x += enemy_speed * enemy_direction
                if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                    move_down = True

            if move_down:
                enemy_direction *= -1
                for enemy in enemies:
                    enemy.rect.x += enemy_speed * enemy_direction
                    enemy.rect.y += enemy_drop
                    if enemy.rect.bottom >= player.rect.top:
                        game_state = STATE_GAME_OVER

            # 4. Collisions
            for bullet in bullets[:]:
                for enemy in enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        audio.play_boom()
                        if bullet in bullets:
                            bullets.remove(bullet)
                        enemies.remove(enemy)
                        score += 1
                        break

            if not enemies:
                game_state = STATE_WIN

            # 5. Drawing
            player.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

        elif game_state == STATE_INIT:
            draw_centered_text(
                screen, "SPACE WARRIORS", title_font, WHITE, SCREEN_WIDTH // 2, 170
            )
            draw_centered_text(
                screen,
                "Press Enter or click Start",
                button_font,
                YELLOW,
                SCREEN_WIDTH // 2,
                240,
            )
            draw_button(screen, start_rect, "Start Game", button_font, mouse_pos)
            draw_button(screen, quit_rect, "Quit", button_font, mouse_pos)

        elif game_state == STATE_GAME_OVER:
            draw_centered_text(screen, "GAME OVER", title_font, RED, SCREEN_WIDTH // 2, 170)
            draw_centered_text(
                screen, f"Final Score: {score}", button_font, WHITE, SCREEN_WIDTH // 2, 240
            )
            draw_button(screen, restart_rect, "Restart", button_font, mouse_pos)
            draw_button(screen, quit_rect, "Quit", button_font, mouse_pos)

        elif game_state == STATE_WIN:
            draw_centered_text(screen, "YOU WIN!", title_font, GREEN, SCREEN_WIDTH // 2, 170)
            draw_centered_text(
                screen, f"Final Score: {score}", button_font, WHITE, SCREEN_WIDTH // 2, 240
            )
            draw_button(screen, restart_rect, "Play Again", button_font, mouse_pos)
            draw_button(screen, quit_rect, "Quit", button_font, mouse_pos)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
