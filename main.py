import math
import pygame
import random
import sys
from pathlib import Path
from game.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    BLACK,
    WHITE,
)
from game.sound.fx import SoundEffects
from game.game_models import Player, Enemy, Bullet
from game.ui import draw_game_over_screen, draw_init_screen, draw_win_screen


# ==========================================
# MAIN GAME LOOP
# ==========================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Warriors")
    clock = pygame.time.Clock()
    font_dir = Path(__file__).parent / "assets" / "fonts"
    display_font_path = (
        font_dir / "Bitcount_Grid_Double" / "static" / "BitcountGridDouble_Roman-Bold.ttf"
    )
    interface_font_path = font_dir / "Space_Grotesk" / "static" / "SpaceGrotesk-Medium.ttf"

    # Bitcount is reserved for the prominent game display; Space Grotesk keeps
    # supporting text and controls easy to read.
    score_font = pygame.font.Font(display_font_path, 50)
    title_font = pygame.font.Font(display_font_path, 70)
    button_font = pygame.font.Font(interface_font_path, 42)

    # Initialize our custom numpy audio from sound.py
    audio = SoundEffects()

    # States
    STATE_INIT = "init"
    STATE_WARP = "warp"
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
    asteroids = []
    game_over_asteroids = []
    win_asteroids = []
    asteroid_spawn_time = 0.0
    screen_asteroid_spawn_time = 0.0
    warp_elapsed = 0.0
    WARP_DURATION = 0.75

    def make_asteroid():
        size = random.randint(4, 10)
        if random.choice((True, False)):
            x, y = random.uniform(-size, SCREEN_WIDTH), random.uniform(-80, -size)
        else:
            x, y = random.uniform(-80, -size), random.uniform(-size, SCREEN_HEIGHT)
        return {"x": x, "y": y, "size": size, "speed": random.uniform(45, 100)}

    def make_game_over_asteroid():
        size = random.randint(7, 15)
        return {
            "x": random.uniform(size, SCREEN_WIDTH - size),
            "y": -size,
            "size": size,
            "vx": random.uniform(-18, 18),
            "vy": random.uniform(80, 180),
            "color": random.choice(((75, 160, 255), (100, 190, 255), (65, 125, 230))),
            "shape": "teardrop",
        }

    def make_win_asteroid():
        size = random.randint(6, 15)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(65, 170)
        return {
            "x": random.uniform(0, SCREEN_WIDTH),
            "y": random.uniform(0, SCREEN_HEIGHT),
            "size": size,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "color": tuple(random.randint(90, 255) for _ in range(3)),
            "shape": random.choice(("rock", "diamond", "triangle")),
        }

    def update_screen_asteroids(asteroid_field, delta_time):
        for asteroid in asteroid_field[:]:
            asteroid["x"] += asteroid["vx"] * delta_time
            asteroid["y"] += asteroid["vy"] * delta_time
            size = asteroid["size"]
            if (
                asteroid["x"] < -size
                or asteroid["x"] > SCREEN_WIDTH + size
                or asteroid["y"] < -size
                or asteroid["y"] > SCREEN_HEIGHT + size
            ):
                asteroid_field.remove(asteroid)

    asteroids = [make_asteroid() for _ in range(18)]

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
        game_over_asteroids.clear()
        win_asteroids.clear()
        spawn_enemies()
        audio.play_start()

    # Shared menu buttons
    start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 295, 260, 65)
    restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 300, 240, 55)
    quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 380, 200, 55)

    running = True

    score_pos = (10, 10)

    while running:
        delta_time = clock.tick(FPS) / 1000
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
                        warp_elapsed = 0.0
                        game_state = STATE_WARP
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

        if game_state in (STATE_INIT, STATE_WARP):
            if game_state == STATE_INIT:
                asteroid_spawn_time += delta_time
                if asteroid_spawn_time >= 0.35:
                    asteroids.append(make_asteroid())
                    asteroid_spawn_time = 0.0

            speed_multiplier = 11 if game_state == STATE_WARP else 1
            for asteroid in asteroids[:]:
                asteroid["x"] += asteroid["speed"] * speed_multiplier * delta_time
                asteroid["y"] += asteroid["speed"] * 0.72 * speed_multiplier * delta_time
                if (
                    asteroid["x"] - asteroid["size"] > SCREEN_WIDTH
                    or asteroid["y"] - asteroid["size"] > SCREEN_HEIGHT
                ):
                    asteroids.remove(asteroid)

            if game_state == STATE_WARP:
                warp_elapsed += delta_time
                if warp_elapsed >= WARP_DURATION:
                    asteroids.clear()
                    game_state = STATE_PLAYING

        elif game_state == STATE_GAME_OVER:
            screen_asteroid_spawn_time += delta_time
            if screen_asteroid_spawn_time >= 0.3 and len(game_over_asteroids) < 40:
                game_over_asteroids.append(make_game_over_asteroid())
                screen_asteroid_spawn_time = 0.0
            update_screen_asteroids(game_over_asteroids, delta_time)

        elif game_state == STATE_WIN:
            screen_asteroid_spawn_time += delta_time
            if screen_asteroid_spawn_time >= 0.22 and len(win_asteroids) < 50:
                win_asteroids.append(make_win_asteroid())
                screen_asteroid_spawn_time = 0.0
            update_screen_asteroids(win_asteroids, delta_time)

        if game_state == STATE_PLAYING:
            score_text = score_font.render(f"SCORE: {score}", True, WHITE)
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
                    if game_state == STATE_PLAYING and enemy.rect.bottom >= player.rect.top:
                        game_state = STATE_GAME_OVER
                        game_over_asteroids = [make_game_over_asteroid() for _ in range(14)]
                        screen_asteroid_spawn_time = 0.0
                        audio.play_game_over()

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

            if game_state == STATE_PLAYING and not enemies:
                game_state = STATE_WIN
                win_asteroids = [make_win_asteroid() for _ in range(18)]
                screen_asteroid_spawn_time = 0.0
                audio.play_win()

            # 5. Drawing
            player.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

        elif game_state == STATE_INIT:
            draw_init_screen(
                screen, title_font, button_font, mouse_pos, start_rect, quit_rect, asteroids
            )

        elif game_state == STATE_WARP:
            draw_init_screen(
                screen,
                title_font,
                button_font,
                mouse_pos,
                start_rect,
                quit_rect,
                asteroids,
                warp_elapsed / WARP_DURATION,
            )

        elif game_state == STATE_GAME_OVER:
            draw_game_over_screen(
                screen,
                title_font,
                button_font,
                mouse_pos,
                score,
                restart_rect,
                quit_rect,
                game_over_asteroids,
            )

        elif game_state == STATE_WIN:
            draw_win_screen(
                screen,
                title_font,
                button_font,
                mouse_pos,
                score,
                restart_rect,
                quit_rect,
                win_asteroids,
            )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
