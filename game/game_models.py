import pygame
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, GREEN, BLACK, RED, YELLOW


class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 15)
        self.speed = 10

    def move(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, YELLOW, self.rect)


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
