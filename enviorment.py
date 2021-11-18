import gym
from gym.core import ActionWrapper
from gym.spaces import space
import gym
import numpy as np
import pygame
import sys
from pygame.display import get_surface
from pygame.locals import *
from math import atan2
import map
class GameEnv(gym.Env):
    def __init__(self,agent,pygameEnv,env_config={}):
        self.agent = agent;
        self.pygameEnv = pygameEnv
        # self.observation_space = <gym.space>
        # self.action_space = <gym.space>
    
    def reset(self):
        self.pygameEnv.resetEnv();

    def step(self, action=np.zeros((2),dtype=np.float)):
        #action[0] left and right 0: nothing, 1: move left, 2: move right
        #action[1] jump 0: nothing, 1: jump

        
        self.agent.move(action[0])
        if action[1] == 1:
            self.agent.jump()
        observation, reward, done, info = self.agent.getObservation(),0.,False,{}
        return observation,reward, done, info

#enviorment = GameEnv();


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

yMapTileLength = int(len(MAP)/(X_COUNT-1))

print(yMapTileLength)
FramePerSec = pygame.time.Clock()

displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

all_sprites = pygame.sprite.Group()

boostOrbs = pygame.sprite.Group();

toggleBlocks = pygame.sprite.Group();
gamers = pygame.sprite.Group();
winOb = []
levers = pygame.sprite.Group();

class SpriteRect(pygame.sprite.Sprite):
        def __init__(self, width, pos):
            super().__init__()
            self.surf = pygame.Surface((width, width))
            self.rect = self.surf.get_rect(center = (pos.x, pos.y-width/2))
            
        
        def setRect(self, rect):
            self.rect = rect;

class Agent(pygame.sprite.Sprite):
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
        self.toggle = False;

    def getObservation(self):
        obs = [self.pos.y,]
        #observations will have y
        obs_norm = np.interp()
        return .0;
    
    def collide(self, pos):
        rectSprite = SpriteRect(self.width,pos)
        hits = pygame.sprite.spritecollide(rectSprite, platforms, False);
        return hits 
    
    def collideToggle(self, pos):
        rectSprite = SpriteRect(self.width,pos)
        hits = pygame.sprite.spritecollide(rectSprite, toggleBlocks, False);
        return hits 

    def collideBoostOrb(self, pos):
        rectSprite = SpriteRect(self.width,pos)
        hits = pygame.sprite.spritecollide(rectSprite, boostOrbs, False);
        return hits 

    def collideLever(self,pos):
        rectSprite = SpriteRect(self.width,vec(pos.x, pos.y+1))
        hits = pygame.sprite.spritecollide(rectSprite, levers, False);
        return hits 

    def move(self, input):
        
        self.acc = vec(0,GRAVITY);
        
        if input == 1:
            self.acc.x = -self.ACCVAL
        if input == 2:
            self.acc.x = self.ACCVAL

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        #self.pos += self.vel + 0.5 *self.acc
        self.temp = vec(0,0)
        delta = self.vel + 0.5 *self.acc;
        if not self.collide(vec(self.pos.x + delta.x, self.pos.y-1)) and self.pos.x > self.width/2 and self.pos.x <WIDTH:
            if self.toggle and self.collideToggle(vec(self.pos.x + delta.x, self.pos.y-1)):
                self.vel.x = 0;
            else:
                self.temp.x = delta.x
        else:
            # if self.pos.x < self.width/2 or self.pos.x >WIDTH:
            #     self.temp.x = -delta.x
            
            self.vel.x = 0;
        curHit = self.collide(vec(self.pos.x , self.pos.y+ delta.y));
        if not curHit:
            #self.temp.y = delta.y
            if not self.toggle or not self.collideToggle(vec(self.pos.x , self.pos.y+ delta.y)):
                all_nonPlayerSprites.update(delta.y,False, 0)
            else:
                self.vel.y = 0;
                self.grounded = True;
                self.boost = False
        else:
            self.vel.y = 0;
            self.grounded = True;
            self.boost = curHit[0].boost
        self.pos += self.temp;
        
        
            
        if self.pos.x > WIDTH-self.width/2:
            self.pos.x = WIDTH-self.width/2
        if self.pos.x < self.width/2:
            self.pos.x = self.width/2+0.5
    
        self.rect.midbottom = self.pos
    
    def jump(self):
        if self.collideBoostOrb(self.pos):
            self.vel.y = -self.JUMP_HEIGHT * 1.8;
        elif self.collideLever(self.pos+vec(0,10)):
            self.vel.y = -self.JUMP_HEIGHT;
            if self.toggle:
                self.toggle = False;
                toggleBlocks.update(0,True,(105, 77, 0))
            else:
                
                toggleBlocks.update(0,True,(252, 186, 3))
                self.toggle = True
        elif self.grounded:
            if self.boost:
                self.vel.y = -self.JUMP_HEIGHT * 1.8;
            else:
                self.vel.y = -self.JUMP_HEIGHT;
            self.grounded = False;
            self.boost = False;

    def update(self):
            
            
            self.rect.midbottom = self.pos
    
class goal(pygame.sprite.Sprite):
        def __init__(self,position,size,boost,color):
            super().__init__()
            self.width = size[0];
            self.surf = pygame.Surface(size)
            self.surf.fill(color)
            self.rect = self.surf.get_rect(center = position)
            self.pos = vec(position)
        def update(self, dy,colorChange, color):
            if colorChange:
                self.surf.fill(color)
                return
            self.pos.y -= dy;
            self.rect.center = vec(self.pos.x,self.pos.y)   
        def checkPlayer(self):
            hit = self.collideVictory();
            if hit:
                print("victory")
        def collideVictory(self):
            rectSprite = SpriteRect(self.width,vec(self.pos.x, self.pos.y))
            hits = pygame.sprite.spritecollide(rectSprite, gamers, False);
            return hits

            
# def raycast(angle,position):


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
        self.toggle = False;
        self.truePos = vec(self.pos.x, PLATFORM_SIZE* yMapTileLength - (HEIGHT - self.pos.y)  );
        print("playerPos")
        print(self.pos.y)
    
    def collide(self, pos):
        rectSprite = SpriteRect(self.width,pos)
        hits = pygame.sprite.spritecollide(rectSprite, platforms, False);
        return hits 
    
    def collideToggle(self, pos):
        rectSprite = SpriteRect(self.width,pos)
        hits = pygame.sprite.spritecollide(rectSprite, toggleBlocks, False);
        return hits 

    def collideBoostOrb(self, pos):
        rectSprite = SpriteRect(self.width,pos)
        hits = pygame.sprite.spritecollide(rectSprite, boostOrbs, False);
        return hits 

    def collideLever(self,pos):
        rectSprite = SpriteRect(self.width,vec(pos.x, pos.y+1))
        hits = pygame.sprite.spritecollide(rectSprite, levers, False);
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
            if self.toggle and self.collideToggle(vec(self.pos.x + delta.x, self.pos.y-1)):
                self.vel.x = 0;
            else:
                self.temp.x = delta.x
        else:
            # if self.pos.x < self.width/2 or self.pos.x >WIDTH:
            #     self.temp.x = -delta.x
            
            self.vel.x = 0;
        curHit = self.collide(vec(self.pos.x , self.pos.y+ delta.y));
        if not curHit:
            #self.temp.y = delta.y
            if not self.toggle or not self.collideToggle(vec(self.pos.x , self.pos.y+ delta.y)):
                all_nonPlayerSprites.update(delta.y,False, 0)
                self.truePos = vec(self.pos.x+ self.temp.x, self.truePos.y+delta.y )
            else:
                self.vel.y = 0;
                self.grounded = True;
                self.boost = False
        else:
            self.vel.y = 0;
            self.grounded = True;
            self.boost = curHit[0].boost
        self.pos += self.temp;
        
        
            
        if self.pos.x > WIDTH-self.width/2:
            self.pos.x = WIDTH-self.width/2
        if self.pos.x < self.width/2:
            self.pos.x = self.width/2+0.5
        
        print(self.truePos)
        self.rect.midbottom = self.pos
    
    def jump(self):
        if self.collideBoostOrb(self.pos):
            self.vel.y = -self.JUMP_HEIGHT * 1.8;
        elif self.collideLever(self.pos+vec(0,10)):
            self.vel.y = -self.JUMP_HEIGHT;
            if self.toggle:
                self.toggle = False;
                toggleBlocks.update(0,True,(105, 77, 0))
            else:
                
                toggleBlocks.update(0,True,(252, 186, 3))
                self.toggle = True
        elif self.grounded:
            if self.boost:
                self.vel.y = -self.JUMP_HEIGHT * 1.8;
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
    def update(self, dy,colorChange, color):
        if colorChange:
            self.surf.fill(color)
            return
        self.pos.y -= dy;
        self.rect.center = vec(self.pos.x,self.pos.y)
        
        
        


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
                gamers.add(P1)
            if MAP[y*X_COUNT + x] == 2:
                PT = platform((localStart + x*PLATFORM_SIZE,localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE, PLATFORM_SIZE), True,(0,255,0))
                platforms.add(PT)
                all_sprites.add(PT)
            if MAP[y*X_COUNT+x] == 3:
                PT = platform((localStart + x*PLATFORM_SIZE,localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE-10, PLATFORM_SIZE-10), True,(0,255,170))
                all_sprites.add(PT);
                boostOrbs.add(PT)
            if MAP[y*X_COUNT+x] == 4:
                PT = platform((localStart + x*PLATFORM_SIZE,localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE-10, PLATFORM_SIZE-10), False,(255,255,170))
                all_sprites.add(PT);
                levers.add(PT)
                platforms.add(PT)
            if MAP[y*X_COUNT+x] == 5:
                PT = platform((localStart + x*PLATFORM_SIZE,localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE, PLATFORM_SIZE), False,(105, 77, 0))
                all_sprites.add(PT);
                toggleBlocks.add(PT)
            if MAP[y*X_COUNT+x] == 8:
                    print("wat")
                    PT = goal((localStart + x*PLATFORM_SIZE,localHeight - i*PLATFORM_SIZE), (PLATFORM_SIZE, PLATFORM_SIZE), False,( 249, 46, 196 ))
                    winOb.append(PT)
                    all_sprites.add(PT);
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
                P1.jump()
            
        

    
    displaysurface.fill((0,0,0))
    
    for entity in all_sprites:
        displaysurface.blit(entity.surf, entity.rect)
    #player doing stuff
    P1.move();
    P1.update();
    
    #pygame.draw.line(displaysurface,(255,255,255), (40,780), (80,720), 2)

    #agent move
    #enviorment.step(action)
    winOb[0].checkPlayer()
    font = pygame.font.SysFont(None, 24)
    img = font.render("fps: "+"{:.2f}".format(clock.get_fps()), True, "#20afdf")
    clock.tick()
    displaysurface.blit(img, (20, 20))
    pygame.display.update()
    FramePerSec.tick(FPS)

# def reset(self):
#     return observation

# def step(self,action):
#     return observation, reward, done, info