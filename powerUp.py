import animations
import constants

import pygame

class powerUp():
    def __init__(self, pos ,stage):
        self.pos = pos
        self.rect = pygame.Rect(self.pos[0] * constants.TILE_SIZE, self.pos[1] * constants.TILE_SIZE, constants.TILE_SIZE, constants.TILE_SIZE)
        self.stage = stage
        self.begin_time = pygame.time.get_ticks()
        self.remove_time = self.begin_time + 5000
        self.used_time = None


class coin(powerUp):
    def __init__(self, pos, stage):
        super().__init__(pos, stage)
        self.img = pygame.image.load('assets/coin.png')
        self.remove_time = self.begin_time + 5000
        self.text = pygame.font.Font(None, 17).render(f' +${40}', True, (200, 200, 0))

    def applyEffect(self, stage):
        if stage.paused:
            return
        stage.money += 40
        stage.powerUps.remove(self)
        stage.used_powerUps.append(self)
        self.used_time = pygame.time.get_ticks()

    def draw(self, screen):
        image = pygame.transform.scale(self.img, ( constants.TILE_SIZE  ,constants.TILE_SIZE))
        # Draw the rotated image
        screen.blit(image, self.rect)

class aid(powerUp):
    def __init__(self, pos, stage):
        super().__init__(pos, stage)
        self.img = pygame.image.load('assets/aid.png')
        self.remove_time = self.begin_time + 5000
        self.text = pygame.font.Font(None, 17).render(f' +{20}hp', True, (0, 200, 0))

    def applyEffect(self, stage):
        if stage.paused:
            return
        stage.stage_health += 50
        stage.powerUps.remove(self)
        stage.used_powerUps.append(self)
        self.used_time = pygame.time.get_ticks()

    def draw(self, screen):
        image = pygame.transform.scale(self.img, ( constants.TILE_SIZE +7,constants.TILE_SIZE))
        # Draw the rotated image
        screen.blit(image, self.rect)

class tnt(powerUp):
    def __init__(self, pos, stage):
        super().__init__(pos, stage)
        self.img = pygame.image.load('assets/tnt.png')
        self.remove_time = self.begin_time + 5000
        self.text = pygame.font.Font(None, 17).render('', True, (0, 0, 0))

    def applyEffect(self, stage):
        if stage.paused:
            return
        for mon in stage.generated_wave.monsters:
            if abs(mon.x -self.pos[0]) <= 5.35 and abs(mon.y -self.pos[1]) <= 5.35:
                mon.health -= 60

        stage.powerUps.remove(self)
        stage.used_powerUps.append(self)
        self.used_time = pygame.time.get_ticks()
        stage.anims.append(animations.BlastAnimation(self.pos[0], self.pos[1]))

    def draw(self, screen):
        image = pygame.transform.scale(self.img, ( constants.TILE_SIZE +8,constants.TILE_SIZE+8))
        # Draw the rotated image
        screen.blit(image, self.rect)

class slower(powerUp):
    def __init__(self, pos, stage):
        super().__init__(pos, stage)
        self.img = pygame.image.load('assets/slower.png')
        self.remove_time = self.begin_time + 5000
        self.text = pygame.font.Font(None, 17).render('', True, (0, 0, 0))

    def applyEffect(self, stage):
        if stage.paused:
            return
        for mon in stage.generated_wave.monsters:
            if abs(mon.x -self.pos[0]) <= 10 and abs(mon.y -self.pos[1]) <= 10:
                mon.freeze(0.5, 5000, stage.game_speed)
        stage.powerUps.remove(self)
        stage.used_powerUps.append(self)
        self.used_time = pygame.time.get_ticks()
        stage.anims.append(animations.SlowDownAnimation(self.pos[0], self.pos[1]))


    def draw(self, screen):
        image = pygame.transform.scale(self.img, ( constants.TILE_SIZE +7,constants.TILE_SIZE))
        # Draw the rotated image
        screen.blit(image, self.rect)