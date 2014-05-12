import pygame
import tmx

class Enemy(pygame.sprite.Sprite):
    def __init__(self, color, *groups):
        super(Enemy, self).__init__(*groups)

        self.speed_x = 0
        self.speed_y = 0
        self.direction_x = 0
        self.direction_y = 0
        self.color = color

    def move(self, dt):
        self.rect.x += self.speed_x * dt * self.direction_x
        self.rect.y += self.speed_y * dt * self.direction_y
    
    def update(self, dt, game, *args):
        last = self.rect.copy()

        self.move(dt)
        for tile in game.level.layers['triggers'].collide(self.rect, 'reverse'):
            if tile.color == game.disabled_color:
                continue
            self.rect = last
            if 'x' in tile['reverse']:
                self.direction_x *= -1
            if 'y' in tile['reverse']:
                self.direction_y *= -1
            break

        for tile in game.level.layers['triggers'].collide(self.rect, 'move'):
            if tile.color == game.disabled_color:
                continue
            self.rect = last
            if 'left' == tile['move']:
                self.direction_x = -1
                self.direction_y = 0
            if 'right' == tile['move']:
                self.direction_x = 1
                self.direction_y = 0
            if 'up' == tile['move']:
                self.direction_x = 0
                self.direction_y = -1
            if 'down' == tile['move']:
                self.direction_x = 0
                self.direction_y = 1
            break

class SimpleEnemy(Enemy):
    def __init__(self, color, x, y, *groups):
        super(SimpleEnemy, self).__init__(color, *groups)

        self.image = pygame.Surface((28, 60))
        self.image.fill((200, 100, 250))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 50
        self.direction_x = 1

def create_enemy(name, x, y, color, *groups):
    return SimpleEnemy(color, x, y, *groups)
