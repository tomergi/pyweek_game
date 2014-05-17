#!/usr/bin/python
import pygame
import tmx
import enemy
import sys
import flag
import kezmenu
import time
import color_display
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, *groups):
        super(Player, self).__init__(*groups)
        
        self.image = pygame.image.load(os.path.join('resources', 'troll.png'))
        
        self.rect = self.image.get_rect()
        self.rect.x = start_x
        self.rect.y = start_y

        self.resting = False
        self.speed_y = 0
        self.speed_x = 0
        self.direction = 0
        self.win = False
        self.god = False

    def check_death(self, game):
        if self.god:
            return False
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

    def check_win(self, game):
        for tile in pygame.sprite.spritecollide(self, game.flag_layer, False):
            return True
        return False

    def update(self, dt, game, *args):
        previous_rect = self.rect.copy()

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
        
        # re-calculating is done each time to avoid "sticky cells".
        if len(self.get_enabled_colliding_cells(game)) != 0:
            self.handle_right_collision_if_occurred(previous_rect, self.get_enabled_colliding_cells(game))
            self.handle_left_collision_if_occurred(previous_rect, self.get_enabled_colliding_cells(game))
            self.handle_bottom_collision_if_occurred(previous_rect, self.get_enabled_colliding_cells(game))
            self.handle_top_collision_if_occurred(previous_rect, self.get_enabled_colliding_cells(game))

        if self.resting and keys[pygame.K_SPACE]:
            self.resting = False
            self.speed_y = -500
        else:
            self.speed_y = min((500, self.speed_y + 20))

        self.dead = self.check_death(game)
        self.win = self.check_win(game)

    
    def handle_right_collision_if_occurred(self, previous_rect, cells):
        colliding_cells = filter((lambda cell: ((previous_rect.right < cell.left) and 
                                                (self.rect.right >= cell.left))), cells)
        if (len(colliding_cells) == 0):
            return
        left_ends = map((lambda cell: cell.left), colliding_cells)
        min_left_end = min(left_ends)
        self.rect.right = min_left_end - 1
        
    def handle_left_collision_if_occurred(self, previous_rect, cells):
        colliding_cells = filter((lambda cell: ((previous_rect.left > cell.right) and 
                                                (self.rect.left <= cell.right))), cells)
        if (len(colliding_cells) == 0):
            return
        right_ends = map((lambda cell: cell.right), colliding_cells)
        max_right_end = max(right_ends)
        self.rect.left = max_right_end + 1
    
    def handle_bottom_collision_if_occurred(self, previous_rect, cells):
        colliding_cells = filter((lambda cell: ((previous_rect.bottom < cell.top) and 
                                                (self.rect.bottom >= cell.top))), cells)
        if (len(colliding_cells) == 0):
            return
        top_ends = map((lambda cell: cell.top), colliding_cells)
        min_top_end = min(top_ends)
        self.rect.bottom = min_top_end - 1
        
        self.resting = True
        self.speed_y = 0
        
    def handle_top_collision_if_occurred(self, previous_rect, cells):
        colliding_cells = filter((lambda cell: ((previous_rect.top > cell.bottom) and 
                                                (self.rect.top <= cell.bottom))), cells)
        if (len(colliding_cells) == 0):
            return
        bottom_ends = map((lambda cell: cell.bottom), colliding_cells)
        max_bottom_end = max(bottom_ends)
        self.rect.top = max_bottom_end + 1
        
        self.speed_y = 50
    
    def get_enabled_colliding_cells(self, game):
        cells = game.level.layers['triggers'].collide(self.rect, 'blocker')
        return filter((lambda cell: cell['color'] != game.disabled_color or cell['color'] == ""), cells)
        
class Game(object):

    def __init__(self, level_path, screen_size, screen, fps=60):
        self.level = tmx.load(level_path, screen_size)
        spawn = self.level.layers['triggers'].find('spawn')[0]

        self.sprite_layer = tmx.SpriteLayer()
        self.player = Player(spawn.px, spawn.py, self.sprite_layer)
        self.level.layers.append(self.sprite_layer)

        self.flag_layer = tmx.SpriteLayer()
        flag_sprite = flag.Flag(self.level.layers['triggers'].find('win')[0], self.flag_layer)
        self.level.layers.append(self.flag_layer)

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

        self.color_display = color_display.ColorDisplay(screen, self.level)
        
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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F10:
                    self.player.god = not self.player.god

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.toggle_layer("red")
                        self.color_display.change_color("red")
                    elif event.key == pygame.K_2:
                        self.toggle_layer("green")
                        self.color_display.change_color("green")
                    elif event.key == pygame.K_3:
                        self.toggle_layer("blue")
                        self.color_display.change_color("blue")
                    elif event.key == pygame.K_4:
                        self.toggle_layer("orange")
                        self.color_display.change_color("orange")

            self.screen.fill((0,0,0))
            self.level.update(dt, self)
            self.level.set_focus(self.player.rect.x, self.player.rect.y)
            
            self.color_display.print_on_screen()
            
            self.level.draw(self.screen)

            pygame.display.flip()
            if self.player.dead:
                time.sleep(1)
                return False
            if self.player.win:
                time.sleep(1)
                return True

        raise Exception("game exit")

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

def run_game(screen, screen_size, start_level=1):
    level = start_level
    win = True
    while True:
        game = Game('level-%d.tmx' % level, screen_size, screen)
        win = game.loop()
        if win:
            level += 1
    

def display_instructions(screen):
    font = pygame.font.Font(None, 30)
    text = """Objective:
Reach to the flag in every level.

Controls:
Use arrow keys to move, space to jump.
Numbers 1-4 toggle colors.
press Esc at any time to return to menu.

Press <space> to return""".splitlines()
    rendered = [font.render(i, 1, (0, 0, 0)) for i in text]
    screen.fill((255, 255, 255))
    for y, label in enumerate(rendered):
        screen.blit(label, (0, y * font.get_linesize()))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return


def quit():
    pygame.quit()
    sys.exit(1)
def main():
    start_level = 0
    if len(sys.argv) > 1:
        start_level = int(sys.argv[1])
    pygame.init()
    #TODO: when music won't suck...
    #music = pygame.mixer.music.load(os.path.join("resources", "track.wav"))
    #pygame.mixer.music.set_volume(0.2)
    #pygame.mixer.music.play(-1)
    screen_size = (640, 480)
    screen = pygame.display.set_mode(screen_size)
    
    pixelated_troll = pygame.image.load(os.path.join('resources', 'troll_menu.jpg'))
    pixelated_troll_location = (screen_size[0] - pixelated_troll.get_rect().width, 0)
    
    option_selected = None
    menu = kezmenu.KezMenu(["Start", lambda: run_game(screen, screen_size, start_level=start_level)],
            ["Instructions", lambda: display_instructions(screen)],
                            ["Quit", quit])
    menu.center_at(screen_size[0] / 2, screen_size[1] / 2)
    menu.mouse_enabled=False
    while True:
        events = pygame.event.get()
        menu.update(events)
        screen.fill((255,255,255))
        screen.blit(pixelated_troll, pixelated_troll_location)
        menu.draw(screen)
        pygame.display.flip()
        if option_selected is not None:
            break

    print option_selected


if __name__ == '__main__':
    main()
