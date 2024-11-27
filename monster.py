from random import random

import pygame
import math
import random

import constants
import main

class Monster:
    def __init__(self, image, health, speed, pos, kill_money, img_f):
        self.health = health
        self.initHealth = health
        self.speed = speed
        self.kill_money = kill_money
        self.x, self.y = pos
        self.target = None
        self.path_index = 0
        self.rect = pygame.Rect(self.x * constants.TILE_SIZE, self.y * constants.TILE_SIZE, constants.TILE_SIZE, constants.TILE_SIZE)
        self.angle = 0  
        self.original_speed = speed
        self.freeze_end_time = None
        self.original_image = pygame.image.load(image).convert_alpha()
        self.freeze_img = pygame.image.load(img_f).convert_alpha()
        self.image = self.original_image
        self.isFrozen = False
        self.kill_money_time = None
        self.kill_money_text = pygame.font.Font(None, 18).render(f' +${self.kill_money}', True, (200, 200, 0))
        self.did_exit = False
        self.isBlip = False

    def update_position(self, path, dt, stage):
        if self.health <= 0:
            self.die(False, stage)
        if self.path_index >= len(path):
            self.die(True, stage)
            return

        if self.freeze_end_time and pygame.time.get_ticks() > self.freeze_end_time:
            self.speed = self.original_speed
            self.image = self.original_image
            self.freeze_end_time = None
            self.isFrozen = False

        tx, ty = path[self.path_index]

        if (self.x, self.y) == (tx, ty):
            self.path_index += 1
            if self.path_index >= len(path):
                self.die(True, stage)
                return
            tx, ty = path[self.path_index]

        dx, dy = tx - self.x, ty - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        travel_distance = self.speed * dt * stage.game_speed
        if distance > 0:
            self.angle = math.degrees(math.atan2(dy, dx))  

            if dx != 0:
                self.x += (dx / abs(dx)) * travel_distance
            if dy != 0:
                self.y += (dy / abs(dy)) * travel_distance
        if distance > 0:
            self.x += (dx / distance) * travel_distance
            self.y += (dy / distance) * travel_distance

        if abs(self.x - tx) < travel_distance and abs(self.y - ty) < travel_distance:
            self.x, self.y = tx, ty
            self.path_index += 1

        self.rect.topleft = (self.x * constants.TILE_SIZE, self.y * constants.TILE_SIZE)

    def draw(self, screen):
        init_img  = self.image
        scale_ratio = init_img.get_height() / (constants.TILE_SIZE + 10)
        image = pygame.transform.scale(init_img, (init_img.get_width() / scale_ratio, (constants.TILE_SIZE + 5)))
        rotated_image = pygame.transform.rotate(image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        if not self.health == self.initHealth:
            self.draw_health_bar(screen)

    def draw_health_bar(self, screen):
        health_bar_width = constants.TILE_SIZE
        health_bar_height = 4
        health_ratio = self.health / self.initHealth
        health_bar_color = (255, 0, 0)
        pygame.draw.rect(screen, (255, 255, 255), (self.rect.x, self.rect.y - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, health_bar_color, (self.rect.x, self.rect.y - 10, health_bar_width * health_ratio, health_bar_height))

    def die(self, did_exit, stage):
        self.kill_money_time = pygame.time.get_ticks()
        if did_exit:
            remaining_health = self.health
            stage.subtract_health(remaining_health)
            self.health = 0
            self.did_exit = True
        else:
             stage.add_money(self.kill_money)
             chance = random.randint(0,9)
             if chance == 1:
                stage.add_powerUp((self.x, self.y))

    def freeze(self, ratio, duration, game_speed):
        if not self.isFrozen:
            self.speed *= ratio
        self.isFrozen = True
        self.freeze_end_time = pygame.time.get_ticks() + duration / game_speed 
        self.image = self.freeze_img

class Monster_A(Monster):
    def __init__(self, pos):
        super().__init__("assets/mon_a.png", constants.mon_A_health, constants.mon_A_speed, pos, constants.mon_A_kill_money, "assets/mon_a_f.png")
        self.isAir = False
        self.image = pygame.image.load("assets/mon_a.png")

    def draw(self, screen):
        init_img  = self.image
        scale_ratio = init_img.get_height() / constants.TILE_SIZE
        image = pygame.transform.scale(init_img, ( init_img.get_width() / (scale_ratio * 1.5) ,constants.TILE_SIZE / 1.5))
        rotated_image = pygame.transform.rotate(image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        if not self.health == self.initHealth:
            self.draw_health_bar(screen)

class Monster_B(Monster):
    def __init__(self, pos):
        super().__init__("assets/mon_b.png", constants.mon_B_health, constants.mon_B_speed, pos, constants.mon_B_kill_money, "assets/mon_b_f.png")
        self.isAir = False

class Monster_C(Monster):
    def __init__(self, pos):
        super().__init__("assets/mon_c.png", constants.mon_C_health, constants.mon_C_speed, pos, constants.mon_C_kill_money, "assets/mon_c_f.png")
        self.isAir = False

class Monster_D(Monster):
    def __init__(self, pos):
        super().__init__("assets/mon_d.png", constants.mon_d_health, constants.mon_d_speed, pos, constants.mon_d_kill_money, "assets/mon_d_f.png")
        self.isAir = True

class Monster_E(Monster):
    def __init__(self, pos):
        super().__init__("assets/mon_e.png", constants.mon_e_health, constants.mon_e_speed, pos, constants.mon_e_kill_money, "assets/mon_e_f.png")
        self.isAir = True
        self.image = pygame.image.load("assets/mon_e.png")
    def draw(self, screen):
        init_img  = self.image
        scale_ratio = init_img.get_height() / (constants.TILE_SIZE + 30)
        image = pygame.transform.scale(init_img, (init_img.get_width() / scale_ratio, (constants.TILE_SIZE + 30)))
        rotated_image = pygame.transform.rotate(image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        if not self.health == self.initHealth:
            self.draw_health_bar(screen)

class Monster_F(Monster):
    def __init__(self, pos):
        super().__init__("assets/mon_f.png", constants.mon_F_health, constants.mon_F_speed, pos, constants.mon_F_kill_money, "assets/mon_f_f.png")
        self.isAir = False
    def draw(self, screen):
        init_img  = self.image
        image = pygame.transform.scale(init_img, (40,40))
        rotated_image = pygame.transform.rotate(image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        if not self.health == self.initHealth:
            self.draw_health_bar(screen)

class Monster_G(Monster):
    def __init__(self, pos):
        super().__init__("assets/mon_g.png", constants.mon_G_health, constants.mon_G_speed, pos, constants.mon_G_kill_money, "assets/mon_g_f.png")
        self.isAir = True
    def draw(self, screen):
        init_img  = self.image
        image = pygame.transform.scale(init_img, (60,30))
        rotated_image = pygame.transform.rotate(image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        if not self.health == self.initHealth:
            self.draw_health_bar(screen)

class Monster_H(Monster):
    def __init__(self, pos):
        super().__init__("assets/mon_h.png", constants.mon_h_health, constants.mon_h_speed, pos, constants.mon_h_kill_money, "assets/mon_h_f.png")
        self.isAir = True
    def draw(self, screen):
        init_img  = self.image
        scale_ratio = init_img.get_height() / (constants.TILE_SIZE + 10)
        image = pygame.transform.scale(init_img, (init_img.get_width() / scale_ratio, (constants.TILE_SIZE + 30)))
        rotated_image = pygame.transform.rotate(image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        if not self.health == self.initHealth:
            self.draw_health_bar(screen)

    def die(self, did_exit, stage):
        self.kill_money_time = pygame.time.get_ticks()
        if did_exit:
            remaining_health = self.health
            stage.subtract_health(remaining_health)
            self.health = 0
            self.did_exit = True
        else:
             stage.add_money(self.kill_money)
             chance = random.randint(0,9)
             if chance == 1:
                stage.add_powerUp((self.x, self.y))
             stage.generated_wave.monsters.append(Monster_B((self.x, self.y)))
             stage.generated_wave.monsters[-1].path_index = self.path_index

class Monster_I(Monster):
    def __init__(self, pos, stage):
        super().__init__("assets/mon_i.png", constants.mon_I_health, constants.mon_I_speed, pos, constants.mon_I_kill_money, "assets/mon_i_f.png")
        self.isAir = False
        self.stage = stage 
        self.last_heal = 0
        self.mons_healed = []
    def draw(self, screen):
        init_img  = self.image
        image = pygame.transform.scale(init_img, (35,55))
        rotated_image = pygame.transform.rotate(image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, rotated_rect.topleft)
        if not self.health == self.initHealth:
            self.draw_health_bar(screen)
        current_time = pygame.time.get_ticks()
        if current_time >= self.last_heal + 4000/self.stage.game_speed:
            self.mons_healed = []
            for mon in self.stage.generated_wave.monsters:
                if self.in_range(mon):
                    mon.health += 20
                    self.mons_healed.append(mon)
                    if mon.health >= mon.initHealth:
                        mon.health = mon.initHealth
            self.last_heal = current_time
        if current_time <= self.last_heal +850/self.stage.game_speed and not self.stage.paused:
            for mon in self.mons_healed:
                screen.blit(pygame.transform.scale(constants.mon_heal,(12,12)), (mon.x*constants.TILE_SIZE +7, mon.y*constants.TILE_SIZE -24))

    def in_range(self, monster):
        distance = math.hypot(monster.x - self.x, monster.y - self.y)
        if monster.isBlip:
            return False
        return distance <= 2.5

class Path_blip(Monster):
    def __init__(self, pos, count, path):
        super().__init__("assets/path_blip.png", 1, 2.8, pos, 0, "assets/path_blip.png")
        self.isAir = False
        self.isBlip = True
        self.count = count
        self.image = pygame.transform.scale(self.image,(19-1*(8-self.count), 19-1*(8-self.count)) )
        self.path_index = min(range(len(path)), key=lambda i: ((path[i][0] - pos[0]) ** 2 + (path[i][1] - pos[1]) ** 2) ** 0.5)  # index of closest tuple value to pos in path[]
    def update_position(self, path, dt, stage):
        if self.health <= 0:
            self.die(False, stage)
        if self.path_index >= len(path):
            self.die(True, stage)
            return
        tx, ty = path[self.path_index]
        if (self.x, self.y) == (tx, ty):
            self.path_index += 1
            if self.path_index >= len(path):
                self.die(True, stage)
                return
            tx, ty = path[self.path_index]
        dx, dy = tx - self.x, ty - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        travel_distance = self.speed * dt * stage.game_speed
        if distance > 0:
            self.angle = math.degrees(math.atan2(dy, dx)) 

            if dx != 0:
                self.x += (dx / abs(dx)) * travel_distance
            if dy != 0:
                self.y += (dy / abs(dy)) * travel_distance
        if distance > 0:
            self.x += (dx / distance) * travel_distance
            self.y += (dy / distance) * travel_distance

        if abs(self.x - tx) < travel_distance and abs(self.y - ty) < travel_distance:
            self.x, self.y = tx, ty
            self.path_index += 1
        self.rect.topleft = (self.x * constants.TILE_SIZE, self.y * constants.TILE_SIZE)

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        if not self.health ==0:
            screen.blit(rotated_image, rotated_rect.topleft)

    def die(self, did_exit, stage):
        self.health = 0
        return

    def freeze(self, ratio, duration, game_speed):
        return

    def shrink(self):
        self.image = pygame.transform.scale(self.image, (self.image.get_width()-2*(8-self.count), self.image.get_height()-2*(8-self.count)))
