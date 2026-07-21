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
from game.sound.music import MusicManager
from game.game_models import Player, Enemy, Bullet, EnemyBullet, HealthBooster
from game.ui import draw_game_over_screen, draw_init_screen, draw_win_screen, draw_options_screen
from game.database import init_db, get_state, save_high_score, save_highest_level, save_settings, reset_to_default

# Base directory: bundled (PyInstaller) or the project root (where main.py lives).
try:
    _BASE_DIR = Path(sys._MEIPASS)
except AttributeError:
    _BASE_DIR = Path(__file__).resolve().parent


# ==========================================
# MAIN GAME LOOP
# ==========================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Warriors")
    icon = pygame.image.load(str(_BASE_DIR / "assets" / "images" / "SpaceWarriors.png"))
    icon = pygame.transform.scale(icon, (32, 32))
    pygame.display.set_icon(icon)
    clock = pygame.time.Clock()
    font_dir = _BASE_DIR / "assets" / "fonts"
    display_font_path = (
        font_dir / "Bitcount_Grid_Double" / "static" / "BitcountGridDouble_Roman-Bold.ttf"
    )
    interface_font_path = font_dir / "Space_Grotesk" / "static" / "SpaceGrotesk-Medium.ttf"

    # Bitcount is reserved for the prominent game display; Space Grotesk keeps
    # supporting text and controls easy to read.
    score_font = pygame.font.Font(display_font_path, 50)
    title_font = pygame.font.Font(display_font_path, 70)
    button_font = pygame.font.Font(interface_font_path, 42)
    options_font = pygame.font.Font(interface_font_path, 32)
    hud_font = pygame.font.Font(interface_font_path, 28)

    init_db()
    state = get_state()
    high_score = state["high_score"]
    highest_level = state["highest_level"]
    options = {"music": state["music"], "sfx": state["sfx"], "mouse_ctrl": state["mouse_ctrl"]}
    
    # States
    STATE_INIT = "init"
    STATE_WARP = "warp"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"
    STATE_WIN = "win"
    STATE_OPTIONS = "options"
    game_state = STATE_INIT

    # Initialize game SFX and background music systems.
    audio = SoundEffects()
    audio.set_muted(not options["sfx"])
    music = MusicManager()
    music.set_muted(not options["music"])
    music.play_for_state(game_state)

    player = None
    bullets = []
    enemies = []
    small_enemies = []
    enemy_bullets = []
    enemy_speed = 2
    enemy_drop = 30
    enemy_direction = 1
    score = 0
    level = highest_level
    small_enemies_defeated = 0
    health_boosters = []
    booster_timer = 0.0
    booster_interval = random.randint(1, 5)
    asteroids = []
    game_over_asteroids = []
    win_asteroids = []
    asteroid_spawn_time = 0.0
    screen_asteroid_spawn_time = 0.0
    warp_elapsed = 0.0
    WARP_DURATION = 0.75
    auto_fire_timer = 0.0
    AUTO_FIRE_INTERVAL = 0.35
    small_enemy_spawn_timer = 0.0

    # Options state
    pre_options_state = STATE_INIT  # tracks which screen opened options

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

    def has_special_ship(lvl):
        """Player gets a special ship on level 3 and every multiple of 10."""
        return lvl == 3 or (lvl >= 10 and lvl % 10 == 0)

    def spawn_enemies():
        enemies.clear()
        for row in range(4):
            for col in range(10):
                x = 50 + col * 60
                y = 50 + row * 50
                if level >= 3 and row == 0:
                    # Front row becomes boss enemies on L3+
                    enemies.append(Enemy(x, y, enemy_type="boss", health=3))
                else:
                    enemies.append(Enemy(x, y))

    def spawn_small_enemy_wave():
        """Spawn 4 small enemies from random screen edges."""
        for _ in range(4):
            side = random.choice(("top", "left", "right"))
            if side == "top":
                x = random.uniform(20, SCREEN_WIDTH - 20)
                y = -20
                vx = random.uniform(-80, 80)
                vy = random.uniform(120, 220)
            elif side == "left":
                x = -20
                y = random.uniform(20, SCREEN_HEIGHT // 2)
                vx = random.uniform(120, 220)
                vy = random.uniform(40, 140)
            else:
                x = SCREEN_WIDTH + 20
                y = random.uniform(20, SCREEN_HEIGHT // 2)
                vx = random.uniform(-220, -120)
                vy = random.uniform(40, 140)
            e = Enemy(x, y, enemy_type="small")
            e.vx = vx
            e.vy = vy
            small_enemies.append(e)

    def fire_player_bullets():
        """Create bullets based on whether player has a special ship."""
        bx = player.x + player.width // 2 - 2
        by = player.y - 10
        new_bullets = []
        if player.special_ship:
            # Three-bullet spread: center, slight left, slight right
            new_bullets.append(Bullet(bx, by))
            new_bullets.append(Bullet(bx - 14, by + 4))
            new_bullets.append(Bullet(bx + 14, by + 4))
        else:
            new_bullets.append(Bullet(bx, by))
        return new_bullets

    def reset_game():
        nonlocal player, bullets, enemy_speed, enemy_direction, score, auto_fire_timer
        nonlocal enemy_bullets, small_enemies, small_enemies_defeated, small_enemy_spawn_timer
        nonlocal health_boosters, booster_timer, booster_interval
        player = Player(special_ship=has_special_ship(level))
        bullets = []
        enemy_bullets = []
        small_enemies = []
        small_enemies_defeated = 0
        small_enemy_spawn_timer = 0.0
        enemy_speed = 2
        enemy_direction = 1
        score = 0
        auto_fire_timer = 0.0
        health_boosters = []
        booster_timer = 0.0
        booster_interval = random.randint(1, 5)
        game_over_asteroids.clear()
        win_asteroids.clear()
        spawn_enemies()
        audio.play_start()

    def set_game_state(new_state):
        nonlocal game_state
        game_state = new_state
        # Don't change music when entering/leaving options; keep whatever is playing.
        if new_state != STATE_OPTIONS:
            music.play_for_state(game_state)

    # Shared menu buttons
    start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 270, 260, 65)
    options_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 350, 260, 65)
    restart_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 300, 240, 55)
    endscreen_options_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 370, 240, 55)
    quit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 55)

    # Options screen layout
    toggle_w, toggle_h = 350, 45
    toggle_x = SCREEN_WIDTH // 2 - toggle_w // 2
    toggle_rects = [
        pygame.Rect(toggle_x, 120 + i * 55, toggle_w, toggle_h)
        for i in range(3)
    ]
    level_changer_y = 320
    minus_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, level_changer_y, 45, 45)
    plus_rect = pygame.Rect(SCREEN_WIDTH // 2 + 55, level_changer_y, 45, 45)
    
    reset_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 385, 200, 45)
    back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, 450, 200, 45)

    running = True

    score_pos = (10, 10)

    while running:
        delta_time = clock.tick(FPS) / 1000
        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()

        # 1. Handle Events
        for event in pygame.event.get():
            if music.handle_event(event):
                continue

            if event.type == pygame.QUIT:
                running = False

            if game_state == STATE_INIT:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    reset_game()
                    set_game_state(STATE_PLAYING)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_rect.collidepoint(event.pos):
                        reset_game()
                        warp_elapsed = 0.0
                        set_game_state(STATE_WARP)
                    elif options_rect.collidepoint(event.pos):
                        pre_options_state = STATE_INIT
                        set_game_state(STATE_OPTIONS)
                    elif quit_rect.collidepoint(event.pos):
                        running = False

            elif game_state in (STATE_GAME_OVER, STATE_WIN):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if game_state == STATE_WIN:
                        level += 1
                        if level > highest_level:
                            highest_level = level
                            save_highest_level(highest_level)
                    reset_game()
                    set_game_state(STATE_PLAYING)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_rect.collidepoint(event.pos):
                        if game_state == STATE_WIN:
                            level += 1
                            if level > highest_level:
                                highest_level = level
                                save_highest_level(highest_level)
                        reset_game()
                        set_game_state(STATE_PLAYING)
                    elif endscreen_options_rect.collidepoint(event.pos):
                        pre_options_state = game_state
                        set_game_state(STATE_OPTIONS)
                    elif quit_rect.collidepoint(event.pos):
                        running = False

            elif game_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not options["mouse_ctrl"]:
                        new_bullets = fire_player_bullets()
                        bullets.extend(new_bullets)
                        audio.play_shoot()

            elif game_state == STATE_OPTIONS:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    save_settings(options["music"], options["sfx"], options["mouse_ctrl"])
                    set_game_state(pre_options_state)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_rect.collidepoint(event.pos):
                        save_settings(options["music"], options["sfx"], options["mouse_ctrl"])
                        set_game_state(pre_options_state)
                    elif minus_rect.collidepoint(event.pos):
                        if level > 1:
                            level -= 1
                    elif plus_rect.collidepoint(event.pos):
                        if level < highest_level:
                            level += 1
                    elif reset_rect.collidepoint(event.pos):
                        reset_to_default()
                        state = get_state()
                        options = {"music": state["music"], "sfx": state["sfx"], "mouse_ctrl": state["mouse_ctrl"]}
                        music.set_muted(not options["music"])
                        audio.set_muted(not options["sfx"])
                    for i, key in enumerate(("music", "sfx", "mouse_ctrl")):
                        if toggle_rects[i].collidepoint(event.pos):
                            options[key] = not options[key]
                            if key == "music":
                                music.set_muted(not options["music"])
                            elif key == "sfx":
                                audio.set_muted(not options["sfx"])

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
                    set_game_state(STATE_PLAYING)

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
            # --- HUD ---
            score_text = score_font.render(f"SCORE: {score}", True, WHITE)
            sc_rect = score_text.get_rect(topleft=score_pos)
            screen.blit(score_text, sc_rect)

            level_text = hud_font.render(f"LVL {level}", True, WHITE)
            screen.blit(level_text, (SCREEN_WIDTH - level_text.get_width() - 15, 15))

            # Show small enemy progress for L4+
            if level >= 4:
                target = level
                progress_text = hud_font.render(
                    f"Scouts: {small_enemies_defeated}/{target}", True, (200, 200, 255)
                )
                screen.blit(progress_text, (SCREEN_WIDTH - progress_text.get_width() - 15, 48))
                
            # Health Bar
            health_bar_width = 150
            health_bar_height = 20
            health_bar_x = SCREEN_WIDTH // 2 - health_bar_width // 2
            health_bar_y = 15
            pygame.draw.rect(screen, (100, 100, 100), (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
            if player.health > 0:
                health_ratio = player.health / player.max_health
                pygame.draw.rect(screen, (0, 255, 100), (health_bar_x, health_bar_y, int(health_bar_width * health_ratio), health_bar_height))
            pygame.draw.rect(screen, WHITE, (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
            
            health_text = hud_font.render(f"HP: {player.health}/{player.max_health}", True, WHITE)
            screen.blit(health_text, (health_bar_x + health_bar_width // 2 - health_text.get_width() // 2, health_bar_y + 25))

            # --- Player movement ---
            if options["mouse_ctrl"]:
                # Mouse control: player follows cursor X, clamped to screen
                mx, my = pygame.mouse.get_pos()
                # Only follow if mouse is inside the window
                if pygame.mouse.get_focused():
                    target_x = max(0, min(SCREEN_WIDTH - player.width, mx - player.width // 2))
                    player.x = target_x
                    player.rect.x = player.x

                # Auto-fire
                auto_fire_timer += delta_time
                if auto_fire_timer >= AUTO_FIRE_INTERVAL:
                    auto_fire_timer -= AUTO_FIRE_INTERVAL
                    new_bullets = fire_player_bullets()
                    bullets.extend(new_bullets)
                    audio.play_shoot()
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    player.move(-1)
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    player.move(1)

            # 2. Update Bullets
            for bullet in bullets[:]:
                bullet.move()
                if bullet.rect.y < 0:
                    bullets.remove(bullet)

            # 2b. Update Enemy Bullets
            for eb in enemy_bullets[:]:
                eb.move()
                if eb.rect.y > SCREEN_HEIGHT:
                    enemy_bullets.remove(eb)
                elif eb.rect.colliderect(player.rect):
                    # Player hit by enemy bullet -> lose 1 health
                    enemy_bullets.remove(eb)
                    player.health -= 1
                    # Play a generic hit sound; we can reuse boom or game_over partially
                    audio.play_boom() 
                    if player.health <= 0:
                        set_game_state(STATE_GAME_OVER)
                        game_over_asteroids = [make_game_over_asteroid() for _ in range(14)]
                        screen_asteroid_spawn_time = 0.0
                        audio.play_game_over()
                        break
                        
            # 2c. Booster Update
            if game_state == STATE_PLAYING:
                booster_timer += delta_time
                if booster_timer >= booster_interval:
                    booster_timer = 0.0
                    if player.health < 5:
                        health_boosters.append(HealthBooster(booster_interval))
                    booster_interval = random.randint(1, 5)
                
                for hb in health_boosters[:]:
                    hb.move()
                    if hb.rect.y > SCREEN_HEIGHT:
                        health_boosters.remove(hb)
                    elif hb.rect.colliderect(player.rect):
                        player.health = min(player.max_health, player.health + hb.xp)
                        health_boosters.remove(hb)

            # 2c. Bullet vs Bullet collision
            if game_state == STATE_PLAYING:
                for b in bullets[:]:
                    for eb in enemy_bullets[:]:
                        if b.rect.colliderect(eb.rect):
                            if b in bullets:
                                bullets.remove(b)
                            if eb in enemy_bullets:
                                enemy_bullets.remove(eb)
                            break

            # 3. Update Enemies (grid movement)
            if game_state == STATE_PLAYING:
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
                            set_game_state(STATE_GAME_OVER)
                            game_over_asteroids = [make_game_over_asteroid() for _ in range(14)]
                            screen_asteroid_spawn_time = 0.0
                            audio.play_game_over()

            # 3b. Enemy firing (L2+)
            if game_state == STATE_PLAYING and level >= 2:
                for enemy in enemies:
                    enemy.fire_timer += delta_time
                    can_fire = True
                    for other in enemies:
                        if other != enemy and other.rect.bottom > enemy.rect.bottom:
                            if not (other.rect.left >= enemy.rect.right or other.rect.right <= enemy.rect.left):
                                can_fire = False
                                break
                    if can_fire:
                        fire_interval = 2.0 if enemy.enemy_type == "boss" else random.uniform(3.0, 6.0)
                        if enemy.fire_timer >= fire_interval:
                            enemy.fire_timer = 0.0
                            cx = enemy.rect.centerx
                            cy = enemy.rect.bottom
                            if enemy.enemy_type == "boss":
                                # Boss fires 3 bullets in a spread
                                enemy_bullets.append(EnemyBullet(cx - 12, cy))
                                enemy_bullets.append(EnemyBullet(cx - 2, cy))
                                enemy_bullets.append(EnemyBullet(cx + 8, cy))
                            else:
                                enemy_bullets.append(EnemyBullet(cx - 2, cy))

            # 3c. Small enemies (L4+)
            if game_state == STATE_PLAYING and level >= 4:
                # Count normal enemies (non-small)
                normal_count = len(enemies)
                if normal_count < 4 and len(small_enemies) < 8:
                    small_enemy_spawn_timer += delta_time
                    if small_enemy_spawn_timer >= 2.0:
                        small_enemy_spawn_timer = 0.0
                        spawn_small_enemy_wave()

                # Update small enemy positions
                for se in small_enemies[:]:
                    se.rect.x += se.vx * delta_time
                    se.rect.y += se.vy * delta_time

                    # Bounce off screen edges (keep them in play)
                    if se.rect.left < 0:
                        se.rect.left = 0
                        se.vx = abs(se.vx)
                    elif se.rect.right > SCREEN_WIDTH:
                        se.rect.right = SCREEN_WIDTH
                        se.vx = -abs(se.vx)
                    if se.rect.top < 0:
                        se.rect.top = 0
                        se.vy = abs(se.vy)
                    elif se.rect.bottom > SCREEN_HEIGHT - 60:
                        se.rect.bottom = SCREEN_HEIGHT - 60
                        se.vy = -abs(se.vy)

                    # Fire when directly above player (within 20px)
                    if abs(se.rect.centerx - player.rect.centerx) < 20:
                        se.fire_timer += delta_time
                        if se.fire_timer >= 1.5:
                            se.fire_timer = 0.0
                            enemy_bullets.append(EnemyBullet(se.rect.centerx - 2, se.rect.bottom))

                    # Collision with player -> game over
                    if se.rect.colliderect(player.rect):
                        set_game_state(STATE_GAME_OVER)
                        game_over_asteroids = [make_game_over_asteroid() for _ in range(14)]
                        screen_asteroid_spawn_time = 0.0
                        audio.play_game_over()
                        break

            # 4. Collisions — player bullets vs grid enemies
            if game_state == STATE_PLAYING:
                for bullet in bullets[:]:
                    hit = False
                    for enemy in enemies[:]:
                        if bullet.rect.colliderect(enemy.rect):
                            audio.play_boom()
                            if bullet in bullets:
                                bullets.remove(bullet)
                            if enemy.hit():
                                enemies.remove(enemy)
                            score += 1
                            if score > high_score:
                                high_score = score
                                save_high_score(high_score)
                            hit = True
                            break
                    if not hit:
                        # Check small enemies
                        for se in small_enemies[:]:
                            if bullet.rect.colliderect(se.rect):
                                audio.play_boom()
                                if bullet in bullets:
                                    bullets.remove(bullet)
                                if se.hit():
                                    small_enemies.remove(se)
                                    small_enemies_defeated += 1
                                score += 1
                                if score > high_score:
                                    high_score = score
                                    save_high_score(high_score)
                                break

            # 5. Win conditions
            if game_state == STATE_PLAYING:
                if level < 4:
                    # L1-L3: defeat all grid enemies
                    if not enemies:
                        set_game_state(STATE_WIN)
                        win_asteroids = [make_win_asteroid() for _ in range(18)]
                        screen_asteroid_spawn_time = 0.0
                        audio.play_win()
                else:
                    # L4+: defeat `level` small enemies to win
                    if small_enemies_defeated >= level:
                        set_game_state(STATE_WIN)
                        win_asteroids = [make_win_asteroid() for _ in range(18)]
                        screen_asteroid_spawn_time = 0.0
                        audio.play_win()

            # 6. Drawing
            if game_state == STATE_PLAYING:
                player.draw(screen)
                for bullet in bullets:
                    bullet.draw(screen)
                for enemy in enemies:
                    enemy.draw(screen)
                for se in small_enemies:
                    se.draw(screen)
                for eb in enemy_bullets:
                    eb.draw(screen)
                for hb in health_boosters:
                    hb.draw(screen)

        elif game_state == STATE_INIT:
            draw_init_screen(
                screen, title_font, button_font, options_font, mouse_pos, start_rect, options_rect, quit_rect, asteroids,
                level=level, high_score=high_score
            )

        elif game_state == STATE_WARP:
            draw_init_screen(
                screen,
                title_font,
                button_font,
                options_font,
                mouse_pos,
                start_rect,
                options_rect,
                quit_rect,
                asteroids,
                warp_elapsed / WARP_DURATION,
                level=level,
                high_score=high_score
            )

        elif game_state == STATE_OPTIONS:
            draw_options_screen(
                screen,
                title_font,
                options_font,
                mouse_pos,
                back_rect,
                toggle_rects,
                options,
                level=level,
                minus_rect=minus_rect,
                plus_rect=plus_rect,
                reset_rect=reset_rect,
                highest_level=highest_level
            )

        elif game_state == STATE_GAME_OVER:
            draw_game_over_screen(
                screen,
                title_font,
                button_font,
                options_font,
                mouse_pos,
                score,
                restart_rect,
                endscreen_options_rect,
                quit_rect,
                game_over_asteroids,
                level=level,
            )

        elif game_state == STATE_WIN:
            draw_win_screen(
                screen,
                title_font,
                button_font,
                options_font,
                mouse_pos,
                score,
                restart_rect,
                endscreen_options_rect,
                quit_rect,
                win_asteroids,
                level=level,
            )

        pygame.display.flip()

    music.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
