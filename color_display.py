#!/usr/bin/python
import pygame
import tmx
import enemy
import sys
import flag
import kezmenu
import time

class ColorDisplay(pygame.sprite.Sprite):
    tile_width = 28
    tile_height = 28
    tile_dimensions = (tile_width, tile_height)
    tile_space = tile_width // 2
    tile_enlargement = tile_space // 2
    enlarged_tile_shift = tile_enlargement // 2
    enlarged_tile_dimensions = (tile_width + tile_enlargement, tile_height + tile_enlargement)
    
    
    def __init__(self, screen, level, *groups):
        super(ColorDisplay, self).__init__(*groups)
        
        self.screen = screen
        self.level = level
        
        self.current_color = None
        
        self.surface_dict = {}
        
        self.surface_dict["red"] = pygame.Surface(ColorDisplay.tile_dimensions)
        self.surface_dict["red"].fill((255,0,0))
        self.surface_dict["green"] = pygame.Surface(ColorDisplay.tile_dimensions)
        self.surface_dict["green"].fill((0,255,0))
        self.surface_dict["blue"] = pygame.Surface(ColorDisplay.tile_dimensions)
        self.surface_dict["blue"].fill((0,0,255))
        self.surface_dict["orange"] = pygame.Surface(ColorDisplay.tile_dimensions)
        self.surface_dict["orange"].fill((255,128,0))
        
    def change_color(self, color):
        if self.current_color == color: # toggle off
            self.surface_dict[self.current_color] = pygame.transform.scale(self.surface_dict[self.current_color], ColorDisplay.tile_dimensions)
            self.current_color = None
            return
        
        if self.current_color != None:
            self.surface_dict[self.current_color] = pygame.transform.scale(self.surface_dict[self.current_color], ColorDisplay.tile_dimensions)
        self.current_color = color
        self.surface_dict[self.current_color] = pygame.transform.scale(self.surface_dict[self.current_color], ColorDisplay.enlarged_tile_dimensions)
        
    def print_on_screen(self):
        start_x = self.level.view_x + (2 * ColorDisplay.tile_width)
        
        x = start_x
        y = self.level.view_y + ColorDisplay.tile_height
        
        for color in ["red", "green", "blue", "orange"]:
            if self.current_color == color:
                enlarged_tile_shift = ColorDisplay.enlarged_tile_shift
                self.screen.blit(self.surface_dict[color], (x - enlarged_tile_shift, y -enlarged_tile_shift))
            else:
                self.screen.blit(self.surface_dict[color], (x, y))
        
            x += ColorDisplay.tile_width + ColorDisplay.tile_space
        
    