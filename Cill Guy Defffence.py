import pygame
import random
import time

screen_x = 1000
screen_y = 800
pygame.init()
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Chill Guy Deffence")
clock = pygame.time.Clock()
running = True

background = pygame.image.load("background.png")
boom = pygame.image.load("boom.png")
boom = pygame.transform.scale(boom,(200,200))
boom_timer = 0

enemies = []
enemy_spawn_timer = 0
buffs = []
buff_spawn_timer = 0

class Buff:
    def  __init__(self):
        self.type = random.choice(["heal", "speed", "power"])
        self.x = random.randint(50, screen_x - 50)
        self.y = random.randint(50, screen_y - 50)
        self.radius = 20
        self.duration = 10
        self.active = False
        self.start_time = 0
        self.collected = False

        if self.type == "speed":
            self.color = (0, 255, 255)
            self.image = pygame.Surface((40,40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (20, 20), 20)
            pygame.draw.polygon(self.image, (0, 0, 0), [(20, 5), (35, 20), (20, 35), (5, 20)])
        elif self.type == "power":
            self.color = (255, 0, 0)
            self.image = pygame.Surface((40,40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (20, 20), 20)
            pygame.draw.rect(self.image, (0, 0, 0), (15, 10, 10, 20))
        else:
            self.color = (0, 255, 0)
            self.image = pygame.Surface((40,40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (20, 20), 20)
            pygame.draw.rect(self.image, (0, 0, 0), (10, 18, 20, 4))
            pygame.draw.rect(self.image, (0, 0, 0), (18, 10, 4, 20))
    #def draw(self):
        #if not selt.collected(


class Tower:
    def __init__(self):
        self.tower_image = pygame.image.load("tower.png")  
        self.tower_image = pygame.transform.scale(self.tower_image, (200, 200)) 
        self.tower_x = 400
        self.tower_y = 300
        self.tower_health = 50
        self.tower_rect = pygame.Rect(self.tower_x, self.tower_y, 200, 200)
    def draw(self):
        screen.blit(self.tower_image, (self.tower_x, self.tower_y))
        
class Boss:
    def __init__(self):
        self.boss = pygame.image.load("prigozin.png").convert_alpha()
        self.boss = pygame.transform.scale(self.boss,(250,150))
        self.boss_x = 360
        self.boss_y = 0
        self.boss_health = 5
        self.boss_speed = 0.5
    def apear(self):
         screen.blit(self.boss, (self.boss_x, self.boss_y))
    def move(self):
         self.boss_y += self.boss_speed 

class EnemyLvL1(Tower):
    def __init__(self):
        enemy_images = [
            "crok.png",
            "sahur.png",
            "shark.png",
        ]
        image_path = random.choice(enemy_images)
        if "crok" in image_path:
            self.speed = 6
        elif "sahur" in image_path:
            self.speed = 3
        else:
            self.speed = 4
        self.enemy1 = pygame.image.load(image_path).convert_alpha()
        self.enemy1 = pygame.transform.scale(self.enemy1,(50,50))
        self.enemy1_speed = 4
        self.side = random.randint(0,3)
        self.enemy1_x = 0
        self.enemy1_y = 0
        if self.side == 0:
            self.enemy1_y = random.randint(0,screen_y - 50)
            self.enemy1_x -= 50
        elif self.side == 1: 
            self.enemy1_y -= 50
            self.enemy1_x = random.randint(0,screen_x - 50)
        elif self.side == 2:
             self.enemy1_y = random.randint(0,screen_y - 50)
             self.enemy1_x = screen_x
        else :
             self.enemy1_y = screen_y
             self.enemy1_x = random.randint(0,screen_x - 50)
    def move(self):
        dx = 400 - self.enemy1_x
        dy = 300 - self.enemy1_y
        distance = max(1, (dx**2 + dy**2)**0.5)

        self.enemy1_x += (dx / distance) * self.enemy1_speed
        self.enemy1_y += (dy / distance) * self.enemy1_speed
    def draw(self):
        screen.blit(self.enemy1,(self.enemy1_x, self.enemy1_y))
    def check_hit(self):
        enemy_rect = pygame.Rect(self.enemy1_x, self.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(400, 300, 200, 200))
    
class Player(EnemyLvL1):
    def __init__(self):
        self.player_image = pygame.image.load("image.png")  
        self.player_image = pygame.transform.scale(self.player_image, (100, 100))
        self.player_size = 100
        self.player_x = 400
        self.player_y = 500
        self.player_speed = 6
        self.player_score = 0
        self.ultimate_cooldown = 20 
        self.ultimate_duration = 5 
        self.ultimate_radius = 200
        self.ultimate_active = False
        self.ultimate_start_time = 0
        self.last_ultimate_time = 0
        self.ultimate_ready = True
    
    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.player_x > 0:
            self.player_x -= self.player_speed
        if keys[pygame.K_RIGHT] and self.player_x < screen_x - self.player_size:
            self.player_x += self.player_speed
        if keys[pygame.K_UP] and self.player_y > 0:
            self.player_y -= self.player_speed
        if keys[pygame.K_DOWN] and self.player_y < screen_y - self.player_size:
            self.player_y += self.player_speed
        if keys[pygame.K_SPACE] and self.ultimate_ready:
            self.activate_ultimate()
    
    def activate_ultimate(self):
        current_time = time.time()
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
    
    def draw(self):
        screen.blit(self.player_image, (self.player_x, self.player_y))
        if self.ultimate_active:
            ultimate_surface = pygame.Surface((self.ultimate_radius*2, self.ultimate_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(ultimate_surface, (255, 255, 0, 100), 
                              (self.ultimate_radius, self.ultimate_radius), self.ultimate_radius)
            screen.blit(ultimate_surface, (self.player_x - self.ultimate_radius + 50, 
                                         self.player_y - self.ultimate_radius + 50))
    
    def kill(self):
        enemy_rect = pygame.Rect(enemy.enemy1_x, enemy.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(self.player_x, self.player_y, 100, 100))
    
    def ultimate_kill(self, enemy):
        if not self.ultimate_active:
            return False
        enemy_center_x = enemy.enemy1_x + 25
        enemy_center_y = enemy.enemy1_y + 25
        player_center_x = self.player_x + 50
        player_center_y = self.player_y + 50
        
        distance = ((enemy_center_x - player_center_x)**2 + (enemy_center_y - player_center_y)**2)**0.5
        return distance <= self.ultimate_radius

player = Player()
tower = Tower()
boss = Boss()

while running:
    current_time = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    player.move()
    player.update_ultimate()
    screen.blit(background, (0, 0))
    tower.draw()
    player.draw()

    enemy_spawn_timer += 2
    if enemy_spawn_timer >= 90:
        enemies.append(EnemyLvL1())
        enemy_spawn_timer = 0

    if player.player_score >= 5:
        boss.apear()
        boss.move()

    for enemy in enemies[:]:
        enemy.move()
        enemy.draw()
        
        if player.ultimate_active and player.ultimate_kill(enemy):
            player.player_score += 1
            enemies.remove(enemy)
            continue
            
        if player.kill() and enemy.check_hit():
            screen.blit(boom, (400, 300))
            tower.tower_health -= 1
            enemies.remove(enemy)
        elif player.kill():
            player.player_score += 1
            enemies.remove(enemy)
        elif enemy.check_hit():
            screen.blit(boom, (400, 300))
            tower.tower_health -= 1
            enemies.remove(enemy)

    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f"Health: {tower.tower_health}", True, (255, 0, 0))
    screen.blit(health_text, (10, 10))

    score_text = font.render(f"Score: {player.player_score}", True, (0, 0, 255))
    screen.blit(score_text, (880, 10))
    
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
    
    ultimate_text = font.render(ultimate_status, True, color)
    screen.blit(ultimate_text, (screen_x // 2 - ultimate_text.get_width() // 2, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()