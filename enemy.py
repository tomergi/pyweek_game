import pygame
import tmx

class Enemy(pygame.sprite.Sprite):
    def __init__(self, color, *groups):
        super(Enemy, self).__init__(*groups)

        self.color = color


class MovingEnemy(Enemy):
    def __init__(self, color, affected_by_triggers, *groups):
        super(MovingEnemy, self).__init__(color, *groups)
        self.speed_x = 0
        self.speed_y = 0
        self.direction_x = 0
        self.direction_y = 0
        self.affected_by_triggers = affected_by_triggers

    def move(self, dt):
        self.rect.x += self.speed_x * dt * self.direction_x
        self.rect.y += self.speed_y * dt * self.direction_y
    
    def update(self, dt, game, *args):
        if self.color == game.disabled_color and game.disabled_color != "":
            return
        last = self.rect.copy()

        self.move(dt)

        if self.affected_by_triggers:
            for tile in game.level.layers['triggers'].collide(self.rect, 'reverse'):
                if game.disabled_color != "" and tile['color'] == game.disabled_color:
                    continue
                self.rect = last
                if 'x' in tile['reverse']:
                    self.direction_x *= -1
                if 'y' in tile['reverse']:
                    self.direction_y *= -1
                break

            for tile in game.level.layers['triggers'].collide(self.rect, 'move'):
                if game.disabled_color != "" and tile['color'] == game.disabled_color:
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

        for tile in game.level.layers['triggers'].collide(self.rect, 'blocker'):
            colliding_side = False
            color = tile['color']
            if color == game.disabled_color:
                continue

            if self.rect.right == tile.left or self.rect.left == tile.right:
                colliding_side = True

            if last.right <= tile.left and self.rect.right > tile.left:
                self.rect.right = tile.left
            if last.left >= tile.right and self.rect.left < tile.right:
                self.rect.left = tile.right
            if last.bottom <= tile.top and self.rect.bottom > tile.top and not colliding_side:
                self.rect.bottom = tile.top
            if last.top >= tile.bottom and self.rect.top < tile.bottom and not colliding_side:
                self.rect.top = tile.bottom


class SimpleEnemy(MovingEnemy):
    def __init__(self, color, x, y, *groups):
        super(SimpleEnemy, self).__init__(color, True, *groups)

        self.image = pygame.Surface((28, 60))
        self.image.fill((200, 100, 250))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 100
        self.direction_x = -1

class ShooterEnemy(Enemy):
    def __init__(self, color, x, y, direction, cooldown, *groups):
        super(ShooterEnemy, self).__init__(color, *groups)

        self.enemy_groups = groups
        self.direction = direction
        self.time_since_last_shot = 0
        self.cooldown = cooldown
        
    def update(self, dt, game, *args):
        if self.color == game.disabled_color:
            return

        if self.time_since_last_shot + dt > self.cooldown:
            self.shoot()

    def shoot(self):
        shot_x = 0
        shot_y = 0
        if self.direction == "up":
            shot_x, shot_y = self.rect.midtop
        elif self.direction == "down":
            shot_x, shot_y = self.rect.midbottom
        elif self.direction == "left":
            shot_x, shot_y = self.rect.midleft
        elif self.direction == "right":
            shot_x, shot_y = self.rect.midright
        else:
            print 'must set shotter direction properly'
            return
        BulletEnemy(self.color, shot_x, shot_y, direction, self.enemy_groups)

class BulletEnemy(MovingEnemy):
    def __init__(self, color, x, y, direction, *groups):
        super(BulletEnemy, self).__init__(color, False, *groups)

        self.speed_x = 50
        self.speed_y = 50
        if direction == "up":
            self.direction_x = 0 
            self.direction_y = -1
        elif direction == "down":
            self.direction_x = 0
            self.direction_y = 1
        elif self.direction == "left":
            self.direction_x = -1
            self.direction_y = 0
        elif direction == "right":
            self.direction_x = 1
            self.direction_y = 0

def create_enemy(name, x, y, color, *groups):
    return SimpleEnemy(color, x, y, *groups)
