import csv
import pygame
import os
import random

import animations
import constants
import monster
import turret
import powerUp

Current_Stage = None
pause_rect = pygame.Rect(30, 12, 50, 48)
speed_rect = pygame.Rect(90, 12, 69, 48)
exit_rect = pygame.Rect(1250, 12, 50, 50)

# Load map from CSV
def load_map(file_name):
    with open(file_name, newline='') as csvfile:
        reader = csv.reader(csvfile)
        game_map = [[int(tile) for tile in row] for row in reader]
    return game_map

# Load and scale background image
def load_and_scale_bg(image_path, target_width, target_height):
    img = pygame.image.load(image_path)
    scaled_img = pygame.transform.scale(img, (target_width, target_height))
    return scaled_img

class Node:
    def __init__(self, x, y):
        self.x = x * constants.TILE_SIZE
        self.y = y * constants.TILE_SIZE
        self.rect = pygame.Rect(x * constants.TILE_SIZE, y * constants.TILE_SIZE, constants.TILE_SIZE, constants.TILE_SIZE)

    def draw(self, screen):
        transparent_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        transparent_surface.fill((0, 0, 0, 0))  # Fill with fully transparent color
        screen.blit(transparent_surface, self.rect.topleft)
        node_img = pygame.transform.scale(pygame.image.load('assets/node.png'), (constants.TILE_SIZE, constants.TILE_SIZE))
        screen.blit(node_img, (self.x, self.y))

class Wave:
    def __init__(self, entrance, exit_tile, path, monster_list, spawndelay):
        self.entrance = entrance
        self.exit_tile = exit_tile
        self.path = path
        self.monster_list = monster_list  # List of tuples [(MonsterType, Number)]
        self.spawnDelay = spawndelay
        self.monsters = []
        self.last_spawn_time = pygame.time.get_ticks()
        self.monsters_spawned = 0
        self.current_tuple_index = 0  # To track which monster type we're spawning
        self.spawn_count = 0  # To track how many monsters of the current type have been spawned
        self.all_dead = False
        self.dead_list = []
        self.blip_count = 10
        self.blip_pos = 0
        self.last_spawn_blip = 0

    def refresh(self):
        self.monsters = []
        self.last_spawn_time = pygame.time.get_ticks()
        self.monsters_spawned = 0
        self.current_tuple_index = 0  # To track which monster type we're spawning
        self.spawn_count = 0  # To track how many monsters of the current type have been spawned
        self.all_dead = False
        self.dead_list = []
        self.blip_count = 10
        self.blip_pos = 0
        self.last_spawn_blip = 0

    def spawn_monster(self, stage):
        current_time = pygame.time.get_ticks()
        if self.current_tuple_index == len(self.monster_list) and len(self.monsters) == 0 :
            self.all_dead = True
        if self.current_tuple_index < len(self.monster_list) and current_time - self.last_spawn_time >= self.spawnDelay /stage.game_speed:
            monster_type, num_to_spawn = self.monster_list[self.current_tuple_index]

            if self.spawn_count < num_to_spawn:
                # Spawn the correct monster type
                if monster_type == 'A':
                    self.monsters.append(monster.Monster_A(self.entrance))
                elif monster_type == 'B':
                    self.monsters.append(monster.Monster_B(self.entrance))
                elif monster_type == 'C':
                    self.monsters.append(monster.Monster_C(self.entrance))
                elif monster_type == 'D':
                    self.monsters.append(monster.Monster_D(self.entrance))
                elif monster_type == 'E':
                    self.monsters.append(monster.Monster_E(self.entrance))
                elif monster_type == 'F':
                    self.monsters.append(monster.Monster_F(self.entrance))
                elif monster_type == 'G':
                    self.monsters.append(monster.Monster_G(self.entrance))
                elif monster_type == 'H':
                    self.monsters.append(monster.Monster_H(self.entrance))
                elif monster_type == 'I':
                    self.monsters.append(monster.Monster_I(self.entrance, stage))
                self.monsters_spawned += 1
                self.spawn_count += 1
                self.last_spawn_time = current_time
            else:
                self.current_tuple_index += 1
                self.spawn_count = 0

    def blip_path(self, stage):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_blip >= 190/stage.game_speed and self.blip_count != 0:
            self.monsters.append(monster.Path_blip(self.path[self.blip_pos], self.blip_count, self.path))
            self.blip_count -= 1
            self.last_spawn_blip = pygame.time.get_ticks()

    def update_wave(self, dt, stage):
        for i in range(self.blip_count):
            self.blip_path(stage)
        if not self.all_dead:
            self.spawn_monster(stage)
        for mon in self.monsters:
            mon.update_position(self.path, dt, stage)
            if mon.health<=0:
                self.dead_list.append(mon)
        self.monsters = [mon for mon in self.monsters if mon.health > 0]

    def draw_ground(self, screen):
        for mon in self.monsters:
            if not mon.isAir and not mon.isBlip:
                mon.draw(screen)
    def draw_air(self, screen):
        for mon in self.monsters:
            if mon.isAir or mon.isBlip:
                mon.draw(screen)
        for mon in self.dead_list:
            if mon.kill_money_time:
                current_time = pygame.time.get_ticks()
                if current_time - mon.kill_money_time <= 1800 and mon.did_exit == False:  
                    screen.blit(mon.kill_money_text, (mon.x*constants.TILE_SIZE+5, mon.y*constants.TILE_SIZE - 20))
                else:
                    mon.kill_money_time = None  

def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((constants.MAP_WIDTH * constants.TILE_SIZE * 0.8, constants.MAP_HEIGHT * constants.TILE_SIZE * 0.75+ constants.STATUS_BAR_HEIGHT))
    pygame.display.set_caption("Monster Wave Game")
    return screen

def draw_game(screen, nodes, wave, menu=None, up_menu=None, bg_image=None, curr_turret=None, mouseactive=False, curr_stage=None):
    current_time = pygame.time.get_ticks()
    bg_image = bg_image
    if bg_image:
        screen.blit(bg_image, (0, 0))
        bg_surface =  pygame.Surface((constants.MAP_WIDTH * constants.TILE_SIZE, constants.MAP_HEIGHT * constants.TILE_SIZE),
                                        pygame.SRCALPHA)
        bg_surface.fill((0,0,0,94))

        screen.blit(bg_surface, (0, 0))

    for node in nodes:
        node.draw(screen)

    for anim in curr_stage.anims:
        anim.update(screen)

    wave.draw_ground(screen)

    if curr_stage.overlay:
        overlay_img = load_and_scale_bg(curr_stage.overlay,constants.MAP_WIDTH * constants.TILE_SIZE,
                                                        constants.MAP_HEIGHT * constants.TILE_SIZE)
        screen.blit(overlay_img, (0, 0))
        bg_surface = pygame.Surface(
            (constants.MAP_WIDTH * constants.TILE_SIZE, constants.MAP_HEIGHT * constants.TILE_SIZE),
            pygame.SRCALPHA)
        screen.blit(bg_surface, (0, 0))

    wave.draw_air(screen)

    # Draw status bar
    status_bar_surface = pygame.Surface((constants.MAP_WIDTH * constants.TILE_SIZE, constants.STATUS_BAR_HEIGHT),
                                        pygame.SRCALPHA)
    status_bar_surface.fill(constants.STATUS_BAR_COLOR) 

    # speed button surface
    speed_surface = pygame.Surface((60,48), pygame.SRCALPHA)
    speed_surface.fill((0,0,0,220 - (curr_stage.game_speed*70)))

    # pause button surface
    pause_surface = pygame.Surface((40, 48), pygame.SRCALPHA)
    pause_surface.fill((0, 0, 0, 200))

    # Draw money and player health 
    font = pygame.font.Font(None, 36)

    money_label = font.render('Money', True, (0, 200, 0))
    money_text = font.render(f' ${curr_stage.money}', True, (0, 200, 0))

    health_label = font.render('Life', True, (0, 220, 0))
    health_text = font.render(f' {curr_stage.stage_health:.2f}', True, (0, 200, 0))
    health_box = pygame.Rect(190, 12, 13, 50)
    health_bar_height = 50* curr_stage.stage_health / curr_stage.max_health
    if health_bar_height >=50:
        health_bar_height = 50
    heath_bar = pygame.Rect(191, 63- health_bar_height, 11, health_bar_height-1)

    wave_label = font.render('Wave', True, (170, 255, 170))
    wave_text = font.render(f' {int(curr_stage.curr_wave_index + 1)} / {len(curr_stage.waves_list)}', True,
                            (200, 255, 200))
    endless_wave_text = font.render(f' {int(curr_stage.curr_wave_index + 1)}', True,
                            (200, 255, 200))

    for turr in curr_stage.turrets:
        turr.draw(screen)
        if turr.under_upgrade:
            if curr_stage.paused:
                screen.blit(pygame.transform.scale(constants.up_overlay,(15,15)), (turr.x*constants.TILE_SIZE+5, 
                                                                               turr.y*constants.TILE_SIZE+5))
            else:
                if current_time >= turr.last_up_time + 480:
                    turr.last_up_time = current_time
                if current_time <= turr.last_up_time + 220:
                    screen.blit(pygame.transform.scale(constants.up_overlay,(15,15)), (turr.x*constants.TILE_SIZE+5, 
                                                                               turr.y*constants.TILE_SIZE+5))

    draw_wave_alert(screen, curr_stage)
    for pup in curr_stage.powerUps:
        pup.draw(screen)

    for pup in curr_stage.used_powerUps:
        if current_time <= pup.used_time + 3000:
            screen.blit(pup.text, (pup.pos[0] * constants.TILE_SIZE + 5, pup.pos[1] * constants.TILE_SIZE - 20))
    if up_menu:
        draw_range(screen, curr_turret)
        draw_upgrade_menu(screen, up_menu)

    if menu:
        draw_menu(screen, menu)

    if mouseactive:
        screen.blit(status_bar_surface, (0, 0))

        screen.blit(money_label, (constants.MAP_WIDTH * constants.TILE_SIZE / 3, 10))
        screen.blit(money_text, (constants.MAP_WIDTH * constants.TILE_SIZE / 3 - 5, 40))

        screen.blit(health_label, (10 + 200, 10))
        screen.blit(health_text, (10 + 192, 40))
        pygame.draw.rect(screen, (255, 255, 255), health_box, 1)
        pygame.draw.rect(screen, (0,255,0), heath_bar)

        screen.blit(wave_label, (constants.MAP_WIDTH * constants.TILE_SIZE / 2 + 300, 10))
        if curr_stage.endless:
            screen.blit(endless_wave_text, (constants.MAP_WIDTH * constants.TILE_SIZE / 2 + 307, 40))
        else:
            screen.blit(wave_text, (constants.MAP_WIDTH * constants.TILE_SIZE / 2 + 297, 40))

        screen.blit(pygame.transform.scale(pygame.image.load('assets/speed_button.png'),(60,48)), speed_rect)
        screen.blit(speed_surface, speed_rect)

        screen.blit(pygame.transform.scale(pygame.image.load('assets/pause_button.png'),(40,48)), pause_rect)

        if curr_stage.paused:
            screen.blit(pause_surface, pause_rect)

        screen.blit(pygame.transform.scale(pygame.image.load('assets/exit_button.png'),(50,50)), exit_rect)
    pygame.display.flip()

def create_menu(node, font, stage):
    if node.y < 300:
        menu_y = node.y
    else:
        menu_y = 300

    if node.x < 1120:
        menu_x = node.x + 30
    else:
        menu_x = node.x - 200

    button_height = 85
    menu_width = 210
    menu_height = 27 + constants.buttons_per_page*button_height  
    stat_font = pygame.font.Font(None, 18)
    cost_font = pygame.font.Font(None, 20)
    air_font = pygame.font.Font(None, 19)
    ground_font = pygame.font.Font(None, 19)

    buttons = []

    menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)

    def add_button(text, action, cost, img, stats):
        button_surface = pygame.Surface((menu_width, button_height), pygame.SRCALPHA)
        if stage.money >= cost:
            button_surface.fill((60, 255, 60, 55))  # Fill the button surface with green if affordable
        else:
            button_surface.fill((255, 255, 255, 30))  # Fill the button surface with white otherwise
        button_text = font.render(text, True, (255, 255, 0))
        buttons.append({
            'surface': button_surface,
            'text': button_text,
            'action': action,
            'stats': stats,
            'button_img': pygame.transform.scale(img, (60, 60))
        })

    # Add turret buttons
    add_button(f'Mine', 'place_mine', constants.MINE_COST, pygame.image.load('assets/mine_m.png'), [
        f'Damage: {constants.MINE_DAMAGE:.2f}',
        f'Hit Speed: N/A',
        f'${constants.MINE_COST}',
        f'Range: {constants.MINE_RANGE}',
        'Ground'
    ])
    add_button(f'Minigun', 'place_minigun', constants.MINIGUN_COST, pygame.image.load('assets/minigun_m.png'), [
        f'Damage: {constants.MINIGUN_DAMAGE:.2f}',
        f'Hit Speed: {constants.MINIGUN_HIT_SPEED:.2f}',
        f'${constants.MINIGUN_COST}',
        f'Range: {constants.MINIGUN_RANGE}',
        'Ground,',
        'Air'

    ])
    add_button(f'Cannon', 'place_cannon', constants.CANNON_COST, pygame.image.load('assets/cannon_m.png'), [
        f'Damage: {constants.CANNON_DAMAGE}',
        f'Hit Speed: {constants.CANNON_HIT_SPEED:.2f}',
        f'${constants.CANNON_COST}',
        f'Range: {constants.CANNON_RANGE}',
        'Ground'

    ])
    add_button(f'Blaster', 'place_blaster', constants.BLASTER_COST, pygame.image.load('assets/blaster_m.png'), [
        f'Damage: {constants.BLASTER_DAMAGE}',
        f'Hit Speed: {constants.BLASTER_HIT_SPEED:.2f}',
        f'${constants.BLASTER_COST}',
        f'Range: {constants.BLASTER_RANGE}',
        'Ground,',
        'Air'
    ])
    add_button(f'Tesla', 'place_tesla', constants.TESLA_COST, pygame.image.load('assets/tesla.png'), [
        f'Damage: {constants.TESLA_DAMAGE:.2f}',
        f'Hit Speed: {constants.TESLA_HIT_SPEED:.2f}',
        f'${constants.TESLA_COST}',
        f'Range: {constants.TESLA_RANGE}',
        'Ground,',
        'Air'
    ])
    add_button(f'Harpoon', 'place_harpoon', constants.HARPOON_COST, pygame.image.load('assets/harpoon_m.png'), [
        f'Damage: {constants.HARPOON_DAMAGE:.2f}',
        f'Hit Speed: {constants.HARPOON_HIT_SPEED:.2f}',
        f'${constants.HARPOON_COST}',
        f'Range: {constants.HARPOON_RANGE}',
        'Air'
    ])
    add_button(f'Cryo-Cannon', 'place_cryocannon', constants.CRYOCANNON_COST, pygame.image.load('assets/cryocannon_m.png'), [
        f'Damage: {constants.CRYOCANNON_DAMAGE}',
        f'Hit Speed: {constants.CRYOCANNON_HIT_SPEED:.2f}',
        f'${constants.CRYOCANNON_COST}',
        f'Range: {constants.CRYOCANNON_RANGE}',
        'Ground,',
        'Air'
    ])
    add_button(f'Laser', 'place_laser', constants.LASER_COST, pygame.image.load('assets/laser.png'), [
        f'Damage: {constants.LASER_DAMAGE:.2f}',
        f'Hit Speed: {constants.LASER_HIT_SPEED:.2f}',
        f'${constants.LASER_COST}',
        f'Range: {constants.LASER_RANGE}',
        'Ground,',
        'Air'
    ])
    add_button(f'Freezer', 'place_freezer', constants.FREEZER_COST, pygame.image.load('assets/freezer.png'), [
        f'Damage: 0.0',
        f'Hit Speed: {constants.FREEZER_HIT_SPEED:.2f}',
        f'${constants.FREEZER_COST}',
        f'Range: {constants.FREEZER_RANGE}',
        'Ground,',
        'Air'
    ])
    add_button(f'Flamethrower', 'place_flame', constants.FLAME_COST, pygame.image.load('assets/flame_m.png'), [
        f'Damage: {constants.FLAME_DAMAGE:.2f}',
        f'Hit Speed: {constants.FLAME_HIT_SPEED:.2f}',
        f'${constants.FLAME_COST}',
        f'Range: {constants.FLAME_RANGE}',
        'Ground'
    ])
    add_button(f'Burst Fire', 'place_burst', constants.BURST_COST, pygame.image.load('assets/burstFire_m.png'), [
        f'Damage: {constants.BURST_DAMAGE:.2f}',
        f'Hit Speed: {constants.BURST_HIT_SPEED:.2f}',
        f'${constants.BURST_COST}',
        f'Range: {constants.BURST_RANGE}',
        'Ground'
    ])
    add_button(f'Frost Cannon', 'place_fr_cannon', constants.BURST_COST, pygame.image.load('assets/frost_cannon_m.png'), [
        f'Damage: {constants.FROSTCANNON_DAMAGE:.2f}',
        f'Hit Speed: {constants.FROSTCANNON_HIT_SPEED:.2f}',
        f'${constants.FROSTCANNON_COST}',
        f'Range: {constants.FROSTCANNON_RANGE}',
        'Ground'
    ])

    return {
        'surface': menu_surface,
        'x': menu_x,
        'y': menu_y,
        'buttons': buttons,
        'font': font,
        'stat_font': stat_font,
        'cost_font': cost_font,
        'air_font' : air_font,
        'ground_font' : ground_font,
        'current_page': 0
    }

def draw_menu(screen, menu):
    menu_surface = pygame.Surface((menu['surface'].get_width(), menu['surface'].get_height()), pygame.SRCALPHA)

    cut_amount = 20  # The size of the cut for the corners
    menu_width = menu['surface'].get_width()
    menu_height = menu['surface'].get_height()
    polygon1_points = [
        (menu_width, cut_amount),  # Top-right 
        (0, cut_amount),  # Top-left 
        (cut_amount, 0),  # Top-left 
        (menu_width - cut_amount, 0)  # Top-right 

    ]
    polygon2_points = [
        (menu_width, menu_height - cut_amount),  # Bottom-right 
        (menu_width - cut_amount, menu_height),  # Bottom-right 
        (cut_amount, menu_height),  # Bottom-left 
        (0, menu_height - cut_amount),  # Bottom-left 
    ]

    pygame.draw.polygon(menu_surface, (30, 255, 30, 125), polygon1_points)
    pygame.draw.polygon(menu_surface, (30, 255, 30, 125), polygon2_points)

    pygame.draw.lines(menu_surface, (0, 255, 0), False, [polygon1_points[0], polygon1_points[1], polygon1_points[2]], 2)
    pygame.draw.lines(menu_surface, (0, 255, 0), False, [polygon1_points[2], polygon1_points[3], polygon1_points[0]],2)  
    pygame.draw.lines(menu_surface, (0, 255, 0), False, [polygon2_points[0], polygon2_points[1], polygon2_points[2]], 5)
    pygame.draw.lines(menu_surface, (0, 255, 0), False, [polygon2_points[3], polygon2_points[2], polygon2_points[1]],5)  

    screen.blit(menu_surface, (menu['x'], menu['y']))

    # Left menu border
    last_line_start = (menu['x'], menu['y'] + 22)
    last_line_end = (menu['x'], menu['y'] + menu['surface'].get_height() - 20)
    pygame.draw.line(screen, (0, 255, 0), last_line_start, last_line_end, 1)

    # Right menu border
    last_line_start = (menu['x'] + menu['surface'].get_width(), menu['y'] + 22)
    last_line_end = (menu['x'] + menu['surface'].get_width(), menu['y'] + menu['surface'].get_height() - 20)
    pygame.draw.line(screen, (0, 255, 0), last_line_start, last_line_end, 1)

    # Middle divider
    last_line_start = (menu['x'] + 90, menu['y'] + 22)
    last_line_end = (menu['x'] + 90, menu['y'] + menu['surface'].get_height() - 20)
    pygame.draw.line(screen, (0, 255, 0), last_line_start, last_line_end, 2)

    # Pagination settings
    start_index = menu['current_page'] * (constants.buttons_per_page + 0)
    end_index = start_index + constants.buttons_per_page
    visible_buttons = menu['buttons'][start_index:end_index]

    # Draw the visible buttons
    for i, button in enumerate(visible_buttons):
        button_x = menu['x']
        button_y = menu['y'] + 20 + (i * 80)  

        line_start = (button_x, button_y)  
        line_end = (button_x + menu['surface'].get_width(), button_y)  
        pygame.draw.line(screen, (0, 255, 0), line_start, line_end, 2) 

        screen.blit(button['surface'], (button_x, button_y))

        screen.blit(button['text'], (button_x + 100, button_y + 5))

        button_img = pygame.transform.scale(button['button_img'], (55,55))
        screen.blit(button_img, (button_x + 9, button_y + 9))

        #stats inside each button
        stats_lines = button['stats']
        for j, line in enumerate(stats_lines):
            stats_text = menu['stat_font'].render(line, True, (0, 255, 0))
            cost_text = menu['cost_font'].render(line, True, (255, 255, 0))
            air_text = menu['air_font'].render(line, True, (152, 245, 249))
            ground_text = menu['ground_font'].render(line, True, (241, 179, 6))

            if j == 5: #blue air text after ground
                screen.blit(air_text, (button_x + 155, button_y + button['surface'].get_height() // 2.2 + ((j-3) * 15) ))
            if j == 4:  # Ground or air
                if len(stats_lines) ==6: #has both, ground font first
                    screen.blit(ground_text, (button_x + 100, button_y + button['surface'].get_height() // 2.2 + ((j-2) * 15)))
                elif stats_lines[4] =='Ground': #has only ground
                    screen.blit(ground_text, (button_x + 100, button_y + button['surface'].get_height() // 2.2 + ((j-2) * 15)))
                else:
                    screen.blit(air_text, (button_x + 100, button_y + button['surface'].get_height() // 2.2 + ((j-2) * 15)))
            if j == 2:  # cost display to the left
                screen.blit(cost_text, (button_x + 50, button_y + button['surface'].get_height() // 2.5 + (j * 16)))
            if j == 3:  # range display moved up
                screen.blit(stats_text, (button_x + 100, button_y + button['surface'].get_height() // 3.5 + ((j - 1) * 15)))
            if j < 2:
                screen.blit(stats_text, (button_x + 100, button_y + button['surface'].get_height() // 3.5 + (j * 15)))

        # Check if this is the last button on the page
        if i == len(visible_buttons) - 1:
            last_line_start = (button_x, button_y + button['surface'].get_height())
            last_line_end = (button_x + menu['surface'].get_width(), button_y + button['surface'].get_height() + 2)
            pygame.draw.line(screen, (0, 255, 0), last_line_start, last_line_end, 2)

    next_img = pygame.image.load('assets/next.png').convert_alpha()
    prev_img = pygame.image.load('assets/prev.png').convert_alpha()
    next_img = pygame.transform.scale(next_img, (next_img.get_width() * 1.3,next_img.get_height() * 1.3))
    prev_img = pygame.transform.scale(prev_img, (prev_img.get_width()* 1.3, next_img.get_height()* 1.3))

    # Draw "Next" button if there are more pages
    if len(menu['buttons']) > end_index:
        next_button_rect = pygame.Rect(menu['x'] + menu['surface'].get_width() / 2 - 25 / 2, menu['y'] + menu['surface'].get_height() - 24, 20, 24)

        next_img_rect = next_img.get_rect(center=next_button_rect.center)
        screen.blit(next_img, next_img_rect.topleft)

    # Draw "Previous" button if not on the first page
    if menu['current_page'] > 0:
        prev_button_rect = pygame.Rect(menu['x'] + menu['surface'].get_width() / 2 - 25 / 2, menu['y'] + 1, 20, 20)
        prev_img_rect = prev_img.get_rect(center=prev_button_rect.center)
        screen.blit(prev_img, prev_img_rect.topleft)

def handle_menu_click(menu, mouse_pos, node, stage):
    if len(menu['buttons']) > (menu['current_page'] + 1) * 4:
        next_button_rect = pygame.Rect(menu['x'] + menu['surface'].get_width()/2 - 25/2, menu['y'] + menu['surface'].get_height() - 30, 30, 30)
        if next_button_rect.collidepoint(mouse_pos):
            menu['current_page'] += 1
            return 'next'  # Keep the menu open after navigating

    # Handle "Previous" button click
    if menu['current_page'] > 0:
        prev_button_rect = pygame.Rect(menu['x']+ menu['surface'].get_width()/2 - 25/2, menu['y']  + 5, 30, 30)
        if prev_button_rect.collidepoint(mouse_pos):
            menu['current_page'] -= 1
            return 'prev'  # Keep the menu open after navigating

    # Determine which visible buttons are being shown on the current page
    buttons_per_page = constants.buttons_per_page
    start_index = menu['current_page'] * buttons_per_page
    end_index = start_index + buttons_per_page
    visible_buttons = menu['buttons'][start_index:end_index]

    for i, button in enumerate(visible_buttons):
        button_x = menu['x']
        button_y = menu['y'] + 20 + i * 80
        button_width = button['surface'].get_width()
        button_height = button['surface'].get_height()

        # Check if the mouse click is within the button's surface bounds
        if button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height:
            if button['action'] == 'place_cannon':
                if stage.money >= constants.CANNON_COST:
                    stage.place_turret(turret.Cannon, node, constants.CANNON_COST)
                    return True  
                return 'n.e.m'
            elif button['action'] == 'place_minigun':
                if stage.money >= constants.MINIGUN_COST:
                    stage.place_turret(turret.Minigun, node, constants.MINIGUN_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_blaster':
                if stage.money >= constants.BLASTER_COST:
                    stage.place_turret(turret.Blaster, node, constants.BLASTER_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_tesla':
                if stage.money >= constants.TESLA_COST:
                    stage.place_turret(turret.Tesla, node, constants.TESLA_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_harpoon':
                if stage.money >= constants.HARPOON_COST:
                    stage.place_turret(turret.Harpoon, node, constants.HARPOON_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_cryocannon':
                if stage.money >= constants.CRYOCANNON_COST:
                    stage.place_turret(turret.CryoCannon, node, constants.CRYOCANNON_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_laser':
                if stage.money >= constants.LASER_COST:
                    stage.place_turret(turret.Laser, node, constants.LASER_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_freezer':
                if stage.money >= constants.CRYOCANNON_COST:
                    stage.place_turret(turret.Freezer, node, constants.FREEZER_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_flame':
                if stage.money >= constants.FLAME_COST:
                    stage.place_turret(turret.Flame, node, constants.FLAME_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_burst':
                if stage.money >= constants.BURST_COST:
                    stage.place_turret(turret.BurstFire, node, constants.BURST_COST)
                    return True
                return 'n.e.m'
            elif button['action'] == 'place_mine':
                if stage.money >= constants.MINE_COST:
                    stage.place_turret(turret.Mine, node, constants.MINE_COST)
                    return True
                return 'n.e.m'
            if button['action'] == 'place_fr_cannon':
                if stage.money >= constants.FROSTCANNON_COST:
                    stage.place_turret(turret.Frost_Cannon, node, constants.FROSTCANNON_COST)
                    return True  
                return 'n.e.m'
    return False  # If no button was clicked, keep the menu open

#--------------------------------------------------
def create_upgrade_menu(turr):
    menu_x = turr.x * constants.TILE_SIZE + 70
    menu_y = turr.y * constants.TILE_SIZE - 70
    if menu_x >= 1180:
        menu_x = turr.x * constants.TILE_SIZE - 150
    if menu_y <= 50:
        menu_y = 50
    menu_rect = pygame.Rect(menu_x, menu_y, 140, 145)
    button_height = 55  
    stat_font = pygame.font.Font(None, 15)
    buttons = []
    font = pygame.font.Font(None,20)

    def add_button(text,action, stats):
        button_rect = pygame.Rect(menu_x, menu_y + 15 + len(buttons) * (button_height + 5), 140, button_height)
        button_text = font.render(text, True, (255, 255, 0))
        buttons.append({'rect': button_rect, 'text': button_text, 'action': action, 'stats': stats})

    add_button(f'Upgrade (${turr.upgrade_cost})', 'upgrade', [])
    add_button(f'Sell        (${int((turr.initial_cost + (turr.level * 0.85 * turr.initial_cost // 2 )) * 0.70)})', 'delete', [])

    return {'rect': menu_rect, 'buttons': buttons, 'font': font, 'stat_font': stat_font, 'turret': turr}


def draw_range(screen, turr):
    inner_radius = turr.range * constants.TILE_SIZE
    outer_radius = turr.range * 1.05 * constants.TILE_SIZE

    range_surface = pygame.Surface((outer_radius * 2, outer_radius * 2), pygame.SRCALPHA)
    range_surface.fill((0, 0, 0, 0))  

    if turr.level < 4:
        pygame.draw.circle(range_surface, (0, 255, 0, 100), (outer_radius, outer_radius), outer_radius)
        pygame.draw.circle(range_surface, (0, 0, 0, 0), (outer_radius, outer_radius), inner_radius)

    pygame.draw.circle(range_surface, (255, 255, 255, 70), (outer_radius, outer_radius), inner_radius)

    blit_x = (turr.x * constants.TILE_SIZE + constants.TILE_SIZE / 2) - outer_radius
    blit_y = (turr.y * constants.TILE_SIZE + constants.TILE_SIZE / 2) - outer_radius

    screen.blit(range_surface, (blit_x, blit_y))


def draw_upgrade_menu(screen, up_menu):
    upgrade_surface = pygame.Surface((up_menu['rect'].width, up_menu['rect'].height), pygame.SRCALPHA)

    cut_amount = 15  
    polygon1_points = [
        (cut_amount, 0),  # Top-left 
        (up_menu['rect'].width - cut_amount, 0),  # Top-right 
        (up_menu['rect'].width, cut_amount),  # Top-right 
        (0, cut_amount)]  # Top-left 
    polygon2_points = [
        (up_menu['rect'].width, up_menu['rect'].height - cut_amount),  # Bottom-right 
        (up_menu['rect'].width - cut_amount, up_menu['rect'].height),  # Bottom-right 
        (cut_amount, up_menu['rect'].height),  # Bottom-left 
        (0, up_menu['rect'].height - cut_amount)]  # Bottom-left 

    pygame.draw.polygon(upgrade_surface, (20, 20, 255, 115), polygon1_points)
    pygame.draw.polygon(upgrade_surface, (20, 20, 255, 115), polygon2_points)

    screen.blit(upgrade_surface, (up_menu['rect'].x, up_menu['rect'].y))

    for button in up_menu['buttons']:
        button_surface = pygame.Surface((button['rect'].width, button['rect'].height), pygame.SRCALPHA)
        button_surface.fill((41, 251, 163, 70))  

        screen.blit(button_surface, (button['rect'].x, button['rect'].y))

        if button['action'] == 'delete':
            screen.blit(button['text'], (button['rect'].x + 5, button['rect'].y + 34))
        else:
            screen.blit(button['text'], (button['rect'].x + 5, button['rect'].y + 5))

    turr_rect = pygame.Rect(up_menu['rect'].x-10, up_menu['rect'].y+45, 160, 55)
    pygame.draw.rect(screen, (10, 10, 200), turr_rect, 1)
    turr_surface = pygame.Surface((160, 55), pygame.SRCALPHA)
    turr_surface.fill((50, 50, 200, 210))
    screen.blit(turr_surface, (up_menu['rect'].x-10, up_menu['rect'].y+45))

    lvl_text = up_menu['font'].render(f'Level {up_menu['turret'].level + 1}', True, (255, 255, 0))
    screen.blit(lvl_text, (turr_rect.topleft[0]+5, turr_rect.topleft[1]+20))

    up_stats_font = pygame.font.Font(None, 14)
    if up_menu['turret'].damage:
        damage_text = up_stats_font.render(f'damage: {up_menu['turret'].damage:.2f}', True, (255, 255, 0))
        damage_up = up_stats_font.render(f'    +{up_menu['turret'].damage/10:.2f}', True, (0, 255, 0))
        screen.blit(damage_text, (turr_rect.topleft[0] + 59, turr_rect.topleft[1] + 5))
        screen.blit(damage_up, (turr_rect.topleft[0] + 122, turr_rect.topleft[1] + 5))

    hit_speed_text = up_stats_font.render(f'hit speed: {up_menu['turret'].hit_speed:.2f}', True, (255, 255, 0))
    hit_speed_up = up_stats_font.render(f'   -{up_menu['turret'].hit_speed/20:.3f}', True, (0, 255, 0))

    range_text = up_stats_font.render(f'range: {up_menu['turret'].range:.2f}', True, (255, 255, 0))
    range_up = up_stats_font.render(f'   +{up_menu['turret'].range / 20:.2f}', True, (0, 255, 0))

    screen.blit(hit_speed_text, (turr_rect.topleft[0] + 59, turr_rect.topleft[1] + 20))
    screen.blit(range_text, (turr_rect.topleft[0] + 59, turr_rect.topleft[1] + 35))

    if up_menu['turret'].level <4:
        screen.blit(hit_speed_up, (turr_rect.topleft[0] + 122, turr_rect.topleft[1] + 20))
        screen.blit(range_up, (turr_rect.topleft[0] + 122, turr_rect.topleft[1] + 35))

def handle_upgrade_menu_click(up_menu, mouse_pos, turr, stage):
    for button in up_menu['buttons']:
        if button['rect'].collidepoint(mouse_pos):
            if button['action'] == 'upgrade' and stage.money >= turr.upgrade_cost:
                if mouse_pos[1] < button['rect'].y +30:
                    turr.upgrade(stage)
            elif button['action'] == 'delete' :
                if mouse_pos[1]> button['rect'].y +25:
                    turr.delete(stage)
            return button['action']
    return None

def draw_wave_alert(screen, stage):
    curr_time = pygame.time.get_ticks()
    time_elapsed = curr_time - stage.lastWaveSent

    if time_elapsed <= 6000:
        if time_elapsed <= 3000:
            alpha_value = 255
        else:
            alpha_value = max(0, 255 - (255 * (time_elapsed - 3000) / 3000))

        alert_surface = pygame.Surface(
            (constants.MAP_WIDTH * constants.TILE_SIZE, constants.MAP_HEIGHT * constants.TILE_SIZE), pygame.SRCALPHA)

        alert_surface.set_alpha(alpha_value)

        font_w = pygame.font.Font(None, 120)
        wave_start_label = font_w.render('Wave', True, (100, 210, 160))
        wave_start_text = font_w.render(f' {int(stage.curr_wave_index + 1)}', True, (100, 210, 160))

        alert_surface.blit(wave_start_label, (
        constants.MAP_WIDTH * constants.TILE_SIZE / 3 -30, constants.MAP_HEIGHT * constants.TILE_SIZE / 3))
        alert_surface.blit(wave_start_text, (
        constants.MAP_WIDTH * constants.TILE_SIZE / 3 + 175, constants.MAP_HEIGHT * constants.TILE_SIZE / 3))

        screen.blit(alert_surface, (0, 0))

class Stage:
    def __init__(self, waves, bg_img, mapfile, screen, stage_health, starting_money, overlay_path, is_endless):
        self.waves_list = waves
        self.curr_wave_index = 0
        self.bg_img = bg_img
        self.overlay = overlay_path
        self.mapfile = mapfile
        self.nodes = None
        self.game_map = None
        self.screen = screen
        self.turrets = []
        self.money = starting_money
        self.lastWaveSent = pygame.time.get_ticks()
        self.stage_health = stage_health
        self.max_health = stage_health
        self.paused = False
        self.game_speed = 1
        self.endless = is_endless
        self.generated_wave = None
        self.won = False
        self.powerUps = []
        self.used_powerUps = []
        self.anims = []
        self.paused_time = 0

    def next_wave(self):
        if self.curr_wave_index < len(self.waves_list)-1:
            self.curr_wave_index += 1
            self.waves_list[self.curr_wave_index].all_dead = False
            self.lastWaveSent = pygame.time.get_ticks()
            self.generated_wave = self.waves_list[self.curr_wave_index]
        elif self.endless:
            self.generated_wave = self.get_rand_wave()
            self.curr_wave_index += 1
            self.lastWaveSent = pygame.time.get_ticks()
        else:
            self.won = True

    def get_rand_wave(self):
        rand_wave_index = random.randint(0, len(self.waves_list)-1)
        rand_path = self.waves_list[rand_wave_index].path

        rand_wave_mon_index = random.randint(0, len(self.waves_list)-1)
        rand_mon_list = self.waves_list[rand_wave_mon_index].monster_list
        stronger_mon_list = []
        for group in rand_mon_list:
            if group[0] =='D': #not increaaseing monster D count
                stronger_group = (group[0], group[1])
            if group[0] =='G': #not increaaseing monster G count
                stronger_group = (group[0], group[1])
            else:
                stronger_group = (group[0], group[1]+self.curr_wave_index-len(self.waves_list))
            if not group[0] == 'A': #monster A eliminated in endless waves
                stronger_mon_list.append(stronger_group)

        spawn_delay = self.waves_list[rand_wave_mon_index].spawnDelay - (self.curr_wave_index-len(self.waves_list))*10
        if spawn_delay <= 300:
            spawn_delay = 300
        return Wave(rand_path[0],rand_path[-1], rand_path, stronger_mon_list, spawn_delay)

    def update_powerUps(self):
        curr_time = pygame.time.get_ticks()
        for pup in self.powerUps:
            if curr_time >= pup.remove_time:
                self.powerUps.remove(pup)

    def update_stage(self, dt):
        self.update_powerUps()
        if self.endless and self.curr_wave_index > len(self.waves_list)-1:
            if self.generated_wave.all_dead:
                self.next_wave()
            self.generated_wave.update_wave(dt, self)
        elif self.waves_list[self.curr_wave_index].all_dead:
            self.next_wave()
        else:
            self.waves_list[self.curr_wave_index].update_wave(dt, self)
            self.generated_wave = self.waves_list[self.curr_wave_index]
        for turr in self.turrets:
            if turr.is_blown:
                self.turrets.remove(turr)
                self.anims.append(animations.MineAnimation(turr.x, turr.y))

    def set_map(self):
        self.game_map = load_map(self.mapfile)
        self.nodes = [Node(x, y) for y in range(constants.MAP_HEIGHT) for x in range(constants.MAP_WIDTH) if self.game_map[y][x] == 1]

    def place_turret(self, turret_class, node, cost):

        if self.money >= cost:
            self.money -= cost
            self.turrets.append(turret_class(node.x // constants.TILE_SIZE, node.y // constants.TILE_SIZE))

    def remove_turret(self, given_turret):
        self.turrets.remove(given_turret)

    def checkMoney(self):
        return self.money

    def add_money(self, amount):
        self.money += amount

    def subtract_health(self, amount):
        self.stage_health -= amount
        if self.stage_health <= 0:
            self.stage_health = 0
            self.curr_wave_index = 0
            self.turrets = []

    def update_game_speed(self):
        if self.game_speed == 1:
            self.game_speed = 2
        elif self.game_speed == 2:
            self.game_speed = 3
        else:
            self.game_speed = 1

    def add_powerUp(self, pos):
        p = random.randint(1,4)
        if p == 4:
            self.powerUps.append(powerUp.slower(pos, self))
        if p == 3:
            self.powerUps.append(powerUp.tnt(pos, self))
        if p == 2:
            self.powerUps.append(powerUp.coin(pos, self))
        if p == 1:
            self.powerUps.append(powerUp.aid(pos, self))

def show_starter(screen):
    img = pygame.image.load('assets/starter.png')
    img = pygame.transform.scale(img, (img.get_width()/1.2, img.get_height()/1.2))
    pygame.display.set_caption("Tower Defense Game - Select Mode")
    font = pygame.font.Font(None, 29)
    screen_size = img.get_size()  
    screen.blit(img, (0, 0))  

    title = font.render("Main Menu", True, (100, 230, 110))
    title_bg_width = title.get_width() + 40  
    title_bg_height = title.get_height() + 20  
    title_bg_color = (255, 255, 255)  
    title_bg_alpha = 0  
    title_border_radius = 10 

    title_bg_surf = pygame.Surface((title_bg_width, title_bg_height), pygame.SRCALPHA)

    pygame.draw.rect(title_bg_surf, (*title_bg_color, title_bg_alpha), title_bg_surf.get_rect(),
                     border_radius=title_border_radius)

    title_bg_pos = (screen_size[0] / 3  , screen_size[1]/4.39)
    title_pos = (title_bg_pos[0] + 40, title_bg_pos[1] + 10)  

    screen.blit(title_bg_surf, title_bg_pos)
    screen.blit(title, title_pos)

    button_width, button_height = img.get_width()/1.62, img.get_height()/6.1
    button_color = (255, 255, 255)  
    button_alpha = 0  
    border_radius = 20

    normal_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    endless_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)

    pygame.draw.rect(normal_surf, (*button_color, button_alpha), normal_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(endless_surf, (*button_color, button_alpha), endless_surf.get_rect(),
                     border_radius=border_radius)

    normal_pos = (img.get_width()/5.10, img.get_height()/2.8)
    endless_pos = (img.get_width()/5.1, img.get_height()/1.8)

    screen.blit(normal_surf, normal_pos)
    screen.blit(endless_surf, endless_pos)

    pygame.display.flip()

    normal_rect = pygame.Rect(normal_pos, (button_width, button_height))
    endless_rect = pygame.Rect(endless_pos, (button_width, button_height))

    return normal_rect, endless_rect

def show_start_screen(screen, prompt):
    open_img = pygame.image.load('assets/open_menu.jpg')

    pygame.display.set_caption("Tower Defense Game - Select Stage")
    font = pygame.font.Font(None, 36)
    screen_size = open_img.get_size()  
    screen.blit(open_img, (0, 0))  

    title = font.render("Choose a Stage", True, (0, 0, 0))

    title_bg_width = title.get_width() + 40 
    title_bg_height = title.get_height() + 20  
    title_bg_color = (255, 255, 255)  
    title_bg_alpha = 128  
    title_border_radius = 10  

    title_bg_surf = pygame.Surface((title_bg_width, title_bg_height), pygame.SRCALPHA)

    pygame.draw.rect(title_bg_surf, (*title_bg_color, title_bg_alpha), title_bg_surf.get_rect(),
                     border_radius=title_border_radius)

    title_bg_pos = (screen_size[0] // 2 - title_bg_width // 2, 50)
    title_pos = (title_bg_pos[0] + 20, title_bg_pos[1] + 10)  
    screen.blit(title_bg_surf, title_bg_pos)
    screen.blit(title, title_pos)

    button_width, button_height = 200, 50
    button_color = (255, 255, 255)  
    button_alpha = 0
    border_radius = 50

    stage1_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    stage2_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    stage3_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    choose_mode_surf = pygame.Surface((115, 100), pygame.SRCALPHA)
    quit_surf = pygame.Surface((115, 100), pygame.SRCALPHA)
    empty_surf = pygame.Surface((115, 100), pygame.SRCALPHA)

    pygame.draw.rect(stage1_button_surf, (*button_color, button_alpha), stage1_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(stage2_button_surf, (*button_color, button_alpha), stage2_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(stage3_button_surf, (*button_color, button_alpha), stage3_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(choose_mode_surf, (*button_color, button_alpha), choose_mode_surf.get_rect(),
                     border_radius=60)
    pygame.draw.rect(quit_surf, (*button_color, button_alpha), quit_surf.get_rect(),
                     border_radius=60)
    pygame.draw.rect(empty_surf, (*button_color, button_alpha), quit_surf.get_rect(),
                     border_radius=60)

    button_spacing = 64
    total_width = button_width * 3 + button_spacing * 2
    start_x = (screen_size[0] - total_width) // 2  

    stage1_button_pos = (start_x+17, screen_size[1] / 3.3 )
    stage2_button_pos = (start_x +8+ button_width + button_spacing, screen_size[1] / 3.3 )
    stage3_button_pos = (start_x + (button_width + button_spacing) * 2, screen_size[1] / 3.3 )
    choose_mode_pos = (start_x + 310, screen_size[1] / 1.28)
    quit_pos = (start_x + 50, screen_size[1] / 1.29)
    empty_pos = (start_x + 170, screen_size[1] / 1.29)
    empty_pos2 = (start_x + 450, screen_size[1] / 1.29)
    empty_pos3 = (start_x + 570, screen_size[1] / 1.29)


    screen.blit(stage1_button_surf, stage1_button_pos)
    screen.blit(stage2_button_surf, stage2_button_pos)
    screen.blit(stage3_button_surf, stage3_button_pos)
    screen.blit(choose_mode_surf, choose_mode_pos)
    screen.blit(quit_surf, quit_pos)
    screen.blit(empty_surf, empty_pos)
    screen.blit(empty_surf, empty_pos2)
    screen.blit(empty_surf, empty_pos3)
    screen.blit(font.render("Stage 1", True, (200, 200, 200)), (stage1_button_pos[0] + 50, stage1_button_pos[1] + 10))
    screen.blit(font.render("Stage 2", True, (200, 200, 200)), (stage2_button_pos[0] + 50, stage2_button_pos[1] + 10))
    screen.blit(font.render("Stage 3", True, (200, 200, 200)), (stage3_button_pos[0] + 50, stage3_button_pos[1] + 10))
    screen.blit(pygame.font.Font(None, 20).render("Main menu", True, (200, 200, 200)), (choose_mode_pos[0] +23, choose_mode_pos[1] + 110))

    
    if prompt:
        bg_surface =  pygame.Surface((screen_size[0], screen_size[1]),
                                        pygame.SRCALPHA)
        bg_surface.fill((0,0,0,130))

        screen.blit(bg_surface, (0, 0))

        prompt_surf = pygame.Surface((400, 300), pygame.SRCALPHA)
        prompt_color = (0, 0, 0)
        pygame.draw.rect(prompt_surf, (*(prompt_color), 210), prompt_surf.get_rect(),
                     border_radius=border_radius)
        screen.blit(prompt_surf, (screen_size[0]/2 - 200, screen_size[1] / 2 - 150 ))
        screen.blit(font.render("Nothing to see here :/", True, (200, 200, 200)), (screen_size[0]/2 - 130, screen_size[1] / 2 - 30 ))
    pygame.display.flip()

    stage1_button_rect = pygame.Rect(stage1_button_pos, (button_width, button_height))
    stage2_button_rect = pygame.Rect(stage2_button_pos, (button_width, button_height))
    stage3_button_rect = pygame.Rect(stage3_button_pos, (button_width, button_height))
    choose_mode_rect = pygame.Rect(choose_mode_pos, (115, 100))
    quit_rect = pygame.Rect(quit_pos, (110, 110))
    empty_rect = pygame.Rect(empty_pos, (110, 110))
    empty_rect2 = pygame.Rect(empty_pos2, (110, 110))
    empty_rect3 = pygame.Rect(empty_pos3, (110, 110))

    return stage1_button_rect, stage2_button_rect, stage3_button_rect, choose_mode_rect, quit_rect, empty_rect, empty_rect2, empty_rect3

def show_lose_screen(screen, prompt):
    open_img = pygame.image.load('assets/open_menu.jpg')

    pygame.display.set_caption("Tower Defense Game - Select Stage")
    font = pygame.font.Font(None, 36)
    screen_size = open_img.get_size()  
    screen.blit(open_img, (0, 0))  

    title = font.render("You Lose", True, (0, 0, 0))

    title_bg_width = title.get_width() + 40 
    title_bg_height = title.get_height() + 20  
    title_bg_color = (255, 255, 255)  
    title_bg_alpha = 128  
    title_border_radius = 10  

    title_bg_surf = pygame.Surface((title_bg_width, title_bg_height), pygame.SRCALPHA)

    pygame.draw.rect(title_bg_surf, (*title_bg_color, title_bg_alpha), title_bg_surf.get_rect(),
                     border_radius=title_border_radius)

    title_bg_pos = (screen_size[0] // 2 - title_bg_width // 2, 50)
    title_pos = (title_bg_pos[0] + 20, title_bg_pos[1] + 10)  
    screen.blit(title_bg_surf, title_bg_pos)
    screen.blit(title, title_pos)

    button_width, button_height = 200, 50
    button_color = (255, 255, 255)  
    button_alpha = 0
    border_radius = 50

    stage1_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    stage2_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    stage3_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    choose_mode_surf = pygame.Surface((115, 100), pygame.SRCALPHA)
    quit_surf = pygame.Surface((115, 100), pygame.SRCALPHA)
    empty_surf = pygame.Surface((115, 100), pygame.SRCALPHA)

    pygame.draw.rect(stage1_button_surf, (*button_color, button_alpha), stage1_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(stage2_button_surf, (*button_color, button_alpha), stage2_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(stage3_button_surf, (*button_color, button_alpha), stage3_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(choose_mode_surf, (*button_color, button_alpha), choose_mode_surf.get_rect(),
                     border_radius=60)
    pygame.draw.rect(quit_surf, (*button_color, button_alpha), quit_surf.get_rect(),
                     border_radius=60)
    pygame.draw.rect(empty_surf, (*button_color, button_alpha), quit_surf.get_rect(),
                     border_radius=60)

    button_spacing = 64
    total_width = button_width * 3 + button_spacing * 2
    start_x = (screen_size[0] - total_width) // 2  

    stage1_button_pos = (start_x+17, screen_size[1] / 3.3 )
    stage2_button_pos = (start_x +8+ button_width + button_spacing, screen_size[1] / 3.3 )
    stage3_button_pos = (start_x + (button_width + button_spacing) * 2, screen_size[1] / 3.3 )
    choose_mode_pos = (start_x + 310, screen_size[1] / 1.28)
    quit_pos = (start_x + 50, screen_size[1] / 1.29)
    empty_pos = (start_x + 170, screen_size[1] / 1.29)
    empty_pos2 = (start_x + 450, screen_size[1] / 1.29)
    empty_pos3 = (start_x + 570, screen_size[1] / 1.29)


    screen.blit(stage1_button_surf, stage1_button_pos)
    screen.blit(stage2_button_surf, stage2_button_pos)
    screen.blit(stage3_button_surf, stage3_button_pos)
    screen.blit(choose_mode_surf, choose_mode_pos)
    screen.blit(quit_surf, quit_pos)
    screen.blit(empty_surf, empty_pos)
    screen.blit(empty_surf, empty_pos2)
    screen.blit(empty_surf, empty_pos3)
    screen.blit(font.render("Stage 1", True, (200, 200, 200)), (stage1_button_pos[0] + 50, stage1_button_pos[1] + 10))
    screen.blit(font.render("Stage 2", True, (200, 200, 200)), (stage2_button_pos[0] + 50, stage2_button_pos[1] + 10))
    screen.blit(font.render("Stage 3", True, (200, 200, 200)), (stage3_button_pos[0] + 50, stage3_button_pos[1] + 10))
    screen.blit(pygame.font.Font(None, 20).render("Main menu", True, (200, 200, 200)), (choose_mode_pos[0] +23, choose_mode_pos[1] + 110))

    
    if prompt:
        bg_surface =  pygame.Surface((screen_size[0], screen_size[1]),
                                        pygame.SRCALPHA)
        bg_surface.fill((0,0,0,130))

        screen.blit(bg_surface, (0, 0))

        prompt_surf = pygame.Surface((400, 300), pygame.SRCALPHA)
        prompt_color = (0, 0, 0)
        pygame.draw.rect(prompt_surf, (*(prompt_color), 210), prompt_surf.get_rect(),
                     border_radius=border_radius)
        screen.blit(prompt_surf, (screen_size[0]/2 - 200, screen_size[1] / 2 - 150 ))
        screen.blit(font.render("Nothing to see here :/", True, (200, 200, 200)), (screen_size[0]/2 - 130, screen_size[1] / 2 - 30 ))
    pygame.display.flip()

    stage1_button_rect = pygame.Rect(stage1_button_pos, (button_width, button_height))
    stage2_button_rect = pygame.Rect(stage2_button_pos, (button_width, button_height))
    stage3_button_rect = pygame.Rect(stage3_button_pos, (button_width, button_height))
    choose_mode_rect = pygame.Rect(choose_mode_pos, (115, 100))
    quit_rect = pygame.Rect(quit_pos, (110, 110))
    empty_rect = pygame.Rect(empty_pos, (110, 110))
    empty_rect2 = pygame.Rect(empty_pos2, (110, 110))
    empty_rect3 = pygame.Rect(empty_pos3, (110, 110))

    return stage1_button_rect, stage2_button_rect, stage3_button_rect, choose_mode_rect, quit_rect, empty_rect, empty_rect2, empty_rect3

def show_win_screen(screen, prompt):
    open_img = pygame.image.load('assets/open_menu.jpg')

    pygame.display.set_caption("Tower Defense Game - Select Stage")
    font = pygame.font.Font(None, 36)
    screen_size = open_img.get_size()  
    screen.blit(open_img, (0, 0))  

    title = font.render("You Win", True, (0, 0, 0))

    title_bg_width = title.get_width() + 40 
    title_bg_height = title.get_height() + 20  
    title_bg_color = (255, 255, 255)  
    title_bg_alpha = 128  
    title_border_radius = 10  

    title_bg_surf = pygame.Surface((title_bg_width, title_bg_height), pygame.SRCALPHA)

    pygame.draw.rect(title_bg_surf, (*title_bg_color, title_bg_alpha), title_bg_surf.get_rect(),
                     border_radius=title_border_radius)

    title_bg_pos = (screen_size[0] // 2 - title_bg_width // 2, 50)
    title_pos = (title_bg_pos[0] + 20, title_bg_pos[1] + 10)  
    screen.blit(title_bg_surf, title_bg_pos)
    screen.blit(title, title_pos)

    button_width, button_height = 200, 50
    button_color = (255, 255, 255)  
    button_alpha = 0
    border_radius = 50

    stage1_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    stage2_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    stage3_button_surf = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    choose_mode_surf = pygame.Surface((115, 100), pygame.SRCALPHA)
    quit_surf = pygame.Surface((115, 100), pygame.SRCALPHA)
    empty_surf = pygame.Surface((115, 100), pygame.SRCALPHA)

    pygame.draw.rect(stage1_button_surf, (*button_color, button_alpha), stage1_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(stage2_button_surf, (*button_color, button_alpha), stage2_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(stage3_button_surf, (*button_color, button_alpha), stage3_button_surf.get_rect(),
                     border_radius=border_radius)
    pygame.draw.rect(choose_mode_surf, (*button_color, button_alpha), choose_mode_surf.get_rect(),
                     border_radius=60)
    pygame.draw.rect(quit_surf, (*button_color, button_alpha), quit_surf.get_rect(),
                     border_radius=60)
    pygame.draw.rect(empty_surf, (*button_color, button_alpha), quit_surf.get_rect(),
                     border_radius=60)

    button_spacing = 64
    total_width = button_width * 3 + button_spacing * 2
    start_x = (screen_size[0] - total_width) // 2  

    stage1_button_pos = (start_x+17, screen_size[1] / 3.3 )
    stage2_button_pos = (start_x +8+ button_width + button_spacing, screen_size[1] / 3.3 )
    stage3_button_pos = (start_x + (button_width + button_spacing) * 2, screen_size[1] / 3.3 )
    choose_mode_pos = (start_x + 310, screen_size[1] / 1.28)
    quit_pos = (start_x + 50, screen_size[1] / 1.29)
    empty_pos = (start_x + 170, screen_size[1] / 1.29)
    empty_pos2 = (start_x + 450, screen_size[1] / 1.29)
    empty_pos3 = (start_x + 570, screen_size[1] / 1.29)


    screen.blit(stage1_button_surf, stage1_button_pos)
    screen.blit(stage2_button_surf, stage2_button_pos)
    screen.blit(stage3_button_surf, stage3_button_pos)
    screen.blit(choose_mode_surf, choose_mode_pos)
    screen.blit(quit_surf, quit_pos)
    screen.blit(empty_surf, empty_pos)
    screen.blit(empty_surf, empty_pos2)
    screen.blit(empty_surf, empty_pos3)
    screen.blit(font.render("Stage 1", True, (200, 200, 200)), (stage1_button_pos[0] + 50, stage1_button_pos[1] + 10))
    screen.blit(font.render("Stage 2", True, (200, 200, 200)), (stage2_button_pos[0] + 50, stage2_button_pos[1] + 10))
    screen.blit(font.render("Stage 3", True, (200, 200, 200)), (stage3_button_pos[0] + 50, stage3_button_pos[1] + 10))
    screen.blit(pygame.font.Font(None, 20).render("Main menu", True, (200, 200, 200)), (choose_mode_pos[0] +23, choose_mode_pos[1] + 110))

    
    if prompt:
        bg_surface =  pygame.Surface((screen_size[0], screen_size[1]),
                                        pygame.SRCALPHA)
        bg_surface.fill((0,0,0,130))

        screen.blit(bg_surface, (0, 0))

        prompt_surf = pygame.Surface((400, 300), pygame.SRCALPHA)
        prompt_color = (0, 0, 0)
        pygame.draw.rect(prompt_surf, (*(prompt_color), 210), prompt_surf.get_rect(),
                     border_radius=border_radius)
        screen.blit(prompt_surf, (screen_size[0]/2 - 200, screen_size[1] / 2 - 150 ))
        screen.blit(font.render("Nothing to see here :/", True, (200, 200, 200)), (screen_size[0]/2 - 130, screen_size[1] / 2 - 30 ))
    pygame.display.flip()

    stage1_button_rect = pygame.Rect(stage1_button_pos, (button_width, button_height))
    stage2_button_rect = pygame.Rect(stage2_button_pos, (button_width, button_height))
    stage3_button_rect = pygame.Rect(stage3_button_pos, (button_width, button_height))
    choose_mode_rect = pygame.Rect(choose_mode_pos, (115, 100))
    quit_rect = pygame.Rect(quit_pos, (110, 110))
    empty_rect = pygame.Rect(empty_pos, (110, 110))
    empty_rect2 = pygame.Rect(empty_pos2, (110, 110))
    empty_rect3 = pygame.Rect(empty_pos3, (110, 110))

    return stage1_button_rect, stage2_button_rect, stage3_button_rect, choose_mode_rect, quit_rect, empty_rect, empty_rect2, empty_rect3


def get_stage(num, is_endless):
    screen = pygame.display.set_mode((constants.MAP_WIDTH * constants.TILE_SIZE * 0.8, constants.MAP_HEIGHT * constants.TILE_SIZE * 0.75+ constants.STATUS_BAR_HEIGHT),)
    stage1 = Stage(waves=[constants.wave1_1, constants.wave1_2, constants.wave1_3, constants.wave1_4, constants.wave1_5,constants.wave1_6, 
                          constants.wave1_7, constants.wave1_8, constants.wave1_9,constants.wave1_10, constants.wave1_11], 
                          bg_img=load_and_scale_bg('assets/bgg.png', constants.MAP_WIDTH * constants.TILE_SIZE, constants.MAP_HEIGHT * constants.TILE_SIZE),
                   mapfile='assets/map.csv', screen=screen, stage_health=5500, starting_money=6000, overlay_path= 'assets/bgg_overlay.png', is_endless = is_endless)
    
    stage2 = Stage(waves=[constants.wave2_1, constants.wave2_2, constants.wave2_3, constants.wave2_4, constants.wave2_5,
                          constants.wave2_6, constants.wave2_7, constants.wave2_8], bg_img=load_and_scale_bg('assets/bgg2.png',
                          constants.MAP_WIDTH * constants.TILE_SIZE, constants.MAP_HEIGHT * constants.TILE_SIZE),
                   mapfile='assets/map2.csv', screen=screen, stage_health=7000, starting_money=9000, overlay_path= None, is_endless = is_endless)
    
    stage3 = Stage(waves=[constants.wave3_1, constants.wave3_2, constants.wave3_3, constants.wave3_4, constants.wave3_5, constants.wave3_6, constants.wave3_7], bg_img=load_and_scale_bg('assets/bgg3.png',
                          constants.MAP_WIDTH * constants.TILE_SIZE, constants.MAP_HEIGHT * constants.TILE_SIZE),
                   mapfile='assets/map3.csv', screen=screen, stage_health=9000, starting_money= 15000, overlay_path= 'assets/bgg3_overlay.png', is_endless = is_endless)

    stage1 = Stage(waves=[constants.wave1_1], 
                          bg_img=load_and_scale_bg('assets/bgg.png', constants.MAP_WIDTH * constants.TILE_SIZE, constants.MAP_HEIGHT * constants.TILE_SIZE),
                   mapfile='assets/map.csv', screen=screen, stage_health=5500, starting_money=6000, overlay_path= 'assets/bgg_overlay.png', is_endless = is_endless)

    if num == 1:
        return stage1
    if num == 2:
        return stage2
    else:
        return stage3

def main_while(curr_stage): #game loop
    running = True
    screen = pygame.display.set_mode((constants.MAP_WIDTH * constants.TILE_SIZE * 0.8,
                                      constants.MAP_HEIGHT * constants.TILE_SIZE * 0.75 + constants.STATUS_BAR_HEIGHT), )
    pygame.display.set_caption(f"Grave Defence HD")

    curr_stage.set_map()
    bg_image = curr_stage.bg_img

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    menu = None
    curr_node = None
    up_menu = None
    curr_turr = None
    mouse_active = True
    pygame.init()
    pause_start_time = None

    curr_stage.waves_list[curr_stage.curr_wave_index].refresh()
    curr_stage.curr_wave_index = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    handled = False
                    if mouse_active:  
                        if pause_rect.collidepoint(event.pos):
                            curr_stage.paused = not curr_stage.paused
                            if curr_stage.paused:
                                pause_start_time = pygame.time.get_ticks()
                            else:
                                pause_duration = pygame.time.get_ticks() - pause_start_time
                                curr_stage.paused_time = pause_duration
                            print(curr_stage.paused_time)
                    if speed_rect.collidepoint(event.pos) and mouse_active:
                        curr_stage.update_game_speed()

                    if exit_rect.collidepoint(event.pos) and mouse_active:
                        running = False

                    for pup in curr_stage.powerUps:
                        if pup.rect.collidepoint(event.pos):
                            pup.applyEffect(curr_stage)
                            handled = True

                    if not mouse_active:  
                        mouse_active = True
                        handled = True

                    if menu is None: 
                        for node in curr_stage.nodes:
                            if node.rect.collidepoint(event.pos):
                                t = 0
                                for turr in curr_stage.turrets:
                                    if turr.rect.collidepoint(event.pos):
                                        t += 1
                                if t == 0:
                                    curr_node = node
                                    menu = create_menu(node, font, curr_stage)
                                    handled = True

                    elif menu is not None:  
                        action = handle_menu_click(menu, event.pos, curr_node, curr_stage)
                        if action and action != 'next' and action != 'prev' and action != 'n.e.m':
                            menu = None
                            handled = True
                        if not action:
                            menu = None

                    if up_menu is None:
                        for turr in curr_stage.turrets:
                            if turr.rect.collidepoint(event.pos):
                                curr_turr = turr
                                if not turr.trigger_time and not turr.under_upgrade:
                                    up_menu = create_upgrade_menu(turr)
                                    handled = True

                    elif up_menu is not None:
                        handle_upgrade_menu_click(up_menu, event.pos, curr_turr, curr_stage)
                        up_menu = None
                        handled = True

                    if not handled:
                        if curr_stage.curr_wave_index > len(curr_stage.waves_list)-1:
                            for mon in curr_stage.generated_wave.monsters:
                                if mon.rect.collidepoint(event.pos):
                                    curr_stage.generated_wave.blip_pos = mon.path_index
                                    curr_stage.generated_wave.blip_count = 10
                        else:
                            for mon in curr_stage.waves_list[curr_stage.curr_wave_index].monsters:
                                if mon.rect.collidepoint(event.pos):
                                    curr_stage.waves_list[curr_stage.curr_wave_index].blip_pos = mon.path_index
                                    curr_stage.waves_list[curr_stage.curr_wave_index].blip_count = 10

                    if not handled and mouse_active:
                        if event.pos[1] > 70:
                            mouse_active = False
        dt = clock.tick(constants.FPS) / 1000.0
        current_time = pygame.time.get_ticks()


        if not curr_stage.paused:
            curr_stage.update_stage(dt)

        if curr_stage.won:
            return True

        if curr_stage.stage_health <= 0 :
            running = False

        draw_game(screen, curr_stage.nodes, curr_stage.generated_wave, menu, up_menu, bg_image, curr_turr, mouse_active, curr_stage)
        
        if not curr_stage.paused:
            for turr in curr_stage.turrets:
                elapsed_time = current_time - turr.upgraded_time -turr.pause_while_upgrading
                if elapsed_time >= 3000/curr_stage.game_speed:
                    turr.under_upgrade = False
                if not turr.under_upgrade:
                    turr.update(curr_stage.generated_wave.monsters, current_time, curr_stage.game_speed)
                if turr.under_upgrade:
                    turr.update_upgrade_box(current_time - turr.pause_while_upgrading, curr_stage.game_speed)

        else:
            curr_stage.paused_time = current_time - pause_start_time
            for turr in curr_stage.turrets:
                if turr.under_upgrade:
                    turr.pause_while_upgrading = current_time - pause_start_time
                    
def main():  #screen Launcher
    os.environ['SDL_VIDEO_CENTERED'] = "1"
    pygame.init()
    starter_img = pygame.image.load('assets/starter.png')
    open_img = pygame.image.load('assets/open_menu.jpg')
    screen = pygame.display.set_mode((starter_img.get_width()/1.2, starter_img.get_height()/1.2))
    stage_selected = False
    endless = None
    no_mode = True
    current_stage = None
    reset_mode = False

    while no_mode:
        normal_rect, endless_rect = show_starter(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if normal_rect.collidepoint(event.pos):
                    endless = False
                    no_mode = False
                elif endless_rect.collidepoint(event.pos):
                    endless = True
                    no_mode = False
    screen = pygame.display.set_mode((open_img.get_width(), open_img.get_height()))
    prompt = False
    while not stage_selected:
        stage1_button, stage2_button, stage3_button, choose_mode, quit_button, empty_button, empty_button2, empty_button3= show_start_screen(screen, prompt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if empty_button.collidepoint(event.pos) or empty_button2.collidepoint(event.pos) or empty_button3.collidepoint(event.pos):
                    prompt = not prompt
                elif stage1_button.collidepoint(event.pos) and not prompt:
                    current_stage = get_stage(1, endless)
                    stage_selected = True
                elif stage2_button.collidepoint(event.pos) and not prompt:
                    current_stage = get_stage(2, endless)
                    stage_selected = True
                elif stage3_button.collidepoint(event.pos) and not prompt:
                    current_stage = get_stage(3, endless)
                    stage_selected = True
                elif choose_mode.collidepoint(event.pos) and not prompt:
                    reset_mode = True
                    no_mode = True
                    stage_selected = True
                elif quit_button.collidepoint(event.pos) and not prompt:
                    pygame.quit()
                else:
                    prompt = False

    # After selecting the stage, reinitialize the screen with the game size
    pygame.display.set_caption(f"Grave Defence HD")
    # Proceed with the game after stage selection
    while True: # never ending stage choosing
        if no_mode:
            screen = pygame.display.set_mode((starter_img.get_width() / 1.2, starter_img.get_height() / 1.2))

        while no_mode:
            normal_rect, endless_rect = show_starter(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if normal_rect.collidepoint(event.pos):
                        endless = False
                        stage_selected = False
                        no_mode = False
                    elif endless_rect.collidepoint(event.pos):
                        endless = True
                        stage_selected = False
                        no_mode = False

        if not stage_selected or reset_mode:
            screen = pygame.display.set_mode((open_img.get_width(), open_img.get_height()))

        while not stage_selected or reset_mode:
            stage1_button, stage2_button, stage3_button, choose_mode, quit_button, empty_button, empty_button2, empty_button3= show_start_screen(screen, prompt)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if empty_button.collidepoint(event.pos) or empty_button2.collidepoint(event.pos) or empty_button3.collidepoint(event.pos):
                        prompt = not prompt
                    elif stage1_button.collidepoint(event.pos) and not prompt:
                        current_stage = get_stage(1, endless)
                        stage_selected = True
                        reset_mode = False
                    elif stage2_button.collidepoint(event.pos) and not prompt:
                        current_stage = get_stage(2, endless)
                        stage_selected = True
                        reset_mode = False
                    elif stage3_button.collidepoint(event.pos) and not prompt:
                        current_stage = get_stage(3, endless)
                        stage_selected = True
                        reset_mode = False                        
                    elif choose_mode.collidepoint(event.pos) and not prompt:
                        reset_mode = True
                        no_mode = True
                        stage_selected = True
                    elif quit_button.collidepoint(event.pos) and not prompt:
                        pygame.quit()
                    else:
                        prompt = False

        if not no_mode:
            won = main_while(current_stage)
            if won:
                stage_selected = False
                screen = pygame.display.set_mode((open_img.get_width(), open_img.get_height()))
                while not stage_selected:
                    stage1_button, stage2_button, stage3_button, choose_mode, quit_button, empty_button, empty_button2, empty_button3 = show_win_screen(screen, prompt)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if empty_button.collidepoint(event.pos) or empty_button2.collidepoint(event.pos) or empty_button3.collidepoint(event.pos):
                                prompt = not prompt
                            elif stage1_button.collidepoint(event.pos) and not prompt:
                              current_stage = get_stage(1, endless)
                              stage_selected = True
                              reset_mode = False
                            elif stage2_button.collidepoint(event.pos) and not prompt:
                               current_stage = get_stage(2, endless)
                               stage_selected = True
                               reset_mode = False
                            elif stage3_button.collidepoint(event.pos) and not prompt:
                                current_stage = get_stage(3, endless)
                                stage_selected = True
                                reset_mode = False                        
                            elif choose_mode.collidepoint(event.pos) and not prompt:
                                reset_mode = True
                                no_mode = True
                                stage_selected = True
                            elif quit_button.collidepoint(event.pos) and not prompt:
                                pygame.quit()
                            else:
                                prompt = False
            else:
                stage_selected = False
                screen = pygame.display.set_mode((open_img.get_width(), open_img.get_height()))
                while not stage_selected:
                    stage1_button, stage2_button, stage3_button, choose_mode, quit_button, empty_button, empty_button2, empty_button3 = show_lose_screen(screen, prompt)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if empty_button.collidepoint(event.pos) or empty_button2.collidepoint(event.pos) or empty_button3.collidepoint(event.pos):
                                prompt = not prompt
                            elif stage1_button.collidepoint(event.pos) and not prompt:
                              current_stage = get_stage(1, endless)
                              stage_selected = True
                              reset_mode = False
                            elif stage2_button.collidepoint(event.pos) and not prompt:
                               current_stage = get_stage(2, endless)
                               stage_selected = True
                               reset_mode = False
                            elif stage3_button.collidepoint(event.pos) and not prompt:
                                current_stage = get_stage(3, endless)
                                stage_selected = True
                                reset_mode = False                        
                            elif choose_mode.collidepoint(event.pos) and not prompt:
                                reset_mode = True
                                no_mode = True
                                stage_selected = True
                            elif quit_button.collidepoint(event.pos) and not prompt:
                                pygame.quit()
                            else:
                                prompt = False
if __name__ == "__main__":
    main()