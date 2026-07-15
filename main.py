import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, GREEN, RED, YELLOW
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
# MAIN GAME LOOP
# ==========================================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space Warriors")
    clock = pygame.time.Clock()

    # Initialize our custom numpy audio from sound.py
    audio = SoundEngine()

    player = Player()
    bullets = []
    enemies = []

    # Enemy movement tracking
    enemy_speed = 2
    enemy_drop = 30
    enemy_direction = 1

    # Spawn initial grid of enemies
    def spawn_enemies():
        for row in range(4):
            for col in range(10):
                x = 50 + col * 60
                y = 50 + row * 50
                enemies.append(Enemy(x, y))

    spawn_enemies()
    running = True

    while running:
        screen.fill(BLACK)

        # 1. Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(
                        Bullet(player.x + player.width // 2 - 2, player.y - 10)
                    )
                    audio.play_shoot()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1)
        if keys[pygame.K_RIGHT]:
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
                # Game over condition
                if enemy.rect.bottom >= player.rect.top:
                    print("GAME OVER")
                    running = False

        # 4. Collisions
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    audio.play_boom()
                    if bullet in bullets:
                        bullets.remove(bullet)
                    enemies.remove(enemy)
                    break

        # Respawn if all defeated
        if not enemies:
            enemy_speed += 1
            spawn_enemies()

        # 5. Drawing
        player.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
