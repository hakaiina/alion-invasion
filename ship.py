import pygame
from pygame.sprite import Sprite

class Ship(Sprite):
    def __init__(self, ai_settings, screen):
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings
        
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()
        
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom
        
        self.center = float(self.rect.centerx)
        
        self.moving_right = False
        self.moving_left = False
        self.charging_gun = False
        self.gun_charge = 0
        self.gun_charged = False
        self.charge_limit = ai_settings.charge_limit

    def blitme(self):
        self.screen.blit(self.image, self.rect)


    def center_ship(self):
        self.center = self.screen_rect.centerx