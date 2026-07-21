import pygame
import random
import math
from .constants import SCREEN_HEIGHT, SCREEN_WIDTH, GREEN, BLACK, RED, YELLOW, WHITE, BLUE


class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 15)
        self.speed = 10

    def move(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)


class EnemyBullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 12)
        self.speed = 6

    def move(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)


class Player:
    def __init__(self, special_ship=False):
        self.special_ship = special_ship
        if self.special_ship:
            self.width = 50
            self.height = 25
            self.color = (0, 200, 255)
        else:
            self.width = 40
            self.height = 20
            self.color = GREEN
            
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 6
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.max_health = 10
        self.health = self.max_health

    def move(self, dx):
        self.x += dx * self.speed
        # Keep player on screen
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.rect.x = self.x

    def draw(self, surface):
        if self.special_ship:
            # Draw complex ship shape (triangular/arrow shape with wing details and glowing center)
            points = [
                (self.x + self.width // 2, self.y),  # Top tip
                (self.x, self.y + self.height),      # Bottom left
                (self.x + self.width // 2, self.y + self.height - 5), # Bottom middle indent
                (self.x + self.width, self.y + self.height) # Bottom right
            ]
            pygame.draw.polygon(surface, self.color, points)
            # Glowing center
            center_rect = pygame.Rect(self.x + self.width // 2 - 2, self.y + self.height // 2, 4, 8)
            pygame.draw.rect(surface, WHITE, center_rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
            # Add a little cannon on top
            pygame.draw.rect(surface, self.color, (self.x + 15, self.y - 10, 10, 10))


class Enemy:
    def __init__(self, x, y, enemy_type="normal", health=1):
        self.enemy_type = enemy_type
        self.fire_timer = 0.0
        
        if self.enemy_type == "boss":
            self.width = 45
            self.height = 45
            self.color = (180, 50, 255)
            self.health = 3
        elif self.enemy_type == "small":
            self.width = 20
            self.height = 20
            self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            self.health = health
            self.vx = 0.0
            self.vy = 0.0
        else:
            self.width = 30
            self.height = 30
            self.color = RED
            self.health = health
            
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def draw(self, surface):
        if self.enemy_type == "boss":
            pygame.draw.rect(surface, self.color, self.rect)
            # Thicker border ring
            pygame.draw.rect(surface, WHITE, self.rect, 3)
            # Crown/diamond on top
            crown_points = [
                (self.rect.centerx, self.rect.top - 10),
                (self.rect.left + 5, self.rect.top),
                (self.rect.right - 5, self.rect.top)
            ]
            pygame.draw.polygon(surface, YELLOW, crown_points)
            # Health dots below
            dot_spacing = 8
            start_x = self.rect.centerx - (self.health - 1) * dot_spacing // 2
            for i in range(self.health):
                pygame.draw.circle(surface, RED, (start_x + i * dot_spacing, self.rect.bottom + 5), 3)
                
            # Alien eyes
            pygame.draw.rect(surface, BLACK, (self.rect.x + 10, self.rect.y + 10, 5, 5))
            pygame.draw.rect(surface, BLACK, (self.rect.x + 30, self.rect.y + 10, 5, 5))

        elif self.enemy_type == "small":
            # Round character
            pygame.draw.circle(surface, self.color, self.rect.center, self.width // 2)
            # Big white eyes
            left_eye_pos = (self.rect.centerx - 4, self.rect.centery - 2)
            right_eye_pos = (self.rect.centerx + 4, self.rect.centery - 2)
            pygame.draw.circle(surface, WHITE, left_eye_pos, 4)
            pygame.draw.circle(surface, WHITE, right_eye_pos, 4)
            # Black pupils
            pygame.draw.circle(surface, BLACK, left_eye_pos, 2)
            pygame.draw.circle(surface, BLACK, right_eye_pos, 2)
            # Small smile
            smile_rect = pygame.Rect(self.rect.centerx - 4, self.rect.centery + 2, 8, 4)
            pygame.draw.arc(surface, BLACK, smile_rect, math.pi, 2 * math.pi, 1)

        else:
            pygame.draw.rect(surface, self.color, self.rect)
            # Alien eyes
            pygame.draw.rect(surface, BLACK, (self.rect.x + 5, self.rect.y + 5, 5, 5))
            pygame.draw.rect(surface, BLACK, (self.rect.x + 20, self.rect.y + 5, 5, 5))

    def hit(self):
        self.health -= 1
        return self.health <= 0


class HealthBooster:
    def __init__(self, xp):
        self.width = 24
        self.height = 24
        self.x = random.uniform(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 4
        self.xp = xp
        self.color = (0, 255, 100)
        self.font = pygame.font.SysFont(None, 18)

    def move(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, WHITE, (self.rect.x + 10, self.rect.y + 4, 4, 16))
        pygame.draw.rect(surface, WHITE, (self.rect.x + 4, self.rect.y + 10, 16, 4))
        text = self.font.render(f"+{self.xp}", True, WHITE)
        surface.blit(text, (self.rect.x, self.rect.y + 26))
