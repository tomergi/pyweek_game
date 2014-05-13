#!/usr/bin/python
import pygame
import tmx
import enemy
import sys

class Player(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, *groups):
        super(Player, self).__init__(*groups)
        
        self.image = pygame.Surface((28, 60))
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

        self.resting = False
        self.speed_y = 0
        self.speed_x = 0
        self.direction = 0

    def check_death(self, game):
        for tile in game.level.layers['triggers'].collide(self.rect, 'death'):
            color = tile['color']
            if color == game.disabled_color:
                continue
            return True

        for color, enemies in game.enemies_by_color.items():
            if color == game.disabled_color:
                continue
            for enemy in pygame.sprite.spritecollide(self, enemies, False):
                return True
        return False

    def update(self, dt, game, *args):
        last = self.rect.copy()

        self.rect.x += self.speed_x * dt * self.direction
        self.rect.y += self.speed_y * dt

        self.direction = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.speed_x = 100.0 + self.rect.width
            self.direction = 1
        if keys[pygame.K_LEFT]:
            self.speed_x = 100.0
            self.direction = -1
        if keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]:
            self.speed_x = 0
            self.direction = 0


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
                self.resting = True
                self.rect.bottom = tile.top
                self.speed_y = 0
            if last.top >= tile.bottom and self.rect.top < tile.bottom and not colliding_side:
                self.rect.top = tile.bottom
                self.speed_y = 50


        if self.resting and keys[pygame.K_SPACE]:
            self.resting = False
            self.speed_y = -500
        else:
            self.speed_y = min((500, self.speed_y + 20))

        self.dead = self.check_death(game)


class Game(object):

    def __init__(self, level_path, screen_size, screen, fps=60):
        self.level = tmx.load(level_path, screen_size)
        spawn = self.level.layers['triggers'].find('spawn')[0]

        self.sprite_layer = tmx.SpriteLayer()
        self.player = Player(spawn.px, spawn.py, self.sprite_layer)
        self.level.layers.append(self.sprite_layer)

        self.clock = pygame.time.Clock()
        self.fps = fps
        self.disabled_color = ""

        self.enemies_red = tmx.SpriteLayer()
        try:
            for enemy_obj in self.level.layers['enemies'].match(color='red'):
                enemy.create_enemy(enemy_obj, self.enemies_red)
        except Exception as e:
            print e
        self.enemies_green = tmx.SpriteLayer()
        try:
            for enemy_obj in self.level.layers['enemies'].match(color='green'):
                enemy.create_enemy(enemy_obj, self.enemies_green)
        except Exception as e:
            print e
        self.enemies_blue = tmx.SpriteLayer()
        try:
            for enemy_obj in self.level.layers['enemies'].match(color='blue'):
                enemy.create_enemy(enemy_obj, self.enemies_blue)
        except Exception as e:
            print e
        self.enemies_orange = tmx.SpriteLayer()
        try:
            for enemy_obj in self.level.layers['enemies'].match(color='orange'):
                enemy.create_enemy(enemy_obj, self.enemies_orange)
        except Exception as e:
            print e

        self.level.layers.append(self.enemies_red)
        self.level.layers.append(self.enemies_green)
        self.level.layers.append(self.enemies_blue)
        self.level.layers.append(self.enemies_orange)

        self.enemies_by_color = {'red': self.enemies_red, 'green': self.enemies_green, 'blue': self.enemies_blue, 'orange': self.enemies_orange}


        self.screen = screen

    def loop(self):
        running = True
        while running:
            dt = self.clock.tick(self.fps) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.toggle_layer("red")
                    elif event.key == pygame.K_2:
                        self.toggle_layer("green")
                    elif event.key == pygame.K_3:
                        self.toggle_layer("blue")
                    elif event.key == pygame.K_4:
                        self.toggle_layer("orange")

            self.screen.fill((0,0,0))
            self.level.update(dt, self)
            self.level.set_focus(self.player.rect.x, self.player.rect.y)
            self.level.draw(self.screen)

            if self.player.dead:
                print 'you are dead'

            pygame.display.flip()

    def toggle_layer(self, color):
        print "toggling %s" % color
        visible = not self.level.layers[color].visible
        if self.disabled_color != "":
            self.level.layers[self.disabled_color].visible = True
            self.enemies_by_color[self.disabled_color].visible = True
        self.level.layers[color].visible = visible
        if visible:
            self.disabled_color = ""
        else:
            self.disabled_color = color
            self.enemies_by_color[color].visible = False

def main():
    pygame.init()
    screen_size = (640, 480)
    screen = pygame.display.set_mode(screen_size)

    game = Game('level-0.tmx', screen_size, screen)
    game.loop()

if __name__ == '__main__':
    main()
