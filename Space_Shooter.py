#!/usr/bin/env python 
'''
    File name: Space_Shooter.py
    Author: Joshua Willman
    Date created: 2018.10.28
    Date last modified: 2018.12.02
    Python version: 3.4

    For a tutorial about writing your own space shooter or to understand how the 
    game was created, please check out:
    https://www.redhulimachinelearning.com
'''

# import necessary packages
import pygame, sys, random
from pygame import *
from os import path
import math

img_dir = path.join(path.dirname(__file__), 'images')
sound_dir = path.join(path.dirname(__file__), 'sounds')

WINDOWWIDTH = 480
WINDOWHEIGHT = 600
FPS = 30

# colors
BLACK = (0,0,0)
WHITE = (255,255,255)
GREENYELLOW = (143,245,34)
YELLOW = (234, 245, 34)
GREY = (210,210,210)
DARKGREY = (93,94,94)
RED = (255,0,0)
GREEN = (0,255,0)
REDORANGE = (245,103,32)

# initialize pygame and create window
pygame.init()
pygame.mixer.init() # initialize for sound
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('The Lonely Shooter')

FPSCLOCK = pygame.time.Clock() # For syncing the FPS

class Player(pygame.sprite.Sprite):
    '''create Player class'''
    def __init__(self, player_image, bullet_image, missile_image, sprites_list, bullet_list, bullet_sound, missile_sound):
        super().__init__()
        # scale player image 
        self.image = pygame.transform.scale(player_image, (70, 70))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        # sprites list
        self.sprites = sprites_list
        
        # player starting location
        self.rect.centerx = WINDOWWIDTH / 2
        self.rect.bottom = WINDOWHEIGHT - 10

        # player speed attributes
        self.speedx = 0
        self.speedy = 0

        # bullet attributes related to player
        self.bullet_image = bullet_image
        self.missile_image = missile_image
        self.bullets = bullet_list
        self.shoot_delay = 250 # milliseconds
        self.last_shot = pygame.time.get_ticks()
        self.missile_sound = missile_sound
        self.bullet_sound = bullet_sound

        # other player attributes
        self.shield = 100
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.upgrade = 1
        self.upgrade_timer = pygame.time.get_ticks()

    def update(self):
        '''update the player'''
        # unhide player
        if self.hidden and (pygame.time.get_ticks() - self.hide_timer > 1500):
            self.hidden = False
            self.rect.centerx = WINDOWWIDTH / 2
            self.rect.bottom = WINDOWHEIGHT - 10

        # timer for upgrades
        if self.upgrade >= 2 and pygame.time.get_ticks() - self.upgrade_timer > 4500:
            self.upgrade -= 1
            self.upgrade_timer = pygame.time.get_ticks()

        # make player static in screen by default 
        self.speedx = 0 
        self.speedy = 0 

        # then check if there is event handling for arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.speedx = -9
        if keys[pygame.K_RIGHT]:
            self.speedx = +9
        if keys[pygame.K_UP]:
            self.speedy = -9
        if keys[pygame.K_DOWN]:
            self.speedy = +9

        # fire weapons by holding the 'space' key
        if keys[pygame.K_SPACE] and not(self.rect.top > WINDOWHEIGHT):
            self.shoot()

        # boundary checking
        if self.rect.right > WINDOWWIDTH:
            self.rect.right = WINDOWWIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 200:
            self.rect.top = 200
        if self.rect.bottom > WINDOWHEIGHT - 10 and self.rect.bottom < WINDOWHEIGHT:
            self.rect.bottom = WINDOWHEIGHT - 10

        # Stop player from being able to move or shoot 
        # when at the bottom of the screen
        if self.rect.bottom > WINDOWHEIGHT + 10:
            self.rect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT + 100)

        # update movement
        self.rect.x += self.speedx
        self.rect.y += self.speedy

    def shoot(self):
        '''fire bullets'''
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            if self.upgrade == 1:
                bullet = Bullet(self.bullet_image, self.rect.centerx, self.rect.top)
                self.sprites.add(bullet)
                self.bullets.add(bullet)
                self.bullet_sound.play()
            if self.upgrade == 2:
                bullet = Bullet(self.bullet_image, self.rect.centerx, self.rect.top)
                self.sprites.add(bullet)
                self.bullets.add(bullet)
                missile1 = Missile(self.missile_image, self.rect.left, self.rect.centery)
                self.sprites.add(missile1)
                self.bullets.add(missile1)
                self.bullet_sound.play()
                self.missile_sound.play()
            if self.upgrade == 3:
                bullet = Bullet(self.bullet_image, self.rect.centerx, self.rect.top)
                self.sprites.add(bullet)
                self.bullets.add(bullet)
                missile1 = Missile(self.missile_image, self.rect.left, self.rect.centery)
                self.sprites.add(missile1)
                self.bullets.add(missile1)
                missile2 = Missile(self.missile_image, self.rect.right, self.rect.centery)
                self.sprites.add(missile2)
                self.bullets.add(missile2)
                self.bullet_sound.play()
                self.missile_sound.play()

    def upgrade_power(self):
        if self.upgrade >= 3:
            self.upgrade = 3
        elif self.upgrade < 3:
            self.upgrade += 1
        #print("upgrade:", self.upgrade)
        self.upgrade_timer = pygame.time.get_ticks()

    def hide(self):
        '''make player disappear from view'''
        self.hidden = True
        self.rect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT + 100) # hide player below the screen
        self.hide_timer = pygame.time.get_ticks()
        

class EnemyShip(pygame.sprite.Sprite):
    '''create EnemyShip class'''
    def __init__(self, enemy_image, bullet_image, sprites_list, bullet_list, bullet_sound, boost_anim):
        super().__init__()
        # scale enemy image 
        self.image = pygame.transform.scale(enemy_image, (60, 60))
        self.rect = self.image.get_rect()

        # sprites list
        self.sprites = sprites_list
        self.boost_anim = boost_anim

        # enemy starting location
        self.rect.centerx = random.randrange(90, WINDOWWIDTH - 90)
        self.rect.bottom = random.randrange(-150, -20)

        # bullet attributes for enemy
        self.bullet_image = bullet_image
        self.bullet_sound = bullet_sound
        self.bullets = bullet_list
        self.shoot_delay = 500
        self.last_shot = pygame.time.get_ticks()
        self.num_of_shots = 2

        # enemy kamikaze boost speed
        self.speedy = 30

    def update(self):
        '''update enemy movement'''
        if self.rect.bottom > 50 and self.rect.bottom < 130:
            for i in range(self.num_of_shots):
                    self.shoot()

        if self.rect.bottom <= 120:
            self.rect.bottom += 4
        if self.rect.bottom > 120 and self.rect.bottom < 140:
            self.rect.bottom += 1
        if self.rect.bottom >= 140:
            self.divebomb()

        # if ships go off the screen, respawn them
        if (self.rect.top > WINDOWHEIGHT):
            self.rect.centerx = random.randrange(50, WINDOWWIDTH - 50)
            self.rect.y = random.randrange(-200, -50)

    def shoot(self):
        '''fire lasers'''
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_delay:
            self.last_shot = current_time
            bullet = EnemyBullet(self.bullet_image, self.rect.centerx, self.rect.bottom)
            self.sprites.add(bullet)
            self.bullets.add(bullet)
            self.bullet_sound.play()
            self.bullet_sound.set_volume(0.2)

    def divebomb(self):
        '''divebomb flight pattern'''
        boost = Boost(self.rect.center, 'boost', self.boost_anim)
        self.sprites.add(boost)
        self.rect.bottom += self.speedy


class Boost(pygame.sprite.Sprite):
    '''create Boost class'''
    def __init__(self, center, b_type, boost_anim):
        super().__init__()
        self.b_type = b_type
        self.boost_anim = boost_anim
        self.image = boost_anim[self.b_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 35

    def update(self):
        '''update boost animation'''
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.last_update = current_time
            self.frame += 1
            if self.frame == len(self.boost_anim[self.b_type]):
                self.kill()
            else:
                center = self.rect.center 
                self.image = self.boost_anim[self.b_type][self.frame]
                self.rect = self.image.get_rect()
                self.rect.midtop = center
        

class Bullet(pygame.sprite.Sprite):
    '''create Bullet class'''
    def __init__(self, bullet_image, x, y):
        super().__init__()
        # scale bullet size
        self.image = pygame.transform.scale(bullet_image, (8, 23))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # bullet position is according the player position
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -15

    def update(self):
        '''update bullet'''
        self.rect.y += self.speedy

        # if bullet goes off top of window, destroy it
        if self.rect.bottom < 35:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    '''create Enemy Bullet class'''
    def __init__(self, bullet_image, x, y):
        super().__init__()
        # scale bullet size
        self.image = pygame.transform.scale(bullet_image, (8, 23))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # bullet position is according the player position
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = 15

    def update(self):
        '''update bullet'''
        self.rect.y += self.speedy

        # if bullet goes off bottom of window, destroy it
        if self.rect.bottom > WINDOWHEIGHT:
            self.kill()


class Missile(pygame.sprite.Sprite):
    '''create Missile class'''
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.image = pygame.transform.scale(image, (25, 38))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        '''update missiles'''
        self.rect.y += self.speedy
        if self.rect.bottom < 35:
            self.kill()


class Asteroid(pygame.sprite.Sprite):
    '''create Asteroid class'''
    def __init__(self, asteroid_img, all_sprites, asteroid_sprites):
        super().__init__()
        self.image_orig = random.choice(asteroid_img)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .90 / 2)

        # set spawn position
        self.rect.x = random.randrange(-25, WINDOWWIDTH + 25)
        self.rect.y = random.randrange(-200, -100)

        # set asteroid speed x and y values
        self.speedy = random.randrange(5, 12)
        self.speedx = random.randrange(-2, 2)

        # add rotation elements to the asteroids to make them look more realistic
        self.angle = 0 # the amount of rotation
        self.rotation_speed = random.randrange(-7, 7)
        self.last_update = pygame.time.get_ticks() # time for rotating asteroid

    def update(self):
        '''update asteroids'''
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # if asteroids go off the screen, respawn asteroids
        if (self.rect.top > WINDOWHEIGHT + 10) or (self.rect.left < -self.rect.width) or (self.rect.right > WINDOWWIDTH + self.rect.width):
            self.rect.x = random.randrange(0, WINDOWWIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -20)
            self.speedy =  random.randrange(3, 10)

    def rotate(self):
        '''handle rotation of asteroids'''
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > 50:
            self.last_update = current_time # reset current time
            self.angle = (self.angle + self.rotation_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.angle) 
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Explosion(pygame.sprite.Sprite):
    '''create Explosion class'''
    def __init__(self, center, ex_type, explosion_anim):
        super().__init__()
        self.ex_type = ex_type
        self.explosion_anim = explosion_anim
        self.image = explosion_anim[self.ex_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 100

    def update(self):
        '''update explosions'''
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_rate:
            self.last_update = current_time
            self.frame +=1
            if self.frame == len(self.explosion_anim[self.ex_type]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.explosion_anim[self.ex_type][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class PowerUp(pygame.sprite.Sprite):
    '''create PowerUp class'''
    def __init__(self, center, powerup_images):
        super().__init__()
        self.type = random.choice(['shield', 'missile'])
        self.image = powerup_images[self.type]
        self.rect = self.image.get_rect()
        # spawn the powerup according to current position of enemy
        self.rect.center = center
        self.speedy = 6

    def update(self):
        '''power up movement'''
        self.rect.y += self.speedy
        # destroy sprite if we do not collect it and it moves past WINDOWHEIGHT
        if self.rect.top > WINDOWHEIGHT + 10:
            self.kill()


class Shield(pygame.sprite.Sprite):
    '''create Shield class'''
    def __init__(self, image, center, player):
        super().__init__()
        self.image = pygame.transform.scale(image, (85, 85))
        self.center = center
        self.rect = self.image.get_rect(center=(self.center))
        self.player = player
    
    def update(self):
        '''update shield location'''
        self.rect.centerx = self.player.rect.centerx
        self.rect.centery = self.player.rect.centery

        if self.player.shield <= 30:
            self.rect.center = (WINDOWWIDTH/2, WINDOWHEIGHT + 115)
        elif self.player.shield > 30:
            self.rect.centerx = self.player.rect.centerx
            self.rect.centery = self.player.rect.centery
        

def draw_text(surface, text, size, x, y, color):
    '''draw text to screen'''
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def menu():
    '''display main menu'''
    pygame.mixer.music.load(path.join(sound_dir, 'SpaceShooter_Theme.wav'))
    pygame.mixer.music.play(-1)
    
    title = pygame.image.load(path.join(img_dir, "The_Lonely_Shooter.png")).convert_alpha()
    title = pygame.transform.scale(title, (WINDOWWIDTH, 81 * 2))
    background = pygame.image.load('images/stars_bg.jpeg').convert()
    background_rect = background.get_rect()

    # display instructions for game
    arrow_keys = pygame.image.load(path.join(img_dir, 'arrowkeys.png')).convert_alpha()
    arrow_keys = pygame.transform.scale(arrow_keys, (150, 85))
    spacebar = pygame.image.load(path.join(img_dir, 'spacebar.png')).convert_alpha()
    spacebar = pygame.transform.scale(spacebar, (150, 50))

    DISPLAYSURF.blit(background, background_rect)
    DISPLAYSURF.blit(title, (0,20))
    DISPLAYSURF.blit(arrow_keys, (225, 400))
    DISPLAYSURF.blit(spacebar, (225, 500))
    pygame.draw.rect(DISPLAYSURF, GREENYELLOW, (80, 294, 321, 35))
    pygame.draw.rect(DISPLAYSURF, GREENYELLOW, (120, 345, 240, 35))
    draw_text(DISPLAYSURF, "PRESS [ENTER] TO BEGIN", 35, WINDOWWIDTH/2, WINDOWHEIGHT/2, DARKGREY)
    draw_text(DISPLAYSURF, "PRESS [Q] TO QUIT", 35, WINDOWWIDTH/2, (WINDOWHEIGHT/2) + 50, DARKGREY)

    # game instructions
    pygame.draw.rect(DISPLAYSURF, GREENYELLOW, (50, 430, 100, 35))
    pygame.draw.rect(DISPLAYSURF, GREENYELLOW, (50, 510, 100, 35))
    draw_text(DISPLAYSURF, "MOVE:", 35, 100, 436, DARKGREY)
    draw_text(DISPLAYSURF, "SHOOT:", 35, 101, 516, DARKGREY)

    pygame.display.update()

    while True:
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                break
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()    

def draw_lives(surface, x, y, lives, image):
    '''display ship's lives on the screen'''
    for i in range(lives):
        img_rect = image.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surface.blit(image, img_rect)

def shield_bar(surface, player_shield):
    '''display the graphic and track shield for the player'''
    if player_shield > 100:
        player_shield_color = GREEN
        player_shield = 100
    elif player_shield > 75:
        player_shield_color = GREEN
    elif player_shield > 50:
        player_shield_color = YELLOW
    else:
        player_shield_color= RED

    pygame.draw.rect(surface, GREY, (5, 5, 104, 24), 3)
    pygame.draw.rect(surface, player_shield_color, (7, 7, player_shield, 20))

def main(): 
    '''main loop'''
    #### load all game images ####
    # draw background rectangle first
    background = pygame.image.load('images/stars_bg.jpeg').convert()
    background_rect = background.get_rect()
    planet = pygame.image.load('images/planet.png').convert()
    planet = pygame.transform.scale(planet, (400, 400))
    planet.set_colorkey(BLACK)
    planet_rect = planet.get_rect(center=(70,70))

    black_bar = pygame.Surface((WINDOWWIDTH, 35))
    
    # load player and bullet images
    player_img = pygame.image.load('images/spaceship.png').convert()
    life_player_image = pygame.transform.scale(player_img, (25, 25))
    life_player_image.set_colorkey(BLACK)
    bullet_img = pygame.image.load('images/laser_red.png').convert()
    enemy_bullet_img = pygame.image.load('images/laser_purple.png').convert()
    missile_img = pygame.image.load('images/missile.png').convert_alpha()
    energy_shield = pygame.image.load('images/energy_shield.png').convert_alpha()

    # load enemy images
    enemy_img = pygame.image.load('images/spacecraft_enemy.png').convert_alpha()

    # load asteroid images and put asteroid names in a list
    asteroid_images = []
    asteroid_list = [
        'asteroid_medium2.png',
        'asteroid_medium1.png',
        'asteroid_medium3.png',
        'asteroid_big1.png',
        'asteroid_tiny.png'   
    ]

    for image in asteroid_list:
        asteroid_images.append(pygame.image.load(path.join(img_dir, image)).convert_alpha())

    # asteroid explosion
    explosion_anim = {}
    explosion_anim['large'] = []
    explosion_anim['small'] = []
    explosion_anim['ship'] = []
    for i in range(5):
        filename = 'explosion0{}.png'.format(i)
        img = pygame.image.load(path.join(img_dir, filename)).convert_alpha()
        # change the sizes of the explosion
        image_lg = pygame.transform.scale(img, (75, 75))
        explosion_anim['large'].append(image_lg)
        image_sm = pygame.transform.scale(img, (45, 45))
        explosion_anim['small'].append(image_sm)
    
    for i in range(10):
        filename = 'ship_explosion0{}.png'.format(i)
        img = pygame.image.load(path.join(img_dir, filename)).convert()
        img.set_colorkey(BLACK)
        # change the sizes of the explosion
        image_player = pygame.transform.scale(img, (100, 100))
        explosion_anim['ship'].append(image_player)

    # boost animation
    boost_anim = {}
    boost_anim['boost'] = []
    for i in range(8):
        filename = 'boost0{}.png'.format(i)
        img = pygame.image.load(path.join(img_dir, filename)).convert_alpha()
        # change the sizes of the explosion
        boost_img = pygame.transform.scale(img, (50,50))
        boost_anim['boost'].append(boost_img)

    # load powerup images
    powerup_images = {}
    powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield.png')).convert_alpha()
    powerup_images['shield'] = pygame.transform.scale(powerup_images['shield'], (35, 35)) 
    powerup_images['missile'] = pygame.image.load(path.join(img_dir, 'missile_powerup.png')).convert_alpha()
    powerup_images['missile'] = pygame.transform.scale(powerup_images['missile'], (45, 45)) 

    # load game sounds
    bullet_sound = pygame.mixer.Sound(path.join(sound_dir, 'laser.wav'))
    bullet_sound.set_volume(0.25) # volume
    enemy_bullet_sound = pygame.mixer.Sound(path.join(sound_dir, 'enemy_laser.wav'))
    missile_sound = pygame.mixer.Sound(path.join(sound_dir, 'rocket.ogg'))
    missile_sound.set_volume(0.15)
    large_expl = pygame.mixer.Sound(path.join(sound_dir, 'large_explosion.wav'))
    small_expl = pygame.mixer.Sound(path.join(sound_dir, 'small_explosion.wav'))
    ship_expl = pygame.mixer.Sound(path.join(sound_dir, 'explosion_ship.wav'))
    ship_expl.set_volume(0.4)

    running = True
    show_menu = True
    while running: # main game loop
        if show_menu:
            menu()
            pygame.time.delay(1500)

            # fade out menu music
            pygame.mixer.music.fadeout(1500)

            pygame.mixer.music.load(path.join(sound_dir, 'SpaceShooter_Theme2.wav'))
            pygame.mixer.music.play(-1)

            show_menu = False

            # create group to store all sprites
            all_active_sprites = pygame.sprite.Group()
            # create group for bullets
            bullets = pygame.sprite.Group()
            # create group for enemy bullets
            enemy_bullets = pygame.sprite.Group()
            # create group for asteroids
            asteroids = pygame.sprite.Group()
            # create group for power ups
            powerups = pygame.sprite.Group()
            # create group for enemies
            enemy_ships = pygame.sprite.Group()

            player = Player(player_img, bullet_img, missile_img, all_active_sprites, 
                            bullets, bullet_sound, missile_sound)
            shield = Shield(energy_shield, player.rect.center, player)
            all_active_sprites.add(player, shield)

            for i in range(2):
                enemy_ship = EnemyShip(enemy_img, enemy_bullet_img, all_active_sprites, 
                                       enemy_bullets, enemy_bullet_sound, boost_anim)
                all_active_sprites.add(enemy_ship)
                enemy_ships.add(enemy_ship)
            
            for i in range(7):
                new_asteroid = Asteroid(asteroid_images, all_active_sprites, asteroids)
                all_active_sprites.add(new_asteroid)
                asteroids.add(new_asteroid)   
            
            # score variable
            score = 0

        # process inputs/events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
                sys.exit()

        # update all sprites
        all_active_sprites.update()

        #### Collision Checking ####
        # check if a bullet hit an asteroid
        asteroid_hit = pygame.sprite.groupcollide(asteroids, bullets, True, pygame.sprite.collide_circle)
        # when asteroids are destroyed, spawn new asteroids
        for hit in asteroid_hit:
            score += 50 - hit.radius # different scores for different size asteroids
            large_expl.play()
            large_expl.set_volume(0.1)
            expl = Explosion(hit.rect.center, 'large', explosion_anim)
            all_active_sprites.add(expl)
            if random.random() > 0.92:
                powerup = PowerUp(hit.rect.center, powerup_images)
                all_active_sprites.add(powerup)
                powerups.add(powerup)
            new_asteroid = Asteroid(asteroid_images, all_active_sprites, asteroids)
            all_active_sprites.add(new_asteroid)
            asteroids.add(new_asteroid)

        # check if a bullet hit an enemy ship
        enemy_hit = pygame.sprite.groupcollide(enemy_ships, bullets, True, pygame.sprite.collide_circle)
        # when asteroids are destroyed, spawn new asteroids
        for hit in enemy_hit:
            score += 75
            ship_expl.play()
            ship_expl.set_volume(0.1)
            expl = Explosion(hit.rect.center, 'ship', explosion_anim)
            all_active_sprites.add(expl)
            if random.random() > 0.85:
                powerup = PowerUp(hit.rect.center, powerup_images)
                all_active_sprites.add(powerup)
                powerups.add(powerup)
            new_ship = EnemyShip(enemy_img, enemy_bullet_img, all_active_sprites, enemy_bullets, 
                                 enemy_bullet_sound, boost_anim)
            all_active_sprites.add(new_ship)
            enemy_ships.add(new_ship)
            
        # check if enemy bullet hit player
        player_hit_by_bullet = pygame.sprite.spritecollide(player, enemy_bullets, True)

        # if player is hit
        for hit in player_hit_by_bullet:
            #print("Player hit")
            player.shield -= 5
            if player.shield <= 0:
                ship_expl.play()
                expl_ship = Explosion(player.rect.center, 'ship', explosion_anim)
                all_active_sprites.add(expl_ship)
                player.hide()
                player.lives -= 1
                player.shield = 100

        # check for collisions between asteroids and player
        player_hit = pygame.sprite.spritecollide(player, asteroids, True)

        # if player is hit
        for hit in player_hit:
            player.shield -= random.randint(10, 25)
            #print(player.shield)
            small_expl.play()
            small_expl.set_volume(0.1)
            expl = Explosion(hit.rect.center, 'small', explosion_anim)
            all_active_sprites.add(expl)
            new_asteroid = Asteroid(asteroid_images, all_active_sprites, asteroids)
            all_active_sprites.add(new_asteroid)
            asteroids.add(new_asteroid)
            if player.shield <= 0:
                ship_expl.play()
                expl_ship = Explosion(player.rect.center, 'ship', explosion_anim)
                all_active_sprites.add(expl_ship)
                player.hide()
                player.lives -= 1
                player.shield = 100

        # check for collisions between enemy ships and player
        player_hit_by_ship = pygame.sprite.spritecollide(player, enemy_ships, True)

        # if player is hit by enemy ship
        for hit in player_hit_by_ship:
            player.shield -= 35
            ship_expl.play()
            ship_expl.set_volume(0.1)
            expl = Explosion(hit.rect.center, 'ship', explosion_anim)
            all_active_sprites.add(expl)
            new_ship = EnemyShip(enemy_img, enemy_bullet_img, all_active_sprites, enemy_bullets, 
                                 enemy_bullet_sound, boost_anim)
            all_active_sprites.add(new_ship)
            enemy_ships.add(new_ship)
            if player.shield <= 0:
                ship_expl.play()
                expl_ship = Explosion(player.rect.center, 'ship', explosion_anim)
                all_active_sprites.add(expl_ship)
                player.hide()
                player.lives -= 1
                player.shield = 100
        
        # check for collisions between player and power ups
        powerup_hit = pygame.sprite.spritecollide(player, powerups, True)
        
        # check if player hits power up
        for hit in powerup_hit:
            if hit.type == 'shield':
                score += 100
                player.shield += 20
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'missile':
                score += 50
                player.upgrade_power()
        
        # If player dies, return to menu
        if player.lives == 0 and not expl_ship.alive():
            #print("in loop")
            #running = False
            pygame.mixer.music.stop()
            show_menu = True
            
        # draw/render 
        DISPLAYSURF.fill(BLACK)
        # draw background image to game
        DISPLAYSURF.blit(background, background_rect)
        DISPLAYSURF.blit(planet, planet_rect)

        all_active_sprites.draw(DISPLAYSURF)
        DISPLAYSURF.blit(black_bar, (0,0))
        pygame.draw.rect(DISPLAYSURF, GREY, (0, 0, WINDOWWIDTH, 35), 3)
        shield_bar(DISPLAYSURF, player.shield)

        # display score
        draw_text(DISPLAYSURF, "SCORE", 12, WINDOWWIDTH / 2, 2, WHITE)
        draw_text(DISPLAYSURF, str(score), 25, WINDOWWIDTH / 2, 12, WHITE)

        # display lives
        draw_lives(DISPLAYSURF, WINDOWWIDTH - 100, 5, player.lives, life_player_image)

        # done after drawing everything to the screen
        FPSCLOCK.tick(FPS) # number of FPS per loop
        pygame.display.flip()

if __name__ == "__main__":
    main()