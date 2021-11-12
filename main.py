from math import atan2
import sys
import pygame
from pygame.display import get_surface
from pygame.locals import *

pygame.init()
vec = pygame.math.Vector2

HEIGHT = 900
WIDTH = 900
ACC = 0.5
FRIC = -0.12
FPS = 60
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

CAMERA_Y = HEIGHT - 50

class SpriteRect(pygame.sprite.Sprite):
        def __init__(self, width, pos):
            super().__init__()
            self.surf = pygame.Surface((width, width))
            self.rect = self.surf.get_rect(center = (pos.x, pos.y-width/2))
            
        
        def setRect(self, rect):
            self.rect = rect;

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,width):
        super().__init__() 
        self.surf = pygame.Surface((30, 30))
        self.surf.fill((128,255,40))
        self.rect = self.surf.get_rect(center = pos)
        self.pos = vec(pos)
        #self.displayPos = vec(pos)
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.grounded = False;
        self.width = width;

    
    
    def collide(self, pos):
        rectSprite = SpriteRect(self.width,pos)
        hits = pygame.sprite.spritecollide(rectSprite, platforms, False);
        return hits 
    
    def move(self):
        
        self.acc = vec(0,0.5);
        
        pressed_keys = pygame.key.get_pressed();
        if pressed_keys[K_a]:
            self.acc.x = -ACC
        if pressed_keys[K_d]:
            self.acc.x = ACC

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        #self.pos += self.vel + 0.5 *self.acc
        self.temp = vec(0,0)
        delta = self.vel + 0.5 *self.acc;
        if not self.collide(vec(self.pos.x + delta.x, self.pos.y-1)):
            self.temp.x = delta.x
        else:
            self.vel.x = 0;
        if not self.collide(vec(self.pos.x , self.pos.y+ delta.y)):
            #self.temp.y = delta.y
            all_nonPlayerSprites.update(delta.y)
        else:
            self.vel.y = 0;
            self.grounded = True;
        self.pos += self.temp;
        
        # self.rect.midbottom = (self.pos.x + delta[0],self.pos.y);
        # hits = pygame.sprite.spritecollide(P1, platforms, False);
        # if hits:
        #     self.rect.midbottom = (self.pos.x - delta[0],self.pos.y);
        # self.rect.midbottom = (self.pos.x,self.pos.y + delta[0]);
        # hits = pygame.sprite.spritecollide(P1, platforms, False);
        # if hits:
        #     self.rect.midbottom = (self.pos.x,self.pos.y - delta[0]);
        # self.pos = vec(self.rect.midbottom)
        # if(pygame.Rect(self.rect.x, self.rect.y + self.dy+1, # +1
        #                 self.rect.width, self.rect.height)
        #     .colliderect(platform.rect))

            
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
     
        self.rect.midbottom = self.pos
    
    def jump(self):
        if self.grounded:
            self.vel.y = -15;
            self.grounded = False;

    def update(self):
            
            # if hits:

                
            #     width = hits[0].rect.width/2
            #     height = hits[0].rect.height/2
            #     direction = vec(0, abs((hits[0].rect.y - height)  - (self.pos.y+self.width/2)) );
            #     if direction.y > height:
            #         self.pos.y += -(self.vel + 0.5 *self.acc).y
            #         self.vel.y = 0;
            #         self.grounded = True;
            #     elif (hits[0].rect.center[0] - (self.pos.x+self.width) ) > width or (hits[0].rect.center[0] - (self.pos.x-self.width)) > width:
            #         self.pos.x += -(self.vel + 0.5 *self.acc).x
            #         self.vel.x = 0;
                

                #
                # if P1.rect.midtop[1] < hits[0].rect.midtop[1]:
                #     self.pos.y += -(self.vel + 0.5 *self.acc).y
                #     self.vel.y = 0;
                #     self.grounded = True;
                #     print('cock')
            
                # elif P1.rect.midleft[0] > hits[0].rect.midleft[0] or P1.rect.midright[0] < hits[0].rect.midright[0]:
                    
                #     self.pos.x += -(self.vel + 0.5 *self.acc).x
                #    self.vel.x = 0;
                    
                
                    
            # if hits:
            #     self.grounded = True;
            #     self.pos += -(self.vel + 0.5 *self.acc)*1.1 
            #     self.vel = vec(0,0);
            # else:
            #     self.grounded = False;
            #     #self.pos += -self.vel + 0.5 *self.acc
                
            #     # self.pos.y = hits[0].rect.top + 1
            #     # self.vel.y = 0
            self.rect.midbottom = self.pos
    

class platform(pygame.sprite.Sprite):
    def __init__(self,position,size):
        super().__init__()
        self.surf = pygame.Surface(size)
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = position)
        self.pos = vec(position)
    def update(self, dy):
        
        self.pos.y -= dy;
        self.rect.center = vec(self.pos.x,self.pos.y)

#RectSprite = SpriteRect(pygame.Rect((20, 50), (50, 100)))

PT1 = platform((WIDTH/2, HEIGHT -80), (WIDTH, 300))
PT2 = platform((WIDTH/2+100, HEIGHT-550), (50, 60))
PT3 = platform((WIDTH/2, HEIGHT - 400), (50, 60))

PT4 = platform((WIDTH/2 -200, HEIGHT - 500), (50, 60))


P1 = Player((200,HEIGHT - 280),30)
platforms = pygame.sprite.Group()
platforms.add(PT1)
platforms.add(PT2)
platforms.add(PT3)
platforms.add(PT4)
all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)
all_sprites.add(PT2)
all_sprites.add(PT3)
all_sprites.add(PT4)
all_nonPlayerSprites = all_sprites.copy()
all_sprites.add(P1)



while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                P1.jump();

     
    displaysurface.fill((0,0,0))
    
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
    P1.move();
    P1.update();
    pygame.display.update()
    FramePerSec.tick(FPS)