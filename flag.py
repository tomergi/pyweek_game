import os
import pygame

class Flag(pygame.sprite.Sprite):
    def __init__(self, tile_obj, *groups):
        super(Flag, self).__init__(*groups)

        self.image = pygame.image.load(os.path.join('resources', 'flag.png'))
        self.rect = self.image.get_rect()

        self.rect.x = tile_obj.px
        self.rect.y = tile_obj.py
    
    def update(self, *args):
        pass
    
