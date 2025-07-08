import pygame
import random

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

bosses = []
boss_spaun_timer = 0

enemies = []
enemy_spawn_timer = 0
        

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
        self.side = random.randint(0,3)
        self.boss_health = 200
        self.boss_speed = 1
    def apear(self):
        screen.blit(self.boss, (self.boss_x, self.boss_y))
    def take_damage(self):
        self.boss_y -= 1.3
        self.boss_health -= player.player_attack
    def move(self):
        self.boss_y += self.boss_speed 
    def boss_die(self):
        bosses.remove(boss)

              



class Enemies(Tower):
    def __init__(self):
        enemy_images = [
            "crok.png",
            "sahur.png",
            "shark.png",
        ]
        image_path = random.choice(enemy_images)
        if "crok" in image_path:
            self.speed = 6
            self.health = 2
        elif "sahur" in image_path:
            self.speed = 3
            self.health = 1
        else:
            self.speed = 4
            self.health = 3
        self.enemy1 = pygame.image.load(image_path).convert_alpha()
        self.enemy1 = pygame.transform.scale(self.enemy1,(50,50))
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
        self.enemy1_x += (dx / distance) * self.speed
        self.enemy1_y += (dy / distance) * self.speed
    def draw(self):
        screen.blit(self.enemy1,(self.enemy1_x, self.enemy1_y))
    def take_damage(self):
        if self.side == 0:
            self.enemy1_x -= 100
            self.health -= player.player_attack
        elif self.side == 1:
            self.enemy1_y -= 100
            self.health -= player.player_attack
        elif self.side == 2:
            self.enemy1_x += 100
            self.health -= player.player_attack
        else:
            self.enemy1_y += 100
            self.health -= player.player_attack
    def check_hit(self):
        enemy_rect = pygame.Rect(self.enemy1_x, self.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(400, 300, 200, 200))
    
class Player(Enemies):
    def __init__(self):
      self.player_image = pygame.image.load("image.png")  
      self.player_image = pygame.transform.scale(self.player_image, (100, 100))
      self.player_size = 100
      self.player_x = 400
      self.player_y = 500
      self.player_attack = 1
      self.player_speed = 6
      self.player_score = 0
    def move(self):
         keys = pygame.key.get_pressed()
         if keys[pygame.K_a] and self.player_x > 0:
              self.player_x -= self.player_speed
         if keys[pygame.K_d] and self.player_x < screen_x - self.player_size:
              self.player_x += self.player_speed
         if keys[pygame.K_w] and self.player_y > 0:
              self.player_y -= self.player_speed
         if keys[pygame.K_s] and self.player_y < screen_y - self.player_size:
              self.player_y += self.player_speed
    def draw(self):
         screen.blit(self.player_image, (self.player_x, self.player_y))
    def punch(self):
        enemy_rect = pygame.Rect(enemy.enemy1_x, enemy.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(self.player_x,self.player_y,100,100)) and enemy.health != 0
    def punch_boss(self):
        boss_rect = pygame.Rect(boss.boss_x, boss.boss_y, 250, 150)
        return boss_rect.colliderect(pygame.Rect(self.player_x,self.player_y,100,100)) and boss.boss_health != 0
    def kill_boss(self):
        boss_rect = pygame.Rect(boss.boss_x, boss.boss_y, 250, 150)
        return boss_rect.colliderect(pygame.Rect(self.player_x,self.player_y,100,100)) and boss.boss_health == 0
    def kill(self):
        enemy_rect = pygame.Rect(enemy.enemy1_x, enemy.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(self.player_x,self.player_y,100,100)) and enemy.health == 0


player = Player()
tower = Tower()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    player.move()
    screen.blit(background, (0, 0))
    tower.draw()
    player.draw()

    enemy_spawn_timer += 1
    if enemy_spawn_timer >= 90:
        enemies.append(Enemies())
        enemy_spawn_timer = 0    
    for enemy in enemies[:]:

        enemy.move()
        enemy.draw()
        if player.punch():
            enemy.take_damage()
        elif player.kill() and enemy.check_hit():
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

    boss_spaun_timer +=1
    if boss_spaun_timer == 600:
        boss_spaun_timer = 0
        bosses.append(Boss())

    for boss in bosses[:]:
        boss.move()
        boss.apear()
        if player.punch_boss():
             boss.take_damage()
        elif player.kill_boss():
             bosses.remove(boss)


    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f"Health: {tower.tower_health}", True, (255, 0, 0))
    screen.blit(health_text, (10, 10))

    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f"Score: {player.player_score}", True, (0, 0, 255))
    screen.blit(health_text, (890, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()