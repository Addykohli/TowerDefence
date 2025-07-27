import pygame
import math

import constants

class B_Projectile:
    def __init__(self, x, y, target, angle, turr, game_speed):
        self.x = x
        self.y = y
        self.target = target
        self.angle = angle
        self.image = pygame.transform.scale(pygame.image.load('assets/blaster_anim.png'), (25, 47))
        self.tx = self.target.x
        self.ty = self.target.y
        self.turr = turr
        self.speed = 17
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
        if abs(self.tx-self.x/constants.TILE_SIZE) <=.9 and abs(self.ty-self.y/constants.TILE_SIZE)<=.9:
            self.turr.damage_target(self.target)
            return True  # Reached the target
        return False

    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect.topleft)

class C_Projectile:
    def __init__(self, x, y, target, angle, turr, game_speed):
        self.x = x
        self.y = y
        self.target = target
        self.angle = angle
        self.image = pygame.image.load('assets/cannon_anim.png')
        self.image = pygame.transform.scale(self.image, (self.image.get_width()/1.1, self.image.get_height()/1.25))  
        self.tx = self.target.x
        self.ty = self.target.y
        self.turr = turr
        self.speed = 35
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
        if abs(self.tx-self.x/constants.TILE_SIZE) <=1.4 and abs(self.ty-self.y/constants.TILE_SIZE)<=1.4:
            return True  # Reached the target
        return False

    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect.topleft)

class H_Projectile:
    def __init__(self, x, y, target, angle, turr, game_speed):
        self.x = x 
        self.y = y
        self.target = target
        self.angle = angle
        self.image = pygame.image.load('assets/harpoon_anim.png')
        self.image = pygame.transform.scale(self.image, (self.image.get_width()/1.35, self.image.get_height()/1.25))  
        self.tx = self.target.x
        self.ty = self.target.y
        self.turr = turr
        self.speed = 30
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
        if abs(self.tx-self.x/constants.TILE_SIZE) <=1.4 and abs(self.ty-self.y/constants.TILE_SIZE)<=1.4:
            self.turr.damage_target(self.target)
            return True  # Reached the target
        return False

    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect.topleft)

class BF_Projectile:
    def __init__(self, x, y, target, angle, turr, game_speed):
        self.x = x
        self.y = y
        self.target = target
        self.angle = angle
        self.image = pygame.image.load('assets/burstProj.png')
        self.image = pygame.transform.scale(self.image, (12, 12))  
        self.tx = self.target.x
        self.ty = self.target.y
        self.turr = turr
        self.speed = 30
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
        if abs(self.tx-self.x/constants.TILE_SIZE) <=1.4 and abs(self.ty-self.y/constants.TILE_SIZE)<=1.4:
            self.turr.place_burn(self.tx*constants.TILE_SIZE, self.ty*constants.TILE_SIZE)
            return True  # Reached the target
        return False

    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect.topleft)

class FC_Projectile:
    def __init__(self, x, y, target, angle, turr, game_speed):
        self.x = x 
        self.y = y 
        self.target = target
        self.angle = angle
        self.image = pygame.image.load('assets/frostball.png')
        self.image = pygame.transform.scale(self.image, (self.image.get_width()/2.2, self.image.get_height()/2.2))  
        self.tx = self.target.x
        self.ty = self.target.y
        self.turr = turr
        self.speed = 10
        self.dx = math.cos(math.radians(self.angle)) * self.speed
        self.dy = -math.sin(math.radians(self.angle)) * self.speed
        self.rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.rotated_image.get_rect(center=(self.x, self.y))

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.center = (self.x, self.y)
        if abs(self.tx-self.x/constants.TILE_SIZE) <=1.4 and abs(self.ty-self.y/constants.TILE_SIZE)<=1.4:
            self.turr.damage_target(self.target)
            return True  # Reached the target
        return False

    def draw(self, screen):
        screen.blit(self.rotated_image, self.rect.topleft)

class BlastAnimation:
    def __init__(self, x, y):
        self.x = x * constants.TILE_SIZE
        self.y = y * constants.TILE_SIZE
        self.image = pygame.image.load('assets/blast_anim.png').convert_alpha()
        self.frames = 10
        self.current_frame = 0
        self.finished = False
        self.scaled_images = self.scale_frames()

    def scale_frames(self):
        width, height = self.image.get_size()
        width, height = width/2, height/2
        scaled_images = []
        for i in range(1, self.frames + 1):
            scale_factor = 1 + (i*1.2 / self.frames) 
            new_size = (int(width * scale_factor), int(height * scale_factor))
            scaled_image = pygame.transform.scale(self.image, new_size)
            scaled_images.append(scaled_image)
        return scaled_images

    def update(self, screen):
        if self.current_frame < self.frames-1:
            self.current_frame += 1
        else:
            self.finished = True  
        self.draw(screen)

    def draw(self, surface):
        if not self.finished:
            current_image = self.scaled_images[self.current_frame]
            rect = current_image.get_rect(center=(self.x, self.y))
            surface.blit(current_image, rect)

    def is_finished(self):
        return self.finished

class SlowDownAnimation:
    def __init__(self, x, y):
        self.x = x * constants.TILE_SIZE
        self.y = y * constants.TILE_SIZE
        self.image = pygame.image.load('assets/slow_anim.png').convert_alpha()
        self.frames = 20
        self.current_frame = 0
        self.finished = False
        self.scaled_images = self.scale_frames()

    def scale_frames(self):
        width, height = self.image.get_size()
        width, height = width/5, height/5
        scaled_images = []
        for i in range(1, self.frames + 1):
            scale_factor = 1 + (9*i / self.frames) 
            new_size = (int(width * scale_factor), int(height * scale_factor))
            scaled_image = pygame.transform.scale(self.image, new_size)
            scaled_images.append(scaled_image)
        return scaled_images

    def update(self, screen):
        if self.current_frame < self.frames-1:
            self.current_frame += 1
        else:
            self.finished = True 
        self.draw(screen)

    def draw(self, surface):
        if not self.finished:
            current_image = self.scaled_images[self.current_frame]
            rect = current_image.get_rect(center=(self.x, self.y))
            surface.blit(current_image, rect)

    def is_finished(self):
        return self.finished
    
class MineAnimation:
    def __init__(self, x, y):
        self.x = x * constants.TILE_SIZE + constants.TILE_SIZE/2
        self.y = y * constants.TILE_SIZE + constants.TILE_SIZE/2
        self.image = pygame.image.load('assets/mine_anim.png').convert_alpha()
        self.frames = 10
        self.current_frame = 0
        self.finished = False
        self.scaled_images = self.scale_frames()

    def scale_frames(self):
        width, height = self.image.get_size()
        width, height = width/2, height/2
        scaled_images = []
        for i in range(1, self.frames + 1):
            scale_factor = 0.7 + (i*1.01 / self.frames) 
            new_size = (int(width * scale_factor), int(height * scale_factor))
            scaled_image = pygame.transform.scale(self.image, new_size)
            scaled_images.append(scaled_image)
        return scaled_images

    def update(self, screen):
        if self.current_frame < self.frames-1:
            self.current_frame += 1
        else:
            self.finished = True 
        self.draw(screen)

    def draw(self, surface):
        if not self.finished:
            current_image = self.scaled_images[self.current_frame]
            rect = current_image.get_rect(center=(self.x, self.y))
            surface.blit(current_image, rect)

    def is_finished(self):
        return self.finished