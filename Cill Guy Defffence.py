import pygame
import random
import time 

screen_x = 1000
screen_y = 800
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Chill Guy Deffence")
clock = pygame.time.Clock()
running = True

enemy_die_sound = pygame.mixer.Sound("enemy_die.mp3")
tower_hit = pygame.mixer.Sound("hit_tower.mp3")
tower_hit.set_volume(0.5)
ult_sound = pygame.mixer.Sound("ultimate.mp3")
ult_sound.set_volume(0.3)
punch_sound = pygame.mixer.Sound("punch.mp3")
punch_sound.set_volume(0.3)
boss_punch_sound = pygame.mixer.Sound("boss_punch.mp3")
boss_punch_sound.set_volume(0.5)
boss_punch_timer = 0
steps_sound = pygame.mixer.Sound("steps.mp3")
steps_sound_timer = 300

background = pygame.image.load("background.png")
background = pygame.transform.scale(background,(screen_x,screen_y))
boom = pygame.image.load("boom.png")
boom = pygame.transform.scale(boom,(275,275))
boom_timer = 0
boss_boom_timer = 0
boss_animation_timer = 0


player_animation_timer = 0
animation_timer = 0

bosses = []
boss_spaun_timer = 0
boss_attack_cooldown = 0

enemies = []
enemy_buff_timer = 0
enemy_lvl_timer = 0
enemy_spawn_timer = 0

buffs = []
buff_spawn_timer = 0
        
class Tower:
    def __init__(self):
        self.tower_image = pygame.image.load("tower.png")  
        self.tower_image = pygame.transform.scale(self.tower_image, (275, 275)) 
        self.tower_x = 365
        self.tower_y = 225
        self.tower_health = 50
        self.health_bar_length = 275
        self.health_bar_height = 10
        self.tower_max_health = self.tower_health
        self.tower_rect = pygame.Rect(self.tower_x, self.tower_y, 200, 200)
    def draw_health_bar(self, surface):
        health_ratio = self.tower_health / self.tower_max_health
        health_width = int(self.health_bar_length * health_ratio)
        health_bar_pos = (self.tower_x, self.tower_y  + 260)
        first_color = 0
        second_color = 255
        third_color = 0
        if self.tower_health <= self.tower_max_health / 3:
            first_color = 255
            second_color = 0
            third_color = 0
        elif self.tower_health <= self.tower_max_health / 1.5:
            first_color = 254
            second_color =138
            third_color = 24
        pygame.draw.rect(surface, (100, 100, 100), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height))
        pygame.draw.rect(surface, (first_color, second_color, third_color), 
                        (*health_bar_pos, health_width, self.health_bar_height))
        pygame.draw.rect(surface, (255, 255, 255), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height), 1)
    def draw(self):
        screen.blit(self.tower_image, (self.tower_x, self.tower_y))
        self.draw_health_bar(screen)
        
class Boss:
    def __init__(self):
        self.boss_r = pygame.image.load("boss_r.png").convert_alpha()
        self.boss_l = pygame.image.load("boss_l.png").convert_alpha()
        self.side = random.randint(0,3)
        self.boss_x = 0
        self.boss_y = 0
        self.is_buffed = False
        if self.side == 0:
            self.boss_x = 0
            self.boss_y = tower.tower_y
        elif self.side == 1:
            self.boss_x = tower.tower_x
            self.boss_y = 0
        elif self.side == 2:
            self.boss_x = screen_x - 225
            self.boss_y = tower.tower_y
        else: 
            self.boss_x = tower.tower_x
            self.boss_y = screen_y - 200

        if self.side == 0:
            self.boss_y = random.randint(0,screen_y - 225)
            self.boss_x -= 225
        elif self.side == 1: 
            self.boss_y -= 200
            self.boss_x = random.randint(0,screen_x - 225)
        elif self.side == 2:
             self.boss_y = random.randint(0,screen_y - 200)
             self.boss_x = screen_x
        else :
             self.boss_y = screen_y
             self.boss_x = random.randint(0,screen_x - 225)
        self.boss_health = 2000
        self.boss_max_health = self.boss_health
        self.boss_speed = 1
        self.length = 225
        self.height = 200
        self.health_bar_length = 250  
        self.health_bar_height = 15 
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
            second_color =138
            third_color = 24
        health_ratio = self.boss_health / self.boss_max_health
        health_width = int(self.health_bar_length * health_ratio)
        health_bar_pos = (self.boss_x, self.boss_y + 205)
        pygame.draw.rect(surface, (100, 100, 100), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height))
        pygame.draw.rect(surface, (first_color,second_color, third_color), 
                        (*health_bar_pos, health_width, self.health_bar_height))
        pygame.draw.rect(surface, (255, 255, 255), 
                        (*health_bar_pos, self.health_bar_length, self.health_bar_height), 1)
    def boss_animation(self):
        if self.dx > 0:
            boss_animation = pygame.transform.scale(self.boss_r,(self.length,self.height))
            screen.blit(boss_animation, (self.boss_x, self.boss_y))
            self.draw_health_bar(screen)
        else:
            boss_animation = pygame.transform.scale(self.boss_l,(self.length,self.height))
            screen.blit(boss_animation, (self.boss_x, self.boss_y))
            self.draw_health_bar(screen)

    def take_damage(self):
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
    def boss_die(self):
        bosses.remove(boss)
    def check_hit(self):
        boss_rect = pygame.Rect(self.boss_x, self.boss_y, 275, 150)
        return boss_rect.colliderect(pygame.Rect(405, 265, 200, 200))


class Enemies:
    def __init__(self):
        enemy_images = [
            "crok.png",
            "sahur.png",
            "shark.png",
        ]
        self.image_path = random.choice(enemy_images)
        if "crok" in self.image_path:
            self.enemy_image_r = pygame.image.load("crok_r.png")  
            self.enemy_image_r = pygame.transform.scale(self.enemy_image_r, (50, 50))
            self.enemy_image_l = pygame.image.load("crok_l.png")  
            self.enemy_image_l = pygame.transform.scale(self.enemy_image_l, (50, 50))
            self.speed = 5
            self.health = 20
            self.max_health = self.health
            self.final_health = 80
            self.is_buffed = False
        elif "sahur" in self.image_path:
            self.enemy_image_r = pygame.image.load("sahur_r.png")  
            self.enemy_image_r = pygame.transform.scale(self.enemy_image_r, (50, 50))
            self.enemy_image_l = pygame.image.load("sahur_l.png")  
            self.enemy_image_l = pygame.transform.scale(self.enemy_image_l, (50, 50))
            self.speed = 3
            self.health = 10
            self.max_health = self.health
            self.final_health = 40
            self.is_buffed = False
        else:
            self.enemy_image_r = pygame.image.load("shark_r.png")  
            self.enemy_image_r = pygame.transform.scale(self.enemy_image_r, (50, 50))
            self.enemy_image_l = pygame.image.load("shark_l.png")  
            self.enemy_image_l = pygame.transform.scale(self.enemy_image_l, (50, 50))
            self.speed = 4
            self.health = 30
            self.max_health = self.health
            self.final_health = 120
            self.is_buffed = False
        self.side = random.randint(0,3)
        self.enemy1_x = 0
        self.enemy1_y = 0
        self.health_bar_length = 50  
        self.health_bar_height = 5 
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
            second_color =138
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
    def draw(self):
        if self.dx >= 0:
            screen.blit(self.enemy_image_r,(self.enemy1_x, self.enemy1_y))
            self.draw_health_bar(screen)
        else:
            screen.blit(self.enemy_image_l,(self.enemy1_x, self.enemy1_y))
            self.draw_health_bar(screen)
    def animation(self):
        if self.dx >= 0:
            animation = pygame.transform.scale(self.enemy_image_r, (60,40))
            screen.blit(animation,(self.enemy1_x, self.enemy1_y))
            self.draw_health_bar(screen)
        else:
            animation = pygame.transform.scale(self.enemy_image_l, (60,40))
            screen.blit(animation,(self.enemy1_x, self.enemy1_y))
            self.draw_health_bar(screen)
    def take_damage(self):
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
      self.player_attack = 10
      self.player_knockback = 150 
      self.player_speed = 6
      self.player_score = 0
      self.player_turn_r = True
      self.is_still = True
      self.ultimate_cooldown = 20 
      self.ultimate_duration = 5 
      self.ultimate_radius = 200
      self.ultimate_active = False
      self.ultimate_start_time = 0
      self.last_ultimate_time = 0
      self.ultimate_ready = True
      self.is_plaing = False

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
        if keys[pygame.K_d] and self.player_x < screen_x - self.player_size:
            self.player_x += self.player_speed
        if keys[pygame.K_w] and self.player_y > 0:
            self.player_y -= self.player_speed
        if keys[pygame.K_s] and self.player_y < screen_y - self.player_size:
            self.player_y += self.player_speed
        if keys[pygame.K_SPACE] and self.ultimate_ready:
           self.activate_ultimate()

    def activate_ultimate(self):
        ult_sound.play()
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
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
           self.player_turn_r = True
           screen.blit(self.player_image_r, (self.player_x, self.player_y))
        elif keys[pygame.K_a]:
           self.player_turn_r = False
           screen.blit(self.player_image_l, (self.player_x, self.player_y))
        else:
            if self.player_turn_r:
                screen.blit(self.player_image_r, (self.player_x, self.player_y))
            elif not self.player_turn_r:
                screen.blit(self.player_image_l, (self.player_x, self.player_y))
        if self.ultimate_active:
           ultimate_surface = pygame.Surface((self.ultimate_radius*2, self.ultimate_radius*2), pygame.SRCALPHA)
           pygame.draw.circle(ultimate_surface, (255, 255, 0, 100), 
                             (self.ultimate_radius, self.ultimate_radius), self.ultimate_radius)
           screen.blit(ultimate_surface, (self.player_x - self.ultimate_radius + 50, 
                                        self.player_y - self.ultimate_radius + 50))
    
    def animation(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
           self.player_turn_r = True
           animation = pygame.transform.scale(self.player_image_r, (110,90))
           screen.blit(animation, (self.player_x, self.player_y))
        elif keys[pygame.K_a]:
           self.player_turn_r = False
           animation = pygame.transform.scale(self.player_image_l, (110,90))
           screen.blit(animation, (self.player_x, self.player_y))
        else:
            if self.player_turn_r:
                screen.blit(self.player_image_r, (self.player_x, self.player_y))
            elif not self.player_turn_r:
                screen.blit(self.player_image_l, (self.player_x, self.player_y))

    def draw_stand(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
           screen.blit(self.player_stand_r, (self.player_x, self.player_y - 90))
        elif keys[pygame.K_a]:
           screen.blit(self.player_stand_l, (self.player_x, self.player_y - 90))
        else:
            screen.blit(self.player_stand_l, (self.player_x, self.player_y - 90))

    def punch(self):
        enemy_rect = pygame.Rect(enemy.enemy1_x, enemy.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(self.player_x,self.player_y,100,100)) and enemy.health > 0
    def punch_boss(self):
        boss_rect = pygame.Rect(boss.boss_x, boss.boss_y, 250, 150)
        return boss_rect.colliderect(pygame.Rect(self.player_x,self.player_y,100,100)) and boss.boss_health > 0
    def kill_boss(self):
        boss_rect = pygame.Rect(boss.boss_x, boss.boss_y, 250, 150)
        return boss_rect.colliderect(pygame.Rect(self.player_x,self.player_y,100,100)) and boss.boss_health <= 0
    def kill(self):
        enemy_rect = pygame.Rect(enemy.enemy1_x, enemy.enemy1_y, 50, 50)
        return enemy_rect.colliderect(pygame.Rect(self.player_x,self.player_y,100,100)) and enemy.health <= 0
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

while running:
    current_time = time.time()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if tower.tower_health <= 0:
        running = False
    screen.fill((0, 0, 0))
    player.move()

    steps_sound_timer += 1
    if player.is_moving() and  steps_sound_timer >= 300:
        steps_sound.play()  
        steps_sound_timer = 0 
    if not(player.is_moving()):
        steps_sound.stop()

    screen.blit(background, (0, 0))
    tower.draw()

    player_animation_timer +=1
    if player_animation_timer <= 8:
        player.draw()
    else:
        player.animation()

    if player_animation_timer >= 16:
        player_animation_timer = 0

    enemy_spawn_timer += 1
    if enemy_spawn_timer >= 90:
        enemies.append(Enemies())
        enemy_spawn_timer = 0 

    enemy_buff_timer += 1  
    animation_timer += 1 
    for enemy in enemies[:]:

        enemy.move()
        if animation_timer <= 10:
            enemy.draw()
        else:
            enemy.animation()

        if animation_timer >= 20:
            animation_timer = 0

        if enemy.health == 0:
            enemy_die_sound.play()
            player.player_score += 1
            enemies.remove(enemy)


        if enemy_buff_timer >= 1800 and enemy_lvl_timer == 1 and (not enemy.is_buffed):
            enemy.health += enemy.health
            enemy.is_buffed = True
            enemy.max_health = enemy.health
            enemy.speed += 1
        if enemy_buff_timer >= 3600 and enemy_lvl_timer == 2 and (not enemy.is_buffed):
            enemy.health += enemy.health * 2
            enemy.is_buffed = True
            enemy.max_health = enemy.health
            enemy.speed += 1
        if enemy_buff_timer >= 5400 and enemy_lvl_timer == 3 and (not enemy.is_buffed):
            enemy.health += enemy.health * 3
            enemy.is_buffed = True
            enemy.max_health = enemy.health
            enemy.speed += 1

        if enemy_buff_timer == 1800 and enemy_lvl_timer == 0:
            enemy_lvl_timer += 1
        if enemy_buff_timer == 3600 and  enemy_lvl_timer == 1:
            enemy_lvl_timer += 1
        if enemy_buff_timer == 5400 and enemy_lvl_timer == 2:
            enemy_lvl_timer += 1    

        if player.ultimate_active and player.ultimate_kill(enemy):
            enemy_die_sound.play()
            player.player_score += 1
            enemies.remove(enemy)
            continue

        if player.punch():
            enemy.take_damage()
            punch_sound.play()
        elif player.kill() and enemy.check_hit():
            tower.tower_health -= 1
            tower_hit.play()
            enemies.remove(enemy)
        elif player.kill():
            enemy_die_sound.play()
            player.player_score += 1
            enemies.remove(enemy)
        elif enemy.check_hit():
            tower.tower_health -= 1
            tower_hit.play()
            boom_timer = 180
            enemies.remove(enemy)

        if boom_timer >= 60:
            screen.blit(boom, (365, 225))
            boom_timer -= 4

    boss_spaun_timer +=1
    boss_attack_cooldown += 1
    boss_animation_timer +=1
    if boss_spaun_timer == 1800:
        boss_spaun_timer = 0
        bosses.append(Boss())
    boss_punch_timer += 1
    for boss in bosses[:]:
        boss.move()
        if boss_animation_timer <= 10:
            boss.length = 225
            boss.height = 200
            boss.boss_animation()
        elif boss_animation_timer <= 20:
            boss.length = 250
            boss.height = 180
            boss.boss_animation()
        elif boss_animation_timer <= 30:
            boss.length = 275
            boss.height = 160
            boss.boss_animation()
        elif boss_animation_timer <= 40:
            boss.length = 275
            boss.height = 160
            boss.boss_animation()
        elif boss_animation_timer <= 50:
            boss.length = 250
            boss.height = 180
            boss.boss_animation()
        else:
            boss.length = 225
            boss.height = 200
            boss.boss_animation()
        if enemy_lvl_timer == 2 and not(boss.is_buffed):
            boss.boss_health *= 2
            boss.boss_max_health = boss.boss_health
            boss.is_buffed = True
        if enemy_lvl_timer == 3 and not(boss.is_buffed):
            boss.boss_health *= 3
            boss.boss_max_health = boss.boss_health
            boss.is_buffed = True

        if boss_animation_timer >= 60:
            boss_animation_timer = 0
        
        if boss.check_hit():
            boss.boss_speed = 0
            if boss_boom_timer > 0:
                screen.blit(boom , (365, 225))
                boss_boom_timer -= 1

        if boss_attack_cooldown >= 180 and boss.check_hit():
            boss_attack_cooldown = 0
            boss_boom_timer = 60
            tower_hit.play()
            tower.tower_health -= 2

        if player.punch_boss():
            player.draw_stand()
            if boss_punch_timer >= 180:
                boss_punch_sound.play()
                boss_punch_timer = 0
            boss.take_damage()
            boss.boss_speed = 1
        elif player.kill_boss():
            player.player_score += 10
            boss_punch_sound.stop()
            bosses.remove(boss)

    player.update_ultimate()
    
    font = pygame.font.SysFont(None, 36)
    health_text = font.render(f"Health: {tower.tower_health}", True, (255, 0, 0))
    screen.blit(health_text, (10, 10))

    score_text = font.render(f"Score: {player.player_score}", True, (0, 0, 255))
    screen.blit(score_text, (880, 10))

    Lvl_text = font.render(f"Level: {enemy_lvl_timer}" , True ,(219, 172, 52))
    screen.blit(Lvl_text, (screen_x // 2 - Lvl_text.get_width() // 2, screen_y - Lvl_text.get_height()*1.5))
    
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