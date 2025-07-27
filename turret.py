import pygame
import math

import constants
import main
import animations

class Turret:
    def __init__(self, x, y, damage, hit_speed, range, cost):
        self.x = x
        self.y = y
        self.damage = damage
        self.hit_speed = hit_speed
        self.range = range
        self.initial_cost = cost
        self.rect = pygame.Rect(x * constants.TILE_SIZE, y * constants.TILE_SIZE, constants.TILE_SIZE, constants.TILE_SIZE)
        self.target = None
        self.last_shot_time = 0
        self.level = 0
        self.air_attack = False
        self.ground_attack = False
        self.upgrade_cost = (self.initial_cost //3 + (self.level * self.initial_cost // 3))
        self.under_upgrade = True
        self.upgraded_time = pygame.time.get_ticks()
        self.trigger_time = None 
        self.prev_position = False
        self.box_height = 0
        self.box_growth_start_time = None
        self.image = None
        self.up3_image = self.image
        self.up5_image = self.image
        self.is_blown = False
        self.last_up_time = self.upgraded_time
        self.pause_while_upgrading = 0
        self.stage = None 
    def find_target(self, monsters):
        if not monsters:
            return None
        closest_monster = None
        min_distance = float('inf')

        for monster in monsters:
            distance = math.hypot(monster.x - self.x, monster.y - self.y)

            if monster.isAir:
                if distance < min_distance and distance <= self.range and self.air_attack:
                    min_distance = distance
                    closest_monster = monster

            else:
                if distance < min_distance and distance <= self.range and self.ground_attack and not monster.isBlip:
                    min_distance = distance
                    closest_monster = monster
        return closest_monster

    def in_range(self, monster):
        distance = math.hypot(monster.x - self.x, monster.y - self.y)
        if monster.isBlip:
            return False
        return distance <= self.range

    def shoot(self, current_time, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.target.health -= self.damage
            self.last_shot_time = current_time

            self.box_height = 0  # Reset the height to 0 when shooting
            self.box_growth_start_time = current_time  # Start timing the growth


    def upgrade(self, stage):
        if stage.checkMoney() >= self.upgrade_cost:
            self.under_upgrade = True
            self.upgraded_time = pygame.time.get_ticks() 
            stage.add_money(-self.upgrade_cost)
            self.level += 1
            self.box_height = 0
            if self.damage:
                self.damage += self.damage * 0.25
            if self.level < 6:
                self.range += self.range * 0.05
                if self.hit_speed:
                    self.hit_speed -= self.hit_speed * 0.05
            self.upgrade_cost += (self.level * self.initial_cost // 3)
            if self.level == 2:
                self.image = self.up3_image
            if self.level == 4:
                self.image = self.up5_image

    def delete(self, stage):
        stage.add_money(int((self.initial_cost + (self.level * 0.85 * self.initial_cost // 2)) * 0.70))
        stage.remove_turret(self)
        stage.nodes.append(main.Node(self.x, self.y))

    def update_box(self, current_time, game_speed):
        if self.box_growth_start_time is not None:
            # Calculate elapsed time since the growth started
            elapsed_time = current_time - self.box_growth_start_time
            # Calculate the new height of the box
            if elapsed_time < self.hit_speed * 1000:  # Ensure it doesn't exceed hit_speed duration
                self.box_height = (elapsed_time / (self.hit_speed * 1000 / game_speed)) * 30  # Grow to a maximum height of 30
                if self.box_height > 30:
                    self.box_height = 30
            else:
                self.box_height = 30  # Set to maximum height after time exceeds hit_speed
                self.box_growth_start_time = None  # Reset the growth timer

    def update_upgrade_box(self, current_time, game_speed):
        elapsed_time = current_time - self.upgraded_time
            # Calculate the new height of the box
        if elapsed_time <= 3000:  # Ensure it doesn't exceed upgrade duration
            self.box_height = (elapsed_time / (3000 / game_speed)) * 30  # Grow to a maximum height of 30

            if self.box_height > 30:
                self.box_height = 30
        else:
            self.box_height = 30  # Set to maximum height upon upgrade


    def draw_level(self, screen):
        level_image = pygame.image.load('assets/lvl.png')
        star_image = pygame.image.load('assets/starlvl.png')
        start_x = self.x * constants.TILE_SIZE
        start_y = self.y * constants.TILE_SIZE
        if self.under_upgrade:
            effective_level = self.level -1
        else:
            effective_level = self.level
        if effective_level +1 < 5:
            for i in range(effective_level+1):
                screen.blit(level_image, (start_x+constants.TILE_SIZE+1, (start_y +20 - (6 * i))))
        else:
            screen.blit(star_image, (start_x+constants.TILE_SIZE+2, start_y))

    def update(self, monsters, current_time, game_speed):
        self.update_box(current_time, game_speed)
        if self.target and self.target in monsters:
            if self.in_range(self.target):
                self.shoot(current_time, game_speed)
            else:
                self.target = self.find_target(monsters)
        else:

            self.target = self.find_target(monsters)
    
    def rotate_image(self):
        if self.under_upgrade:
            if not self.prev_position:
                return (self.image, self.image.get_rect(center=(self.x *constants.TILE_SIZE +constants.TILE_SIZE/2,
                                                      self.y *constants.TILE_SIZE+ constants.TILE_SIZE/2)))
            return self.prev_position[0], self.prev_position[1]
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            # Calculate the angle to the target in degrees
            self.angle = math.degrees(math.atan2(-dy, dx)) % 360

        # Rotate the image by the calculated angle
        rotated_image = pygame.transform.rotate(self.image, self.angle)

        # Calculate the new rectangle to center the rotated image on the turret's position
        rotated_rect = rotated_image.get_rect(center=(self.x * constants.TILE_SIZE + constants.TILE_SIZE / 2,
                                                      self.y * constants.TILE_SIZE + constants.TILE_SIZE / 2))
        self.prev_position = (rotated_image, rotated_rect)
        return rotated_image, rotated_rect

class Cannon(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.CANNON_DAMAGE, constants.CANNON_HIT_SPEED, constants.CANNON_RANGE, constants.CANNON_COST)
        self.original_image = pygame.image.load('assets/cannon.png')
        self.image = pygame.transform.scale(self.original_image,
                                            (self.original_image.get_width() / 1.6,
                                             self.original_image.get_height() / 1.6))
        self.image_width = self.image.get_width()  
        self.image_height = self.image.get_height()  
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/cannon_up3.png'),
                                                (self.original_image.get_width() / 1.6,
                                                 self.original_image.get_height() / 1.6))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/cannon_up5.png'),
                                                (self.original_image.get_width() / 1.5,
                                                 self.original_image.get_height() / 1.5))

        self.angle = 0
        self.air_attack = False
        self.ground_attack = True

        self.projectiles = []
        self.last_shot_time = 0
        self.is_blown = False

    def shoot(self, current_time, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.last_shot_time = current_time
            self.target.health -= self.damage
            if self.stage:
                self.stage.total_damage_done += self.damage
            angle_rad = math.radians(self.angle)
            projectile = animations.C_Projectile(self.x * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * math.cos(angle_rad)) ,
                                    self.y * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * -math.sin(angle_rad)) ,
                                    self.target, self.angle, self, game_speed)
            self.projectiles.append(projectile)

            self.box_height = 0  
            self.box_growth_start_time = current_time  

    def update_projectiles(self, screen):
        # Update and draw each projectile
        for projectile in self.projectiles[:]:
            if projectile.update():  # If projectile reached target
                self.projectiles.remove(projectile)  # Remove the projectile
            else:
                projectile.draw(screen)

    def draw(self, screen):
        # Rotate and blit the turret image
        rotated_image, rotated_rect = self.rotate_image()

        # Blit the rotated image at the calculated position (adjusted for rotation)
        screen.blit(rotated_image, (rotated_rect.topleft[0], rotated_rect.topleft[1]))

        # Draw projectiles
        self.update_projectiles(screen)

        # Draw the box timer for the turret
        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))
        self.draw_level(screen)


# Updated Blaster class with turret level display
class Blaster(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.BLASTER_DAMAGE, constants.BLASTER_HIT_SPEED, constants.BLASTER_RANGE, constants.BLASTER_COST)
        self.original_image = pygame.image.load('assets/blaster.png')

        self.image = pygame.transform.scale(self.original_image,
                                            (self.original_image.get_width() / 1.6,
                                             self.original_image.get_height() / 1.6))
        self.image_width = self.image.get_width()  
        self.image_height = self.image.get_height()  
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/blaster_up3.png'),
                                            (self.original_image.get_width() / 1.6,
                                             self.original_image.get_height() / 1.6))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/blaster_up5.png'),
                                                (self.original_image.get_width() / 1.4,
                                                 self.original_image.get_height() / 1.4))
        self.angle = 0
        self.air_attack = True
        self.ground_attack = True

        self.projectiles = []
        self.last_shot_time = 0

        self.is_blown = False

    def shoot(self, current_time, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.last_shot_time = current_time
            angle_rad = math.radians(self.angle)
            projectile = animations.B_Projectile(self.x * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * math.cos(angle_rad)) ,
                                    self.y * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * -math.sin(angle_rad)) ,
                                    self.target, self.angle, self, game_speed)
            self.projectiles.append(projectile)
            self.box_height = 0  
            self.box_growth_start_time = current_time 

    def damage_target(self, target):
        target.health -= self.damage
        if self.stage:
            self.stage.total_damage_done += self.damage

    def update_projectiles(self, screen):
        # Update and draw each projectile
        for projectile in self.projectiles[:]:
            if projectile.update():  # If projectile reached target
                self.projectiles.remove(projectile)  # Remove the projectile
            else:
                projectile.draw(screen)

    def draw(self, screen):
        rotated_image, rotated_rect = self.rotate_image()

        screen.blit(rotated_image, (rotated_rect.topleft[0], rotated_rect.topleft[1]))

        self.update_projectiles(screen)

        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE + 6,
                                            self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height, 3.5, self.box_height))
        self.draw_level(screen)


class Minigun(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.MINIGUN_DAMAGE, constants.MINIGUN_HIT_SPEED, constants.MINIGUN_RANGE,
                         constants.MINIGUN_COST)
        self.original_image = pygame.image.load('assets/minigun.png')
        self.image = pygame.transform.scale(self.original_image, (
                                            self.original_image.get_width() / 1.4,
                                            self.original_image.get_height() / 1.4))
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/minigun_up3.png'),
                                                (self.original_image.get_width() / 1.4,
                                                 self.original_image.get_height() / 1.4))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/minigun_up5.png'),
                                                (self.original_image.get_width() / 1.4,
                                                 self.original_image.get_height() / 1.4))

        self.angle = 0

        self.angle = 0
        self.air_attack = True
        self.ground_attack = True

        self.animation_frames = [pygame.image.load(f'assets/minigun_a/frame_{i}.gif') for i in range(6)]
        self.current_frame = 0
        self.animation_active = False
        self.animation_duration = 35  
        self.last_animation_time = 0
        self.is_blown = False

    def shoot(self, current_time, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.target.health -= self.damage
            self.last_shot_time = current_time

            self.animation_active = True
            self.current_frame = 0
            self.last_animation_time = current_time

            self.box_height = 0  
            self.box_growth_start_time = current_time 

    def update_animation(self, current_time):
        if self.animation_active:
            if current_time - self.last_animation_time >= self.animation_duration:
                self.current_frame += 1
                self.last_animation_time = current_time
                if self.current_frame >= len(self.animation_frames):
                    self.animation_active = False
                    self.current_frame = 0

    def draw(self, screen):
        rotated_image, rotated_rect = self.rotate_image()
        screen.blit(rotated_image, (rotated_rect.topleft[0],rotated_rect.topleft[1]))

        current_time = pygame.time.get_ticks()
        self.update_animation(current_time)

        if self.animation_active:
            angle_rad = math.radians(self.angle)
            anim_x = self.x * constants.TILE_SIZE + constants.TILE_SIZE/2 + (45 * math.cos(angle_rad)) - 12.5  
            anim_y = self.y * constants.TILE_SIZE + constants.TILE_SIZE/2 + (45 * -math.sin(angle_rad)) - 12.5  

            anim_image = pygame.transform.scale(self.animation_frames[self.current_frame], (25, 25))
            rotated_anim_image = pygame.transform.rotate(anim_image, self.angle)

            rotated_anim_rect = rotated_anim_image.get_rect(center=(anim_x + 12.5, anim_y + 12.5))  # Center for 25x25

            screen.blit(rotated_anim_image, rotated_anim_rect.topleft)
        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))
        self.draw_level(screen)

class Harpoon(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.HARPOON_DAMAGE, constants.HARPOON_HIT_SPEED, constants.HARPOON_RANGE, constants.HARPOON_COST)
        self.original_image = pygame.image.load('assets/harpoon.png')

        self.image = pygame.transform.scale(self.original_image,
                                            (self.original_image.get_width() / 2,
                                             self.original_image.get_height() / 2))
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/harpoon_up3.png'),
                                                (self.original_image.get_width() / 1.85,
                                                 self.original_image.get_height() / 1.85))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/harpoon_up5.png'),
                                                (self.original_image.get_width() / 1.9,
                                                 self.original_image.get_height() / 1.9))

        self.image_width = self.image.get_width() 
        self.image_height = self.image.get_height()  
        self.angle = 0
        self.air_attack = True
        self.ground_attack = False
        self.projectiles = []
        self.last_shot_time = 0
        self.is_blown = False

    def shoot(self, current_time, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.last_shot_time = current_time
            angle_rad = math.radians(self.angle)
            projectile = animations.H_Projectile(self.x * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * math.cos(angle_rad)) ,
                                    self.y * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * -math.sin(angle_rad)) ,
                                    self.target, self.angle, self, game_speed)
            self.projectiles.append(projectile)
            self.box_height = 0  
            self.box_growth_start_time = current_time  

    def damage_target(self, target):
        target.health -= self.damage

    def update_projectiles(self, screen):
        for projectile in self.projectiles[:]:
            if projectile.update():  # If projectile reached target
                self.projectiles.remove(projectile)  # Remove the projectile
            else:
                projectile.draw(screen)

    def draw(self, screen):
        rotated_image, rotated_rect = self.rotate_image()

        screen.blit(rotated_image, (rotated_rect.topleft[0], rotated_rect.topleft[1]))

        self.update_projectiles(screen)
        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))
        self.draw_level(screen)


class CryoCannon(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.CRYOCANNON_DAMAGE, constants.CRYOCANNON_HIT_SPEED, constants.CRYOCANNON_RANGE, constants.CRYOCANNON_COST)
        self.original_image = pygame.image.load('assets/cryocannon.png')
        self.image = pygame.transform.scale(self.original_image,
                                            (self.original_image.get_width() / 1.6,
                                             self.original_image.get_height() / 1.6))
        self.image_width = self.image.get_width() 
        self.image_height = self.image.get_height() 
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/cryocannon_up3.png'),
                                                (self.original_image.get_width() / 1.35,
                                                 self.original_image.get_height() / 1.35))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/cryocannon_up5.png'),
                                                (self.original_image.get_width() / 1.35,
                                                 self.original_image.get_height() / 1.35))
        self.angle = 0
        self.air_attack = True
        self.ground_attack = True

        self.animation_frames = [pygame.image.load(f'assets/cryocannon_anim.png')]
        self.current_frame = 0
        self.animation_active = False
        self.animation_duration = 170  
        self.last_animation_time = 0
        self.is_blown = False

    def shoot(self, current_time, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.target.health -= self.damage
            self.target.freeze(0.1, 5000+self.level*1000, game_speed)
            self.last_shot_time = current_time

            self.animation_active = True
            self.current_frame = 0
            self.last_animation_time = current_time

            self.box_height = 0  
            self.box_growth_start_time = current_time  

    def update_animation(self, current_time):
        if self.animation_active:
            if current_time - self.last_animation_time >= self.animation_duration:
                self.animation_active = False


    def draw(self, screen):
        rotated_image, rotated_rect = self.rotate_image()

        screen.blit(rotated_image, rotated_rect.topleft)
        current_time = pygame.time.get_ticks()
        self.update_animation(current_time)
        if self.animation_active:
            angle_rad = math.radians(self.angle)
            anim_x = self.x * constants.TILE_SIZE + constants.TILE_SIZE / 2 + (
                        45 * math.cos(angle_rad)) - 12.5 
            anim_y = self.y * constants.TILE_SIZE + constants.TILE_SIZE / 2 + (
                        45 * -math.sin(angle_rad)) - 12.5 

            anim_image = pygame.transform.scale(self.animation_frames[self.current_frame], (60, 27))
            rotated_anim_image = pygame.transform.rotate(anim_image, self.angle)

            rotated_anim_rect = rotated_anim_image.get_rect(center=(anim_x + 12.5, anim_y + 12.5))  

            screen.blit(rotated_anim_image, rotated_anim_rect.topleft)
        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))

        self.draw_level(screen)

# Tesla subclass
class Tesla(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.TESLA_DAMAGE, constants.TESLA_HIT_SPEED, constants.TESLA_RANGE,
                         constants.TESLA_COST)
        self.damage = constants.TESLA_DAMAGE
        self.hit_interval = constants.TESLA_HIT_SPEED
        self.range = constants.TESLA_RANGE
        self.last_hit_time = 0
        self.air_attack = True
        self.ground_attack = True
        self.image = pygame.image.load('assets/tesla.png')
        self.shooting_animation = pygame.image.load('assets/tesla_anim.png')
        self.shooting_animation_up5 = pygame.image.load('assets/tesla_anim_up5.png') 
        self.shooting_start_time = 0 
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/tesla_up3.png'),
                                                (self.image.get_width(), self.image.get_height()))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/tesla_up5.png'),
                                                (self.image.get_width(), self.image.get_height()))
        self.is_blown = False

    def update(self, monsters, current_time, game_speed):
        self.update_box(current_time, game_speed)
        # Check if there is at least one monster in range
        monsters_in_range = [monster for monster in monsters if self.in_range(monster)]

        # If any monster is in range and the time interval has passed, damage all in range
        if monsters_in_range and current_time - self.last_hit_time >= self.hit_interval * 1000 / game_speed:
            for monster in monsters_in_range:
                if not monster.isBlip:
                    monster.health -= self.damage
            self.last_hit_time = current_time
            self.shooting_start_time = current_time
            self.box_height = 0  
            self.box_growth_start_time = current_time 
            # Start the shooting animation timer

    def draw(self, screen):
        screen.blit(self.image,
                    (self.x * constants.TILE_SIZE - 7, self.y * constants.TILE_SIZE - 7))
        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5, self.box_height))

        if self.shooting_start_time > 0:
            elapsed_time = pygame.time.get_ticks() - self.shooting_start_time
            if elapsed_time < 120:
                if self.level < 4:
                    screen.blit(self.shooting_animation,
                                (self.x * constants.TILE_SIZE - 133/3,
                                 self.y * constants.TILE_SIZE - 104/3))
                else:
                    screen.blit(self.shooting_animation_up5,
                                (self.x * constants.TILE_SIZE - 133/3,
                                 self.y * constants.TILE_SIZE - 104/3))
                self.shooting_start_time = 0 
        self.draw_level(screen)


class Laser(Turret):
    def __init__(self, x, y):
            super().__init__(x, y, constants.LASER_DAMAGE, constants.LASER_HIT_SPEED, constants.LASER_RANGE,
                         constants.LASER_COST)
            self.damage = constants.LASER_DAMAGE
            self.hit_interval = constants.LASER_HIT_SPEED
            self.range = constants.LASER_RANGE
            self.last_hit_time = 0
            self.air_attack = True
            self.ground_attack = True
            self.monsters_to_attack = []
            self.image = pygame.image.load('assets/laser.png')
            self.up3_image = pygame.transform.scale(pygame.image.load('assets/laser_up3.png'),
                                                    (self.image.get_width(),
                                                     self.image.get_height()))
            self.up5_image = pygame.transform.scale(pygame.image.load('assets/laser_up5.png'),
                                                    (self.image.get_width()*1.2,
                                                     self.image.get_height()*1.2))
            self.is_blown = False


    def update(self, monsters, current_time, game_speed):
        self.update_box(current_time, game_speed)
        monsters_in_range = [monster for monster in monsters if self.in_range(monster)]

        max_targets = 5 + (2 * self.level)
        self.monsters_to_attack = monsters_in_range[:max_targets]  # Get the first 4 monsters in range

        if self.monsters_to_attack and current_time - self.last_hit_time >= self.hit_interval * 1000 / game_speed:
            for monster in self.monsters_to_attack:
                if not monster.isBlip:
                    monster.health -= self.damage
                    if self.stage:
                        self.stage.total_damage_done += self.damage
            self.last_hit_time = current_time
            self.box_height = 0  
            self.box_growth_start_time = current_time  

    def draw(self, screen):
        img = self.image
        img = pygame.transform.scale(img, (constants.TILE_SIZE * 1.7, constants.TILE_SIZE * 1.7))
        screen.blit(img, (self.x * constants.TILE_SIZE - 8, self.y * constants.TILE_SIZE - 12))

        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))

        for monster in self.monsters_to_attack:
            if monster and not self.under_upgrade:  
                line_color = (245, 11, 250) if self.level >= 4 else (255, 0, 0)
                pygame.draw.line(screen, line_color,  
                                 (self.x * constants.TILE_SIZE + constants.TILE_SIZE/2 +2,
                                          self.y * constants.TILE_SIZE +constants.TILE_SIZE/2-1),  
                                 (monster.x * constants.TILE_SIZE+ constants.TILE_SIZE/2,
                                          monster.y * constants.TILE_SIZE+ constants.TILE_SIZE/2), 3)  
                pygame.draw.line(screen, (255, 255, 255), 
                                 (self.x * constants.TILE_SIZE + constants.TILE_SIZE / 2+2,
                                  self.y * constants.TILE_SIZE + constants.TILE_SIZE / 2-1),
                                 (monster.x * constants.TILE_SIZE + constants.TILE_SIZE / 2,
                                  monster.y * constants.TILE_SIZE + constants.TILE_SIZE / 2), 1)  

        self.draw_level(screen)

class Freezer(Turret):
    def __init__(self, x, y):
        super().__init__(x, y,None, constants.FREEZER_HIT_SPEED, constants.FREEZER_RANGE,
                         constants.FREEZER_COST)
        self.hit_interval = constants.TESLA_HIT_SPEED
        self.range = constants.TESLA_RANGE
        self.last_hit_time = 0
        self.air_attack = True
        self.ground_attack = True
        self.image = pygame.image.load('assets/freezer.png')

        self.up3_image = pygame.transform.scale(pygame.image.load('assets/freezer_up3.png'),
                                            (self.image.get_width(),
                                             self.image.get_height()))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/freezer_up5.png'),
                                            (self.image.get_width(),
                                             self.image.get_height()))
        self.shooting_start_time = None
        self.is_blown = False


    def update(self, monsters, current_time, game_speed):
        self.update_box(current_time, game_speed)
        monsters_in_range = [monster for monster in monsters if self.in_range(monster)]

        if monsters_in_range and current_time - self.last_hit_time >= self.hit_interval * 1000 / game_speed:
            for monster in monsters_in_range:
                if self.level <=4:
                    freeze_speed_ratio = 0.6 - self.level*0.05
                else:
                    freeze_speed_ratio = 0.35 - self.level*0.01
                monster.freeze(freeze_speed_ratio, self.hit_interval*10000, game_speed)
            self.last_hit_time = current_time
            self.shooting_start_time = current_time
            self.box_height = 0 
            self.box_growth_start_time = current_time 

    def draw(self, screen):
        img = self.image
        img = pygame.transform.scale(img, (constants.TILE_SIZE * 1.8, constants.TILE_SIZE * 1.8))
        screen.blit(img, (self.x * constants.TILE_SIZE - 8, self.y * constants.TILE_SIZE - 8))
        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))
        self.draw_level(screen)

class Flame(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.FLAME_DAMAGE, constants.FLAME_HIT_SPEED, constants.FLAME_RANGE,
                         constants.FLAME_COST)
        self.original_image = pygame.image.load('assets/flame.png')
        self.image = pygame.transform.scale(self.original_image, (
                                            self.original_image.get_width() / 1.4,
                                            self.original_image.get_height() / 1.4))
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/flame_up3.png'),
                                                (self.image.get_width(),
                                                 self.image.get_height()))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/flame_up5.png'),
                                                (self.image.get_width(),
                                                 self.image.get_height()))
        self.angle = 0
        self.air_attack = False
        self.ground_attack = True

        self.animation_frames = [pygame.image.load(f'assets/flame_anim.png')]
        self.current_frame = 0

        self.animation_active = False
        self.animation_duration = 130  
        self.last_animation_time = 0
        self.flameRect = None
        self.is_blown = False

    def shoot_flame(self, current_time, monsters, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.last_shot_time = current_time

            self.animation_active = True
            self.current_frame = 0
            self.last_animation_time = current_time
            monsters_in_rect = [monster for monster in monsters if monster.rect.colliderect(self.flameRect)]
            for monster in monsters_in_rect:
                if not monster.isAir and not monster.isBlip:
                    monster.health -= self.damage

            self.box_height = 0  
            self.box_growth_start_time = current_time  

    def update_animation(self, current_time):
        if self.animation_active:
            if current_time - self.last_animation_time >= self.animation_duration:
                self.current_frame += 1
                self.last_animation_time = current_time
                if self.current_frame >= len(self.animation_frames):
                    self.animation_active = False
                    self.current_frame = 0

    def update(self, monsters, current_time, game_speed):
        self.update_box(current_time, game_speed)
        if self.target and self.target in monsters:
            if self.in_range(self.target):
                self.shoot_flame(current_time, monsters, game_speed)
            else:
                self.target = self.find_target(monsters)
        else:

            self.target = self.find_target(monsters)

    def draw(self, screen):
        rotated_image, rotated_rect = self.rotate_image()
        screen.blit(rotated_image, (rotated_rect.topleft[0], rotated_rect.topleft[1]))

        current_time = pygame.time.get_ticks()
        self.update_animation(current_time)

        angle_rad = math.radians(self.angle)
        anim_x = self.x * constants.TILE_SIZE + constants.TILE_SIZE / 2 + (
                45 * math.cos(angle_rad)) - 12.5  
        anim_y = self.y * constants.TILE_SIZE + constants.TILE_SIZE / 2 + (
                45 * -math.sin(angle_rad)) - 12.5  

        anim_image = pygame.transform.scale(self.animation_frames[self.current_frame], (55, 45))
        rotated_anim_image = pygame.transform.rotate(anim_image, self.angle)

        rotated_anim_rect = rotated_anim_image.get_rect(center=(anim_x + 12.5, anim_y + 12.5))
        if self.animation_active:
            screen.blit(rotated_anim_image, rotated_anim_rect.topleft)

        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                             self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height, 3.5, self.box_height))
        rect_width, rect_height = self.range*constants.TILE_SIZE, 45.0
        red_rect = pygame.Rect(0, 0, rect_width, rect_height)  
        red_rect.center = rotated_anim_rect.center  

        rect_surface = pygame.Surface((rect_width, rect_height), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, (255, 0, 0), rect_surface.get_rect(), 3)

        rotated_red_rect_surface = pygame.transform.rotate(rect_surface, self.angle)

        rotated_red_rect = rotated_red_rect_surface.get_rect(center=red_rect.center)
        self.flameRect = rotated_red_rect
        self.draw_level(screen)

class FloorBurn:  # class for BurstFlame explosions
    def __init__(self, x, y, turr):
        self.range = turr.range/3.5
        self.x = x - (self.range * constants.TILE_SIZE) + constants.TILE_SIZE / 2
        self.y = y - (self.range * constants.TILE_SIZE) + constants.TILE_SIZE / 2
        self.rect = pygame.Rect(self.x, self.y, self.range*constants.TILE_SIZE * 2, self.range*constants.TILE_SIZE * 2)
        self.damage = turr.damage
        self.hit_interval = turr.hit_speed /20
        self.last_hit_time = 0
        self.image1 = pygame.transform.scale(pygame.image.load('assets/burn1.png'),(self.range*constants.TILE_SIZE * 2, self.range*constants.TILE_SIZE * 2))
        self.image2 = pygame.transform.scale(pygame.image.load('assets/burn2.png'),(self.range*constants.TILE_SIZE * 2, self.range*constants.TILE_SIZE * 2))
        self.curr_image = self.image1
        self.last_flip = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.prev_time = pygame.time.get_ticks()

    def in_range(self, monster):
        distance = math.hypot(monster.x - self.x/constants.TILE_SIZE, monster.y - self.y/constants.TILE_SIZE)
        if monster.isBlip:
            return False
        return distance <= self.range
    def isColliding(self, monster):
        if self.rect.colliderect(monster.rect):
            return True
    def flip_image(self):
        if self.curr_image == self.image1:
            self.curr_image = self.image2
        else:
            self.curr_image = self.image1

    def update(self, monsters, current_time, game_speed):
        if current_time >= self.last_flip + 250/game_speed:
            self.flip_image()
            self.last_flip = current_time
        monsters_in_range = [monster for monster in monsters if self.isColliding(monster)]

        if monsters_in_range and current_time - self.last_hit_time >= self.hit_interval * 1000 / game_speed:
            for monster in monsters_in_range:
                if not monster.isBlip and not monster.isAir:
                    monster.health -= self.damage

            self.last_hit_time = current_time
        self.elapsed_time += (current_time-self.prev_time)*game_speed
        self.prev_time = current_time

    def draw(self, screen):
        screen.blit(self.curr_image, (self.x , self.y))

class BurstFire(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.BURST_DAMAGE, constants.BURST_HIT_SPEED, constants.BURST_RANGE, constants.BURST_COST)
        self.original_image = pygame.image.load('assets/burstFire.png')

        self.image = pygame.transform.scale(self.original_image,
                                            (self.original_image.get_width() / 1.12,
                                             self.original_image.get_height() / 1.12))
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/burstFire_up3.png'),
                                                (self.original_image.get_width() / 1.12,
                                                 self.original_image.get_height() / 1.12))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/burstFire_up5.png'),
                                                (self.original_image.get_width() / 1.1,
                                                 self.original_image.get_height() / 1.1))

        self.image_width = self.image.get_width()
        self.image_height = self.image.get_height()
        self.angle = 0
        self.air_attack = False
        self.ground_attack = True
        self.projectiles = []
        self.last_shot_time = 0
        self.burns = []
        self.is_blown = False
    
    def shoot(self, current_time, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.last_shot_time = current_time
            angle_rad = math.radians(self.angle)
            projectile = animations.BF_Projectile(self.x * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * math.cos(angle_rad)) ,
                                    self.y * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * -math.sin(angle_rad)) ,
                                    self.target, self.angle, self, game_speed)
            self.projectiles.append(projectile)
            self.box_height = 0  
            self.box_growth_start_time = current_time 

    def update(self, monsters, current_time, game_speed):
        self.update_box(current_time, game_speed)
        for burn in self.burns:
            burn.update(monsters, current_time, game_speed)
            if burn.elapsed_time >= 6000:
                self.burns.remove(burn)
        if self.target and self.target in monsters:
            if self.in_range(self.target):
                self.shoot(current_time, game_speed)
            else:
                self.target = self.find_target(monsters)
        else:
            self.target = self.find_target(monsters)

    def update_projectiles(self, screen):
        for projectile in self.projectiles[:]:
            if projectile.update():  
                self.projectiles.remove(projectile)  
            else:
                projectile.draw(screen)

    def place_burn(self, x, y):
        self.burns.append(FloorBurn(x, y, self))

    def draw(self, screen):
        for burn in self.burns:
            burn.draw(screen)
        rotated_image, rotated_rect = self.rotate_image()
        screen.blit(rotated_image, (rotated_rect.topleft[0], rotated_rect.topleft[1]))

        self.update_projectiles(screen)
        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))
        self.draw_level(screen)

class Mine(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.MINE_DAMAGE, 0.0,constants.MINE_RANGE, constants.MINE_COST)
        self.damage = constants.MINE_DAMAGE
        self.range = constants.MINE_RANGE
        self.cost = constants.MINE_COST
        self.trigger_time = None 
        self.air_attack = False
        self.ground_attack = True
        self.image = pygame.image.load('assets/mine.png')
        self.orignal_image = pygame.image.load('assets/mine.png')

        self.triggered_image = pygame.image.load('assets/mine_trig.png')
        self.flip_time = self.trigger_time
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/mine_up3.png'),
                                                (self.image.get_width() ,
                                                 self.image.get_height()))
        self.up3_image_trig = pygame.transform.scale(pygame.image.load('assets/mine_trig_up3.png'),
                                                (self.image.get_width() ,
                                                 self.image.get_height()))

        self.up5_image = pygame.transform.scale(pygame.image.load('assets/mine_up5.png'),
                                                (self.image.get_width() ,
                                                 self.image.get_height()))
        self.up5_image_trig = pygame.transform.scale(pygame.image.load('assets/mine_trig_up5.png'),
                                                (self.image.get_width() ,
                                                 self.image.get_height()))
        self.is_blown = False

    def update(self, monsters, current_time, game_speed):
        self.update_box(current_time, game_speed)

        monsters_in_range = [monster for monster in monsters if self.in_range(monster)]
        if len(monsters_in_range) >=1:
            if not self.trigger_time:
                self.trigger_time = current_time
                if self.level <2:
                    self.image = self.triggered_image
                elif self.level <4:
                    self.image = self.up3_image_trig
                else:
                    self.image = self.up5_image_trig
        if self.trigger_time:
            self.start_trigger_anim(game_speed)
            if current_time >= self.trigger_time +3000/game_speed:
                for mon in monsters_in_range: 
                    if not mon.isAir and not mon.isBlip:
                        mon.health -= self.damage
                self.is_blown = True
    
    def start_trigger_anim(self, game_speed):
        if self.flip_time == None:
            self.flip_time = self.trigger_time
        current_time = pygame.time.get_ticks()
        if current_time >= self.flip_time + 450/ game_speed and self.level <2:
            if self.image == self.triggered_image:
                self.image = self.orignal_image
            else:
                self.image = self.triggered_image
            self.flip_time = current_time
        elif current_time >= self.flip_time + 450/ game_speed and self.level <4:
            if self.image == self.up3_image_trig:
                self.image = self.up3_image
            else:
                self.image = self.up3_image_trig
            self.flip_time = current_time
        elif current_time >= self.flip_time + 450/ game_speed:
            if self.image == self.up5_image_trig:
                self.image = self.up5_image
            else:
                self.image = self.up5_image_trig
            self.flip_time = current_time

    def draw(self, screen):
        screen.blit(self.image,
                    (self.x * constants.TILE_SIZE - 7, self.y * constants.TILE_SIZE - 7))
        self.draw_level(screen)
        if self.under_upgrade:
            box_color = (100, 230, 160)
            pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))
            
class Frost_Cannon(Turret):
    def __init__(self, x, y):
        super().__init__(x, y, constants.FROSTCANNON_DAMAGE, constants.FROSTCANNON_HIT_SPEED, constants.FROSTCANNON_RANGE, constants.FROSTCANNON_COST)
        self.original_image = pygame.image.load('assets/frost_cannon.png')

        self.image = pygame.transform.scale(self.original_image,
                                            (self.original_image.get_width() / 1.5,
                                             self.original_image.get_height() / 1.5))
        self.up3_image = pygame.transform.scale(pygame.image.load('assets/frost_cannon_up3.png'),
                                                (self.original_image.get_width() / 1.45,
                                                 self.original_image.get_height() / 1.45))
        self.up5_image = pygame.transform.scale(pygame.image.load('assets/frost_cannon_up5.png'),
                                                (self.original_image.get_width() / 1.4,
                                                 self.original_image.get_height() / 1.4))

        self.image_width = self.image.get_width()  
        self.image_height = self.image.get_height() 
        self.angle = 0
        self.air_attack = False
        self.ground_attack = True
        self.projectiles = []
        self.last_shot_time = 0
        self.is_blown = False
        self.all_mons = []
        self.curr_game_speed = None
         
    def shoot(self, current_time, game_speed):
        if self.target and current_time - self.last_shot_time >= self.hit_speed * 1000 / game_speed:
            self.last_shot_time = current_time
            angle_rad = math.radians(self.angle)
            projectile = animations.FC_Projectile(self.x * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * math.cos(angle_rad)) ,
                                    self.y * constants.TILE_SIZE + constants.TILE_SIZE/2 + (15 * -math.sin(angle_rad)) ,
                                    self.target, self.angle, self, game_speed)
            self.projectiles.append(projectile)
            self.box_height = 0  
            self.box_growth_start_time = current_time  

    def damage_target(self, target):
        for mon in self.all_mons:
            distance = math.hypot(target.x - mon.x, target.y - mon.y)
            if distance <= 3 and not mon.isAir:
                mon.health -= self.damage
                mon.freeze(0.4, 3000+self.level*300, self.curr_game_speed)

    def update_projectiles(self, screen):
        for projectile in self.projectiles[:]:
            if projectile.update():  
                self.projectiles.remove(projectile) 
            else:
                projectile.draw(screen)

    def update(self, monsters, current_time, game_speed):
        self.update_box(current_time, game_speed)
        self.all_mons = monsters
        self.curr_game_speed = game_speed
        if self.target and self.target in monsters:
            if self.in_range(self.target):
                self.shoot(current_time, game_speed)
            else:
                self.target = self.find_target(monsters)
        else:

            self.target = self.find_target(monsters)
            
    def draw(self, screen):
        rotated_image, rotated_rect = self.rotate_image()

        screen.blit(rotated_image, (rotated_rect.topleft[0], rotated_rect.topleft[1]))

        self.update_projectiles(screen)
        if self.under_upgrade:
            box_color = (100, 230, 160)
        else:
            box_color = (255, 165, 5)
        pygame.draw.rect(screen, box_color, (self.x * constants.TILE_SIZE + constants.TILE_SIZE+ 6,
                                                 self.y * constants.TILE_SIZE + constants.TILE_SIZE +5  - self.box_height,
                                                 3.5,
                                                 self.box_height))
        self.draw_level(screen)