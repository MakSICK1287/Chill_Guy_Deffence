import pygame
import random
import time
import math
import os

pygame.init()

pygame.mixer.init()
is_paused = False
screen_info = pygame.display.Info()
screen_x = 1000
screen_y = 800
screen = pygame.display.set_mode((screen_x, screen_y), pygame.RESIZABLE)
pygame.display.set_caption("Chill Guy Defence")
clock = pygame.time.Clock()

MENU = 0
GAME = 1
SETTINGS = 2
GAME_OVER = 3 
game_state = MENU

fullscreen = False
base_screen_x = 1000
base_screen_y = 800
scaled_screen = pygame.Surface((base_screen_x, base_screen_y))

font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 36)

class Button:
    def __init__(self, x_ratio, y_ratio, width_ratio, height_ratio, text, color, hover_color):
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.width_ratio = width_ratio
        self.height_ratio = height_ratio
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.update_rect()
        
    def update_rect(self):
        screen_width, screen_height = pygame.display.get_surface().get_size()
        width = int(screen_width * self.width_ratio)
        height = int(screen_height * self.height_ratio)
        x = int(screen_width * self.x_ratio - width // 2)
        y = int(screen_height * self.y_ratio - height // 2)
        self.rect = pygame.Rect(x, y, width, height)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=10)

        font_size = min(self.rect.height // 2, 48)
        font = pygame.font.SysFont(None, font_size)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

def create_buttons():
    return {
        'play': Button(0.5, 0.35, 0.2, 0.08, "Play", (0, 100, 0), (0, 150, 0)),
        'settings': Button(0.5, 0.45, 0.2, 0.08, "Settings", (100, 100, 0), (150, 150, 0)),
        'exit': Button(0.5, 0.55, 0.2, 0.08, "Exit", (100, 0, 0), (150, 0, 0)),
        'window': Button(0.5, 0.4, 0.2, 0.08, "Window", (0, 100, 100), (0, 150, 150)),
        'fullscreen': Button(0.5, 0.5, 0.2, 0.08, "Full Screen", (100, 0, 100), (150, 0, 150)),
        'back': Button(0.5, 0.6, 0.2, 0.08, "Back", (100, 100, 100), (150, 150, 150)),
        'restart': Button(0.5, 0.45, 0.2, 0.08, "Restart", (0, 100, 0), (0, 150, 0)),
        'main_menu': Button(0.5, 0.55, 0.2, 0.08, "Main Menu", (100, 0, 0), (150, 0, 0))
    }

buttons = create_buttons()

def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((base_screen_x, base_screen_y), pygame.RESIZABLE)

    for button in buttons.values():
        button.update_rect()

def get_scaled_mouse_pos():
    mouse_pos = pygame.mouse.get_pos()
    screen_width, screen_height = screen.get_size()

    scale_x = screen_width / base_screen_x
    scale_y = screen_height / base_screen_y
    scale = min(scale_x, scale_y)

    offset_x = (screen_width - base_screen_x * scale) / 2
    offset_y = (screen_height - base_screen_y * scale) / 2

    scaled_x = (mouse_pos[0] - offset_x) / scale
    scaled_y = (mouse_pos[1] - offset_y) / scale
    
    return (scaled_x, scaled_y)

def load_image_safe(filename, default_size=(100, 100)):
    image = pygame.image.load(filename)
    return pygame.transform.scale(image, default_size)

def load_sound_safe(filename):
    return pygame.mixer.Sound(filename)

class Tower:
    def __init__(self):
        self.tower_image = load_image_safe("tower.png", (275, 275))
        self.tower_x = 365
        self.tower_y = 225
        self.tower_health = 25
        self.health_bar_length = 275
        self.health_bar_height = 10
        self.tower_max_health = self.tower_health
        self.tower_rect = pygame.Rect(self.tower_x, self.tower_y, 200, 200)
        
    def draw_health_bar(self, surface):
        health_ratio = self.tower_health / self.tower_max_health
        health_width = int(self.health_bar_length * health_ratio)
        health_bar_pos = (self.tower_x, self.tower_y + 260)
        first_color = 0
        second_color = 255
        third_color = 0
        if self.tower_health <= self.tower_max_health / 3:
            first_color = 255
            second_color = 0
            third_color = 0
        elif self.tower_health <= self.tower_max_health / 1.5:
            first_color = 254
            second_color = 138
            third_color = 24
        pygame.draw.rect(surface, (100, 100, 100), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height))
        pygame.draw.rect(surface, (first_color, second_color, third_color), 
                        (*health_bar_pos, health_width, self.health_bar_height))
        pygame.draw.rect(surface, (255, 255, 255), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height), 1)
        
    def draw(self, surface):
        surface.blit(self.tower_image, (self.tower_x, self.tower_y))
        self.draw_health_bar(surface)

class Boss:
    def __init__(self):
        self.boss_r = load_image_safe("boss_r.png", (225, 200))
        self.boss_l = load_image_safe("boss_l.png", (225, 200))
        self.side = random.randint(0, 3)
        self.boss_x = 0
        self.boss_y = 0
        self.is_buffed = False
        if self.side == 0: 
            self.boss_y = random.randint(0, screen_y - 225)
            self.boss_x = -225
        elif self.side == 1:
            self.boss_y = -200
            self.boss_x = random.randint(0, screen_x - 225)
        elif self.side == 2: 
            self.boss_y = random.randint(0, screen_y - 200)
            self.boss_x = screen_x
        else:
            self.boss_y = screen_y
            self.boss_x = random.randint(0, screen_x - 225)
            
        self.boss_health = 2000
        self.boss_max_health = self.boss_health
        self.boss_speed = 1
        self.length = 225
        self.height = 200
        self.health_bar_length = 250
        self.health_bar_height = 15
        self.dx = 0
        self.dy = 0
        
    def draw_health_bar(self, surface):
        first_color = 0
        second_color = 255
        third_color = 0
        if self.boss_health <= self.boss_max_health / 3:
            first_color = 255
            second_color = 0
            third_color = 0
        elif self.boss_health <= self.boss_max_health / 1.5:
            first_color = 254
            second_color = 138
            third_color = 24
        health_ratio = self.boss_health / self.boss_max_health
        health_width = int(self.health_bar_length * health_ratio)
        health_bar_pos = (self.boss_x, self.boss_y + 205)
        pygame.draw.rect(surface, (100, 100, 100), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height))
        pygame.draw.rect(surface, (first_color, second_color, third_color), 
                        (*health_bar_pos, health_width, self.health_bar_height))
        pygame.draw.rect(surface, (255, 255, 255), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height), 1)
        
    def boss_animation(self, surface):
        if self.dx > 0:
            boss_animation = pygame.transform.scale(self.boss_r, (self.length, self.height))
            surface.blit(boss_animation, (self.boss_x, self.boss_y))
            self.draw_health_bar(surface)
        else:
            boss_animation = pygame.transform.scale(self.boss_l, (self.length, self.height))
            surface.blit(boss_animation, (self.boss_x, self.boss_y))
            self.draw_health_bar(surface)

    def take_damage(self, player):
        if self.side == 0:
            self.boss_x -= 1.3
            self.boss_health -= player.player_attack
        elif self.side == 1:
            self.boss_y -= 1.3
            self.boss_health -= player.player_attack
        elif self.side == 2:
            self.boss_x += 1.3
            self.boss_health -= player.player_attack
        else:
            self.boss_y += 1.3
            self.boss_health -= player.player_attack
            
    def move(self):
        self.dx = 400 - self.boss_x
        self.dy = 300 - self.boss_y
        distance = max(1, (self.dx**2 + self.dy**2)**0.5)
        self.boss_x += (self.dx / distance) * self.boss_speed
        self.boss_y += (self.dy / distance) * self.boss_speed
        
    def check_hit(self):
        boss_rect = pygame.Rect(self.boss_x, self.boss_y, 275, 150)
        return boss_rect.colliderect(pygame.Rect(405, 265, 200, 200))

class Enemies:
    def __init__(self):
        enemy_images = [
            ("crok.png", "crok_r.png", "crok_l.png"),
            ("sahur.png", "sahur_r.png", "sahur_l.png"),
            ("shark.png", "shark_r.png", "shark_l.png"),
        ]
        self.image_info = random.choice(enemy_images)
        
        if "crok" in self.image_info[0]:
            self.enemy_image_r = load_image_safe(self.image_info[1], (50, 50))
            self.enemy_image_l = load_image_safe(self.image_info[2], (50, 50))
            self.speed = 5
            self.health = 20
            self.max_health = self.health
            self.final_health = 80
            self.is_buffed = False
        elif "sahur" in self.image_info[0]:
            self.enemy_image_r = load_image_safe(self.image_info[1], (50, 50))
            self.enemy_image_l = load_image_safe(self.image_info[2], (50, 50))
            self.speed = 3
            self.health = 10
            self.max_health = self.health
            self.final_health = 40
            self.is_buffed = False
        else:
            self.enemy_image_r = load_image_safe(self.image_info[1], (50, 50))
            self.enemy_image_l = load_image_safe(self.image_info[2], (50, 50))
            self.speed = 4
            self.health = 30
            self.max_health = self.health
            self.final_health = 120
            self.is_buffed = False
            
        self.side = random.randint(0, 3)
        self.enemy1_x = 0
        self.enemy1_y = 0
        self.health_bar_length = 50
        self.health_bar_height = 5
        self.dx = 0
        self.dy = 0

        if self.side == 0:
            self.enemy1_y = random.randint(0, screen_y - 50)
            self.enemy1_x = -50
        elif self.side == 1:
            self.enemy1_y = -50
            self.enemy1_x = random.randint(0, screen_x - 50)
        elif self.side == 2: 
            self.enemy1_y = random.randint(0, screen_y - 50)
            self.enemy1_x = screen_x
        else: 
            self.enemy1_y = screen_y
            self.enemy1_x = random.randint(0, screen_x - 50)

    def draw_health_bar(self, surface):
        health_ratio = self.health / self.max_health
        health_width = int(self.health_bar_length * health_ratio)
        health_bar_pos = (self.enemy1_x, self.enemy1_y - 10)
        first_color = 0
        second_color = 255
        third_color = 0
        if self.health <= self.max_health / 3:
            first_color = 255
            second_color = 0
            third_color = 0
        elif self.health <= self.max_health / 1.5:
            first_color = 254
            second_color = 138
            third_color = 24
        pygame.draw.rect(surface, (100, 100, 100), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height))
        pygame.draw.rect(surface, (first_color, second_color, third_color), 
                        (*health_bar_pos, health_width, self.health_bar_height))
        pygame.draw.rect(surface, (255, 255, 255), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height), 1)
        
    def move(self):
        self.dx = 400 - self.enemy1_x
        self.dy = 300 - self.enemy1_y
        distance = max(1, (self.dx**2 + self.dy**2)**0.5)
        self.enemy1_x += (self.dx / distance) * self.speed
        self.enemy1_y += (self.dy / distance) * self.speed
        
    def draw(self, surface):
        if self.dx >= 0:
            surface.blit(self.enemy_image_r, (self.enemy1_x, self.enemy1_y))
            self.draw_health_bar(surface)
        else:
            surface.blit(self.enemy_image_l, (self.enemy1_x, self.enemy1_y))
            self.draw_health_bar(surface)
            
    def animation(self, surface):
        if self.dx >= 0:
            animation = pygame.transform.scale(self.enemy_image_r, (60, 40))
            surface.blit(animation, (self.enemy1_x, self.enemy1_y))
            self.draw_health_bar(surface)
        else:
            animation = pygame.transform.scale(self.enemy_image_l, (60, 40))
            surface.blit(animation, (self.enemy1_x, self.enemy1_y))
            self.draw_health_bar(surface)
            
    def take_damage(self, player):
        if self.side == 0:
            self.enemy1_x -= player.player_knockback
            self.health -= player.player_attack
        elif self.side == 1:
            self.enemy1_y -= player.player_knockback
            self.health -= player.player_attack
        elif self.side == 2:
            self.enemy1_x += player.player_knockback
            self.health -= player.player_attack
        else:
            self.enemy1_y += player.player_knockback
            self.health -= player.player_attack
            
    def check_hit(self):
        enemy_rect = pygame.Rect(self.enemy1_x, self.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(405, 265, 200, 200))

class Player:
    def __init__(self):
        self.player_image_r = pygame.image.load("image_r.png")  
        self.player_image_r = pygame.transform.scale(self.player_image_r, (100, 100))
        self.player_image_l = pygame.image.load("image_l.png")  
        self.player_image_l = pygame.transform.scale(self.player_image_l, (100, 100))
        self.player_stand_r = pygame.image.load("stand_r.png")  
        self.player_stand_r = pygame.transform.scale(self.player_stand_r, (100, 110))
        self.player_stand_l = pygame.image.load("stand_l.png")  
        self.player_stand_l = pygame.transform.scale(self.player_stand_l, (100, 110))
        self.player_size = 100
        self.player_x = 400
        self.player_y = 500
        self.base_attack = 10
        self.player_attack = 10
        self.damage_multiplier = 1.0
        self.power_buff_active = False
        self.player_knockback = 150
        self.player_speed = 6
        self.base_speed = 6
        self.player_score = 0
        self.ultimate_cooldown = 20
        self.ultimate_duration = 5
        self.ultimate_radius = 200
        self.ultimate_active = False
        self.ultimate_start_time = 0
        self.last_ultimate_time = 0
        self.ultimate_ready = True
        self.speed_buff_timer = 0
        self.speed_buff_active = False
        self.speed_buff_count = 0
        self.is_plaing = False
        self.player_turn_r = True
        self.is_still = True

    def is_moving(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            return True
        if keys[pygame.K_d]:
            return True
        if keys[pygame.K_w]:
            return True
        if keys[pygame.K_s]:
            return True

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.player_x > 0:
            self.player_x -= self.player_speed
        if keys[pygame.K_d] and self.player_x < base_screen_x - self.player_size:
            self.player_x += self.player_speed
        if keys[pygame.K_w] and self.player_y > 0:
            self.player_y -= self.player_speed
        if keys[pygame.K_s] and self.player_y < base_screen_y - self.player_size:
            self.player_y += self.player_speed
        if keys[pygame.K_SPACE] and self.ultimate_ready:
            self.activate_ultimate()

    def activate_ultimate(self):
        current_time = time.time()
        ult_sound.play()
        if current_time - self.last_ultimate_time >= self.ultimate_cooldown:
            self.ultimate_active = True
            self.ultimate_start_time = current_time
            self.last_ultimate_time = current_time
            self.ultimate_ready = False
    
    def update_ultimate(self):
        current_time = time.time()
        if self.ultimate_active:
            if current_time - self.ultimate_start_time >= self.ultimate_duration:
                self.ultimate_active = False
        elif current_time - self.last_ultimate_time >= self.ultimate_cooldown:
            self.ultimate_ready = True

    def draw(self, surface):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.player_turn_r = True
            surface.blit(self.player_image_r, (self.player_x, self.player_y))
        elif keys[pygame.K_a]:
            self.player_turn_r = False
            surface.blit(self.player_image_l, (self.player_x, self.player_y))
        else:
            if self.player_turn_r:
                surface.blit(self.player_image_r, (self.player_x, self.player_y))
            elif not self.player_turn_r:
                surface.blit(self.player_image_l, (self.player_x, self.player_y))
            
        if self.ultimate_active:
            ultimate_surface = pygame.Surface((self.ultimate_radius*2, self.ultimate_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(ultimate_surface, (255, 255, 0, 50), 
                             (self.ultimate_radius, self.ultimate_radius), self.ultimate_radius)
            surface.blit(ultimate_surface, (self.player_x - self.ultimate_radius + 50, 
                                        self.player_y - self.ultimate_radius + 50))
    def animation(self, surface):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
           self.player_turn_r = True
           animation = pygame.transform.scale(self.player_image_r, (110,90))
           surface.blit(animation, (self.player_x, self.player_y))
        elif keys[pygame.K_a]:
           self.player_turn_r = False
           animation = pygame.transform.scale(self.player_image_l, (110,90))
           surface.blit(animation, (self.player_x, self.player_y))
        else:
            if self.player_turn_r:
                surface.blit(self.player_image_r, (self.player_x, self.player_y))
            elif not self.player_turn_r:
                surface.blit(self.player_image_l, (self.player_x, self.player_y))

    def draw_stand(self, surface):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            surface.blit(self.player_stand_r, (self.player_x, self.player_y - 90))
        elif keys[pygame.K_a]:
            surface.blit(self.player_stand_l, (self.player_x, self.player_y - 90))
        else:
            if self.player_turn_r:
                surface.blit(self.player_stand_r, (self.player_x, self.player_y - 90))
            elif not self.player_turn_r:
                surface.blit(self.player_stand_l, (self.player_x, self.player_y - 90))


    def punch(self, enemy):
        enemy_rect = pygame.Rect(enemy.enemy1_x, enemy.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(self.player_x, self.player_y, 100, 100)) and enemy.health > 0

    def punch_boss(self, boss):
        boss_rect = pygame.Rect(boss.boss_x, boss.boss_y, 250, 150)
        return boss_rect.colliderect(pygame.Rect(self.player_x, self.player_y, 100, 100)) and boss.boss_health > 0

    def kill_boss(self, boss):
        boss_rect = pygame.Rect(boss.boss_x, boss.boss_y, 250, 150)
        return boss_rect.colliderect(pygame.Rect(self.player_x, self.player_y, 100, 100)) and boss.boss_health <= 0

    def kill(self, enemy):
        enemy_rect = pygame.Rect(enemy.enemy1_x, enemy.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(self.player_x, self.player_y, 100, 100)) and enemy.health <= 0
    
    def ultimate_kill(self, enemy):
        if not self.ultimate_active:
            return False
            
        enemy_center_x = enemy.enemy1_x + 25
        enemy_center_y = enemy.enemy1_y + 25
        player_center_x = self.player_x + 50
        player_center_y = self.player_y + 50
        
        distance = ((enemy_center_x - player_center_x)**2 + (enemy_center_y - player_center_y)**2)**0.5
        return distance <= self.ultimate_radius
    
    def update_buffs(self):
        if self.speed_buff_active:
            current_time = time.time()
            if current_time - self.speed_buff_timer >= 10:
                self.speed_buff_active = False
                self.player_speed = self.base_speed

class Buff:
    def __init__(self):
        self.type = random.choice(["heal", "speed", "power"])
        self.x = random.randint(50, base_screen_x - 50)
        self.y = random.randint(50, base_screen_y - 50)
        self.radius = 20
        self.collected = False
        self.spawn_time = time.time()

        if self.type == "speed":
            self.buff_image = pygame.image.load("speed_buff.png")
            self.buff_image = pygame.transform.scale(self.buff_image , (50,50))
        elif self.type == "power":
            self.buff_image = pygame.image.load("strength_buff.png")
            self.buff_image = pygame.transform.scale(self.buff_image , (60,60))
        else:
            self.buff_image = pygame.image.load("heal_buff.png")
            self.buff_image = pygame.transform.scale(self.buff_image , (50,50))
    
    def draw(self, surface):
        if not self.collected:
            surface.blit(self.buff_image, (self.x - 20, self.y - 20))
    
    def check_collision(self, player):
        if self.collected:
            return False
        
        distance = math.sqrt((self.x - (player.player_x + 50))**2 + (self.y - (player.player_y + 50))**2)
        return distance <= self.radius + 50
    
    def apply(self, player, tower):
        if self.type == "speed":
            player.speed_buff_active = True
            player.speed_buff_timer = time.time()
            player.player_speed = player.base_speed * 1.5
        elif self.type == "power":
            player.damage_multiplier *= 1.1
            player.player_attack = player.base_attack * player.damage_multiplier
            player.power_buff_active = True
        else:
            if tower.tower_health == 24:
                tower.tower_health += 1
            elif tower.tower_health <= 23:
                tower.tower_health += 2
        
        self.collected = True
        
    def should_disappear(self):
        return time.time() - self.spawn_time > 5

enemy_spawn_timer = 0
enemy_buff_timer = 0
animation_timer = 0
buff_spawn_timer = 0
boss_spawn_timer = 0
boss_attack_cooldown = 0
boom_timer = 0
boss_boom_timer = 0
enemy_lvl_timer = 0
boss_animation_timer = 0
boss_punch_timer = 0
steps_sound_timer = 300

def load_game_resources():
    global pause_back, settings_back, back_menu, background, boom, player, tower, enemies, bosses, buffs, buttons
    global menu_music,back_music3,back_music2,back_music1,steps_sound, enemy_die_sound, punch_sound, tower_hit, ult_sound, boss_punch_sound
    global enemy_spawn_timer, enemy_buff_timer, animation_timer, buff_spawn_timer, boss_spawn_timer
    global boss_attack_cooldown, boom_timer, boss_boom_timer, enemy_lvl_timer, steps_sound_timer
    global menu_music_timer,back_music1_timer,boss_animation_timer, boss_punch_timer, player_animation_timer

    buttons = create_buttons()
    
    enemy_die_sound = pygame.mixer.Sound("enemy_die.mp3")
    tower_hit = pygame.mixer.Sound("hit_tower.mp3")
    tower_hit.set_volume(0.5)
    ult_sound = pygame.mixer.Sound("ultimate.mp3")
    ult_sound.set_volume(0.3)
    punch_sound = pygame.mixer.Sound("punch.mp3")
    punch_sound.set_volume(0.3)
    boss_punch_sound = pygame.mixer.Sound("boss_punch.mp3")
    boss_punch_sound.set_volume(0.5)
    steps_sound = pygame.mixer.Sound("steps.mp3")
    back_music1 = pygame.mixer.Sound("back_music1.mp3")
    back_music1.set_volume(0.09)
    back_music1_timer = 0
    back_music2 = pygame.mixer.Sound("back_music2.mp3")
    back_music2.set_volume(0.09)
    back_music3 = pygame.mixer.Sound("back_music3.mp3")
    back_music3.set_volume(0.09)
    menu_music = pygame.mixer.Sound("menu_sound.mp3")
    menu_music.set_volume(0.4)
    menu_music_timer = 0
    
    background = pygame.image.load("background.jpeg")
    background = pygame.transform.scale(background, (base_screen_x, base_screen_y))
    back_menu = pygame.image.load("menu_back.png")
    back_menu = pygame.transform.scale(back_menu, (base_screen_x, base_screen_y))
    settings_back = pygame.image.load("settings_back.jpeg")
    settings_back = pygame.transform.scale(settings_back, (base_screen_x, base_screen_y))
    boom = pygame.image.load("boom.png")
    boom = pygame.transform.scale(boom, (275, 275))

    player = Player()
    tower = Tower()
    enemies = []
    bosses = []
    buffs = []
    
    enemy_spawn_timer = 0
    enemy_buff_timer = 0
    animation_timer = 0
    buff_spawn_timer = 0
    boss_spawn_timer = 0
    boss_attack_cooldown = 0
    boom_timer = 0
    boss_boom_timer = 0
    enemy_lvl_timer = 0
    boss_animation_timer = 0
    steps_sound_timer = 0
    player_animation_timer = 0
    boss_punch_timer = 0

player = Player()
tower = Tower()

load_game_resources()

clock = pygame.time.Clock()
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    scaled_mouse_pos = get_scaled_mouse_pos()
    mouse_clicked = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_clicked = True
        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            for button in buttons.values():
                button.update_rect()

    screen.fill((0, 0, 0))
    scaled_screen.fill((0, 0, 0))
    keys = pygame.key.get_pressed()
    if not (game_state == GAME):
        back_music1.stop()
        back_music2.stop()
        back_music3.stop()
        if menu_music_timer == 0:
            menu_music.play() 
        menu_music_timer += 1
        if menu_music_timer == 450:
            menu_music_timer = 0         
    if game_state == MENU:   
        if fullscreen:
            screen_width, screen_height = screen.get_size()
            back_menu = pygame.transform.scale(back_menu, (screen_width, screen_height))
            screen.blit(back_menu, (0, 0))
        else:
            back_menu = pygame.transform.scale(back_menu, (base_screen_x, base_screen_y))
            screen.blit(back_menu, (0, 0))
        title = font_large.render("Chill Guy Defence", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 
                          int(screen.get_height() * 0.15)))
        
        buttons['play'].check_hover(mouse_pos)
        buttons['settings'].check_hover(mouse_pos)
        buttons['exit'].check_hover(mouse_pos)
        
        buttons['play'].draw(screen)
        buttons['settings'].draw(screen)
        buttons['exit'].draw(screen)
        
        if buttons['play'].is_clicked(mouse_pos, mouse_clicked):
            game_state = GAME
            menu_music.stop()
            load_game_resources()
        elif buttons['settings'].is_clicked(mouse_pos, mouse_clicked):
            game_state = SETTINGS
        elif buttons['exit'].is_clicked(mouse_pos, mouse_clicked):
            running = False
    
    elif game_state == SETTINGS: 
        if fullscreen:
            screen_width, screen_height = screen.get_size()
            settings_back = pygame.transform.scale(settings_back, (screen_width, screen_height))
            screen.blit(settings_back, (0, 0))
        else:
            settings_back = pygame.transform.scale(settings_back, (base_screen_x, base_screen_y))
            screen.blit(settings_back, (0, 0))
        title = font_large.render("Settings", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 
                           int(screen.get_height() * 0.15)))
        
        subtitle = font_medium.render("Screen Mode", True, (255, 255, 255))
        screen.blit(subtitle, (screen.get_width()//2 - subtitle.get_width()//2, 
                              int(screen.get_height() * 0.25)))
        
        buttons['window'].check_hover(mouse_pos)
        buttons['fullscreen'].check_hover(mouse_pos)
        buttons['back'].check_hover(mouse_pos)
        
        buttons['window'].draw(screen)
        buttons['fullscreen'].draw(screen)
        buttons['back'].draw(screen)
        
        if buttons['window'].is_clicked(mouse_pos, mouse_clicked) and fullscreen:
            toggle_fullscreen()
        elif buttons['fullscreen'].is_clicked(mouse_pos, mouse_clicked) and not fullscreen:
            toggle_fullscreen()
        elif buttons['back'].is_clicked(mouse_pos, mouse_clicked):
            game_state = MENU
    
    elif game_state == GAME:
        current_time = time.time() 
        if back_music1_timer == 0:
            back_music1.play()
        if back_music1_timer == 13140:
            back_music2.play()
        if back_music1_timer == 22500:
            back_music3.play()
        back_music1_timer += 1
        if back_music1_timer == 35520:
            back_music1_timer = 0
        if keys[pygame.K_ESCAPE]:
            is_paused = True
        if keys[pygame.K_p]:
            is_paused = False
        if is_paused:
            if keys[pygame.K_o]:
                is_paused = False
                game_state = MENU
                continue
            if fullscreen:
                screen_width, screen_height = screen.get_size()
                pause_back = pygame.image.load("pause_back.png")
                pause_back = pygame.transform.scale(pause_back, (screen_width, screen_height))
                screen.blit(pause_back, (0, 0))
            else:
                pause_back = pygame.image.load("pause_back.png")
                pause_back = pygame.transform.scale(pause_back, (base_screen_x, base_screen_y))
                screen.blit(pause_back, (0, 0))
        else:
            if tower.tower_health <= 0:
                game_state = GAME_OVER
                continue
                
            scaled_screen.blit(background, (0, 0))
            
            tower.draw(scaled_screen)
            
            player.move()
            
            steps_sound_timer += 1
            if player.is_moving() and steps_sound_timer >= 300:
                steps_sound.play()  
                steps_sound_timer = 0 
            if not player.is_moving():
                steps_sound.stop()

            player_animation_timer += 1
            if player_animation_timer <= 8:
                player.draw(scaled_screen)
            else:
                player.animation(scaled_screen)
            if player_animation_timer >= 16:
                player_animation_timer = 0

            player.update_buffs() 

            enemy_spawn_timer += 1
            if enemy_spawn_timer >= 90:
                enemies.append(Enemies())
                enemy_spawn_timer = 0 

            enemy_buff_timer += 1  
            animation_timer += 1 

            for enemy in enemies[:]:
                enemy.move()
                
                if animation_timer <= 10:
                    enemy.draw(scaled_screen)
                else:
                    enemy.animation(scaled_screen)

                if enemy.health <= 0:
                    enemy_die_sound.play()
                    player.player_score += 1
                    enemies.remove(enemy)
                    continue

                if enemy_buff_timer >= 1800 and enemy_buff_timer < 3600 and enemy_lvl_timer == 1 and (not enemy.is_buffed):
                    enemy.health += enemy.health
                    enemy.is_buffed = True
                    enemy.max_health = enemy.health
                    enemy.speed += 1
                if enemy_buff_timer >= 3600 and enemy_buff_timer < 5400 and enemy_lvl_timer == 2 and (not enemy.is_buffed):
                    enemy.health += enemy.health * 2
                    enemy.is_buffed = True
                    enemy.max_health = enemy.health
                    enemy.speed += 1
                if enemy_buff_timer >= 5400 and enemy_buff_timer < 10800 and enemy_lvl_timer == 3 and (not enemy.is_buffed):
                    enemy.health += enemy.health * 3
                    enemy.is_buffed = True
                    enemy.max_health = enemy.health
                    enemy.speed += 1
                if enemy_buff_timer >= 10800 and enemy_lvl_timer == 4 and (not enemy.is_buffed):
                    enemy.health += enemy.health * 20
                    enemy.is_buffed = True
                    enemy.max_health = enemy.health
                    enemy.speed += 5

                if player.ultimate_active and player.ultimate_kill(enemy):
                    enemy_die_sound.play()
                    player.player_score += 1
                    enemies.remove(enemy)
                    continue

                if player.punch(enemy):
                    enemy.take_damage(player)
                    punch_sound.play()
                elif player.kill(enemy) and enemy.check_hit():
                    tower.tower_health -= 1
                    tower_hit.play()
                    enemies.remove(enemy)
                elif player.kill(enemy):
                    enemy_die_sound.play()
                    player.player_score += 1
                    enemies.remove(enemy)
                elif enemy.check_hit():
                    tower.tower_health -= 1
                    tower_hit.play()
                    boom_timer = 180
                    enemies.remove(enemy)

            if animation_timer >= 20:
                animation_timer = 0

            if enemy_buff_timer == 1800 and enemy_lvl_timer == 0:
                enemy_lvl_timer += 1
            if enemy_buff_timer == 3600 and enemy_lvl_timer == 1:
                enemy_lvl_timer += 1
            if enemy_buff_timer == 5400 and enemy_lvl_timer == 2:
                enemy_lvl_timer += 1 
            if enemy_buff_timer == 10800 and enemy_lvl_timer == 3:
                enemy_lvl_timer += 1    

            if boom_timer >= 60:
                scaled_screen.blit(boom, (365, 225))
                boom_timer -= 4

            buff_spawn_timer += 1
            if buff_spawn_timer >= 100:
                buffs.append(Buff())
                buff_spawn_timer = 0

            for buff in buffs[:]:
                buff.draw(scaled_screen)
                if buff.check_collision(player):
                    buff.apply(player, tower)
                    buffs.remove(buff)
                elif buff.should_disappear():
                    buffs.remove(buff)

            boss_spawn_timer += 1
            boss_attack_cooldown += 1
            boss_animation_timer += 1
            if boss_spawn_timer == 1800:
                boss_spawn_timer = 0
                bosses.append(Boss())

            boss_punch_timer += 1
            for boss in bosses[:]:
                boss.move()
                if boss_animation_timer <= 10:
                    boss.length = 225
                    boss.height = 200
                    boss.boss_animation(scaled_screen)
                elif boss_animation_timer <= 20:
                    boss.length = 250
                    boss.height = 180
                    boss.boss_animation(scaled_screen)
                elif boss_animation_timer <= 30:
                    boss.length = 275
                    boss.height = 160
                    boss.boss_animation(scaled_screen)
                elif boss_animation_timer <= 40:
                    boss.length = 275
                    boss.height = 160
                    boss.boss_animation(scaled_screen)
                elif boss_animation_timer <= 50:
                    boss.length = 250
                    boss.height = 180
                    boss.boss_animation(scaled_screen)
                else:
                    boss.length = 225
                    boss.height = 200
                    boss.boss_animation(scaled_screen)

                if enemy_lvl_timer == 2 and not(boss.is_buffed):
                    boss.boss_health += boss.boss_health * 2
                    boss.boss_max_health = boss.boss_health
                    boss.is_buffed = True
                if enemy_lvl_timer == 3 and not(boss.is_buffed):
                    boss.boss_health += boss.boss_health * 3
                    boss.boss_max_health = boss.boss_health
                    boss.is_buffed = True
                if enemy_lvl_timer == 4 and not(boss.is_buffed):
                    boss.boss_health += boss.boss_health * 15
                    boss.boss_max_health = boss.boss_health
                    boss.is_buffed = True

                if boss_animation_timer >= 60:
                    boss_animation_timer = 0
                
                if boss.check_hit():
                    boss.boss_speed = 0
                    if boss_boom_timer > 0:
                        scaled_screen.blit(boom, (365, 225))
                        boss_boom_timer -= 1

                if boss_attack_cooldown >= 180 and boss.check_hit():
                    boss_attack_cooldown = 0
                    boss_boom_timer = 60
                    tower_hit.play()
                    tower.tower_health -= 15

                if player.punch_boss(boss):
                    player.draw_stand(scaled_screen)
                    if boss_punch_timer >= 180:
                        boss_punch_sound.play()
                        boss_punch_timer = 0
                    boss.take_damage(player)
                    boss.boss_speed = 1
                elif player.kill_boss(boss):
                    player.player_score += 10
                    boss_punch_sound.stop()
                    bosses.remove(boss)
                else:
                    boss_punch_sound.stop()
                    boss_punch_timer = 180

            player.update_ultimate()

            if player.ultimate_active:
                ultimate_surface = pygame.Surface((player.ultimate_radius*2, player.ultimate_radius*2), pygame.SRCALPHA)
                pygame.draw.circle(ultimate_surface, (255, 255, 0, 100), 
                            (player.ultimate_radius, player.ultimate_radius), player.ultimate_radius)
                scaled_screen.blit(ultimate_surface, (player.player_x - player.ultimate_radius + 50, 
                                        player.player_y - player.ultimate_radius + 50))

            health_text = font_small.render(f"Health: {tower.tower_health}", True, (255, 0, 0))
            scaled_screen.blit(health_text, (10, 10))

            score_text = font_small.render(f"Score: {player.player_score}", True, (0, 0, 255))
            scaled_screen.blit(score_text, (base_screen_x - score_text.get_width() - 10, 10))

            Lvl_text = font_small.render(f"Level: {enemy_lvl_timer}", True, (219, 172, 52))
            scaled_screen.blit(Lvl_text, (base_screen_x // 2 - Lvl_text.get_width() // 2, base_screen_y - Lvl_text.get_height()*1.5))

            if player.ultimate_active:
                ultimate_status = f"Ultimate: {player.ultimate_duration - (current_time - player.ultimate_start_time):.1f}s"
                color = (0, 255, 0)
            elif player.ultimate_ready:
                ultimate_status = "Ultimate: READY"
                color = (0, 255, 0)
            else:
                cooldown = player.ultimate_cooldown - (current_time - player.last_ultimate_time)
                ultimate_status = f"Ultimate: {cooldown:.1f}s"
                color = (255, 0, 0)

            ultimate_text = font_small.render(ultimate_status, True, color)
            scaled_screen.blit(ultimate_text, (base_screen_x // 2 - ultimate_text.get_width() // 2, 10))

            buff_y_pos = 50

            if player.speed_buff_active:
                remaining_time = max(0, 10 - (current_time - player.speed_buff_timer))
                speed_text = font_small.render(f"Speed x1.5 ({remaining_time:.1f}s)", 
                                    True, (255, 165, 0))
                scaled_screen.blit(speed_text, (10, buff_y_pos))
                buff_y_pos += 30

            if player.damage_multiplier > 1:
                power_text = font_small.render(f"Power x{player.damage_multiplier:.1f}", 
                                True, (255, 255, 0))  
                scaled_screen.blit(power_text, (10, buff_y_pos))
                buff_y_pos += 30
            

            screen_width, screen_height = screen.get_size()
            scale_x = screen_width / base_screen_x
            scale_y = screen_height / base_screen_y
            scale = min(scale_x, scale_y)
        
            new_width = int(base_screen_x * scale)
            new_height = int(base_screen_y * scale)
        
            pos_x = (screen_width - new_width) // 2
            pos_y = (screen_height - new_height) // 2
        
            scaled_display = pygame.transform.scale(scaled_screen, (new_width, new_height))
            screen.blit(scaled_display, (pos_x, pos_y))

    elif game_state == GAME_OVER:

        scaled_screen.blit(background, (0, 0))
        tower.draw(scaled_screen)
        for enemy in enemies:
            enemy.draw(scaled_screen)
        for boss in bosses:
            boss.boss_animation(scaled_screen)
        for buff in buffs:
            buff.draw(scaled_screen)
        player.draw(scaled_screen)

        overlay = pygame.Surface((base_screen_x, base_screen_y), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        scaled_screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(base_screen_x//2, base_screen_y//4))
        scaled_screen.blit(game_over_text, game_over_rect)

        score_text = font_medium.render(f"Final Score: {player.player_score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(base_screen_x//2, base_screen_y//4 + 100))
        scaled_screen.blit(score_text, score_rect)

        restart_button_rect = pygame.Rect(base_screen_x//2 - 160, base_screen_y//2 - 35, 320, 70)
        main_menu_button_rect = pygame.Rect(base_screen_x//2 - 160, base_screen_y//2 + 55, 320, 70)

        scaled_mouse_pos = get_scaled_mouse_pos()
        restart_hovered = restart_button_rect.collidepoint(scaled_mouse_pos)
        main_menu_hovered = main_menu_button_rect.collidepoint(scaled_mouse_pos)
        
        restart_color = (0, 150, 0) if restart_hovered else (0, 100, 0)
        main_menu_color = (150, 0, 0) if main_menu_hovered else (100, 0, 0)
        
        pygame.draw.rect(scaled_screen, restart_color, restart_button_rect, border_radius=10)
        pygame.draw.rect(scaled_screen, (255, 255, 255), restart_button_rect, 2, border_radius=10)
        pygame.draw.rect(scaled_screen, main_menu_color, main_menu_button_rect, border_radius=10)
        pygame.draw.rect(scaled_screen, (255, 255, 255), main_menu_button_rect, 2, border_radius=10)
        
        restart_text = font_medium.render("Restart", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
        scaled_screen.blit(restart_text, restart_text_rect)
        
        main_menu_text = font_medium.render("Main Menu", True, (255, 255, 255))
        main_menu_text_rect = main_menu_text.get_rect(center=main_menu_button_rect.center)
        scaled_screen.blit(main_menu_text, main_menu_text_rect)
        
        if restart_button_rect.collidepoint(scaled_mouse_pos) and mouse_clicked:
            game_state = GAME
            load_game_resources()
        elif main_menu_button_rect.collidepoint(scaled_mouse_pos) and mouse_clicked:
            game_state = MENU

        screen_width, screen_height = screen.get_size()
        scale_x = screen_width / base_screen_x
        scale_y = screen_height / base_screen_y
        scale = min(scale_x, scale_y)
        
        new_width = int(base_screen_x * scale)
        new_height = int(base_screen_y * scale)
        
        pos_x = (screen_width - new_width) // 2
        pos_y = (screen_height - new_height) // 2
        
        scaled_display = pygame.transform.scale(scaled_screen, (new_width, new_height))
        screen.blit(scaled_display, (pos_x, pos_y))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()