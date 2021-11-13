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
clock = pygame.time.Clock()
PLATFORM_SIZE = 50;
X_COUNT = int(WIDTH / PLATFORM_SIZE);

MAP = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,
        0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,
        0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,
        0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]


platforms = pygame.sprite.Group()

FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

all_sprites = pygame.sprite.Group()

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


def createEnviorment():
    localHeight = HEIGHT - PLATFORM_SIZE/2
    localStart = PLATFORM_SIZE/2
    i = 0;
    for y in range( int(((len(MAP))/X_COUNT)-1) ,0,-1):
        for x in range(X_COUNT):
            
            if MAP[y*X_COUNT + x] == 1:
                PT = platform((localStart + PLATFORM_SIZE*x, localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE, PLATFORM_SIZE))
                platforms.add(PT)
                all_sprites.add(PT)
        i+= 1;
createEnviorment();
print(len(MAP))
print(32*X_COUNT )  

# PT1 = platform((WIDTH/2, HEIGHT -80), (WIDTH, 300))
# PT2 = platform((WIDTH/2+100, HEIGHT-550), (50, 60))
# PT3 = platform((WIDTH/2, HEIGHT - 400), (50, 60))

# PT4 = platform((WIDTH/2 -200, HEIGHT - 500), (50, 60))


P1 = Player((200,HEIGHT - 280),30)
# platforms = pygame.sprite.Group()
# platforms.add(PT1)
# platforms.add(PT2)
# platforms.add(PT3)
# platforms.add(PT4)

# all_sprites.add(PT1)
# all_sprites.add(PT2)
# all_sprites.add(PT3)
# all_sprites.add(PT4)
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
    font = pygame.font.SysFont(None, 24)
    img = font.render("fps: "+"{:.2f}".format(clock.get_fps()), True, "#20afdf")
    clock.tick()
    displaysurface.blit(img, (20, 20))
    pygame.display.update()
    FramePerSec.tick(FPS)