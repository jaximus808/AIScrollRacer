import sys
import pygame
from pygame.display import get_surface
from pygame.locals import *
from math import atan2
import map
def runLevel():


    pygame.init()
    vec = pygame.math.Vector2

    HEIGHT = 800
    WIDTH = 1250
    FRIC = -0.12
    FPS = 80
    GRAVITY = 0.5
    clock = pygame.time.Clock()
    PLATFORM_SIZE = 50;
    X_COUNT = int(WIDTH / PLATFORM_SIZE);

    MAP = map.MAP

    platforms = pygame.sprite.Group()

    FramePerSec = pygame.time.Clock()
    
    displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game")

    all_sprites = pygame.sprite.Group()


    class SpriteRect(pygame.sprite.Sprite):
            def __init__(self, width, pos):
                super().__init__()
                self.surf = pygame.Surface((width, width))
                self.rect = self.surf.get_rect(center = (pos.x, pos.y-width/2))
                
            
            def setRect(self, rect):
                self.rect = rect;

    class Player(pygame.sprite.Sprite):
        def __init__(self,pos,width, jumpHeight,acc):
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
            self.JUMP_HEIGHT = jumpHeight;
            self.ACCVAL = acc; 
            self.boost = False;

        
        
        def collide(self, pos):
            rectSprite = SpriteRect(self.width,pos)
            hits = pygame.sprite.spritecollide(rectSprite, platforms, False);
            return hits 
        
        def move(self):
            
            self.acc = vec(0,GRAVITY);
            
            pressed_keys = pygame.key.get_pressed();
            if pressed_keys[K_a]:
                self.acc.x = -self.ACCVAL
            if pressed_keys[K_d]:
                self.acc.x = self.ACCVAL

            self.acc.x += self.vel.x * FRIC
            self.vel += self.acc
            #self.pos += self.vel + 0.5 *self.acc
            self.temp = vec(0,0)
            delta = self.vel + 0.5 *self.acc;
            if not self.collide(vec(self.pos.x + delta.x, self.pos.y-1)) and self.pos.x > self.width/2 and self.pos.x <WIDTH:
                self.temp.x = delta.x
            else:
                if self.pos.x > self.width/2 or self.pos.x <WIDTH:
                    self.temp.x = -delta.x
                self.vel.x = 0;
            curHit = self.collide(vec(self.pos.x , self.pos.y+ delta.y));
            if not curHit:
                #self.temp.y = delta.y
                all_nonPlayerSprites.update(delta.y)
            else:
                self.vel.y = 0;
                self.grounded = True;
                self.boost = curHit[0].boost
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
                if self.boost:
                    self.vel.y = -self.JUMP_HEIGHT * 2;
                else:
                    self.vel.y = -self.JUMP_HEIGHT;
                self.grounded = False;
                self.boost = False;

        def update(self):
                
                
                self.rect.midbottom = self.pos
        

    class platform(pygame.sprite.Sprite):
        def __init__(self,position,size,boost,color):
            super().__init__()
            self.surf = pygame.Surface(size)
            self.surf.fill(color)
            self.rect = self.surf.get_rect(center = position)
            self.pos = vec(position)
            self.boost = boost
        def update(self, dy):
            
            self.pos.y -= dy;
            self.rect.center = vec(self.pos.x,self.pos.y)

    #RectSprite = SpriteRect(pygame.Rect((20, 50), (50, 100)))


    def createEnviorment():
        localHeight = HEIGHT - PLATFORM_SIZE/2-200
        localStart = PLATFORM_SIZE/2
        i = 0;
        for y in range( int(((len(MAP))/X_COUNT)-1) ,0,-1):
            prior = False;
            pos = 0; 
            counter = 0;
            for x in range(X_COUNT):
                
                if MAP[y*X_COUNT + x] == 1:
                    if prior:
                        counter +=1;
                    else:
                        counter+=1;
                        prior = True;
                        pos = x;
                else:
                    if prior:
                        PT = platform(((PLATFORM_SIZE*pos + PLATFORM_SIZE*(counter+pos))/2, localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE*counter, PLATFORM_SIZE), False,(255,0,0))
                        platforms.add(PT)
                        all_sprites.add(PT)
                        prior = False;
                        counter = 0;
                if MAP[y*X_COUNT + x] == 9:
                    P1.pos= vec(PLATFORM_SIZE*x,localHeight - i*PLATFORM_SIZE)
                if MAP[y*X_COUNT + x] == 2:
                    PT = platform((localStart + x*PLATFORM_SIZE,localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE, PLATFORM_SIZE), True,(0,255,0))
                    platforms.add(PT)
                    all_sprites.add(PT)
                    print("??")

            if prior:
                PT = platform(((PLATFORM_SIZE*pos + PLATFORM_SIZE*(counter+pos))/2, localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE*counter, PLATFORM_SIZE), False,(255,0,0))
                platforms.add(PT)
                all_sprites.add(PT)
            i+= 1;
            
    P1 = Player((200,HEIGHT - 280),30, 15, 0.5)
    createEnviorment();
    print(len(MAP))
    print(32*X_COUNT )  

    # PT1 = platform((WIDTH/2, HEIGHT -80), (WIDTH, 300))
    # PT2 = platform((WIDTH/2+100, HEIGHT-550), (50, 60))
    # PT3 = platform((WIDTH/2, HEIGHT - 400), (50, 60))

    # PT4 = platform((WIDTH/2 -200, HEIGHT - 500), (50, 60))


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
runLevel();