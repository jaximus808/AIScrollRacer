import gym
from gym.core import ActionWrapper
from gym.spaces import space
import gym
import numpy as np
#import pygame
import sys
#import pygame
from pygame.display import get_surface
from pygame.locals import *
from math import atan2
import map
class GameEnv(gym.Env):
    import pygame
    from pygame.display import get_surface
    #from pygame.locals import * 
    import sys

    def __init__(self,agent,pygameEnv,env_config={}):
        self.pygame.init();
        self.agent = agent;
        self.pygameEnv = pygameEnv
        self.vec = self.pygame.math.Vector2
        
        
        self.HEIGHT = 800
        self.WIDTH = 1250
        self.FRIC = -0.12
        self.FPS = 80
        self.GRAVITY = 0.5
        self.clock = self.pygame.time.Clock()
        self.PLATFORM_SIZE = 50;
        self.X_COUNT = int(self.WIDTH / self.PLATFORM_SIZE);

        self.MAP = map.MAP

        self.platforms = self.pygame.sprite.Group()

        self.yMapTileLength = int(len(self.MAP)/(self.X_COUNT-1))

        self.FramePerSec = self.pygame.time.Clock()

        self.displaysurface = self.pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.pygame.display.set_caption("Game")

        self.all_sprites = self.pygame.sprite.Group()

        self.boostOrbs = self.pygame.sprite.Group();

        self.toggleBlocks = self.pygame.sprite.Group();
        self.gamers = self.pygame.sprite.Group();
        self.winOb = []
        self.levers = self.pygame.sprite.Group();
        self.P1 = self.Player((200,self.HEIGHT - 280),30, 15, 0.5,self)
        self.createEnviorment(self);
        self.all_nonPlayerSprites = self.all_sprites.copy()
        self.all_sprites.add(self.P1)
        # self.observation_space = <gym.space>
        # self.action_space = <gym.space>
    
    #right now just try transfer files into class and be able to run the loop through some env.step method and then env.render or smth

    class SpriteRect(pygame.sprite.Sprite):
        def __init__(self, width, pos, main ):
            super().__init__()
            self.surf = main.pygame.Surface((width, width))
            self.rect = self.surf.get_rect(center = (pos.x, pos.y-width/2))
            
        
        def setRect(self, rect):
            self.rect = rect;
    class Player(pygame.sprite.Sprite):
        def __init__(self,pos,width, jumpHeight,acc,main):
            super().__init__()
            self.main = main; 
            self.surf = main.pygame.Surface((30, 30))
            self.surf.fill((128,255,40))
            self.rect = self.surf.get_rect(center = pos)
            self.pos = main.vec(pos)
            #self.displayPos = vec(pos)
            self.vel = main.vec(0,0)
            self.acc = main.vec(0,0)
            self.grounded = False;
            self.width = width;
            self.JUMP_HEIGHT = jumpHeight;
            self.ACCVAL = acc; 
            self.boost = False;
            self.toggle = False;
            self.truePos = main.vec(self.pos.x, main.PLATFORM_SIZE* main.yMapTileLength - (main.HEIGHT - self.pos.y)  );
            print("playerPos")
            print(self.pos.y)
        
        def collide(self, pos):
            rectSprite = self.main.SpriteRect(self.width,pos,self.main)
            hits = self.main.pygame.sprite.spritecollide(rectSprite, self.main.platforms, False);
            return hits 
        
        def collideToggle(self, pos):
            rectSprite = self.main.SpriteRect(self.width,pos,self.main)
            hits = self.main.pygame.sprite.spritecollide(rectSprite, self.main.toggleBlocks, False);
            return hits 

        def collideBoostOrb(self, pos):
            rectSprite = self.main.SpriteRect(self.width,pos,self.main)
            hits = self.main.pygame.sprite.spritecollide(rectSprite, self.main.boostOrbs, False);
            return hits 

        def collideLever(self,pos):
            rectSprite = self.main.SpriteRect(self.width,self.main.vec(pos.x, pos.y+1),self.main)
            hits = self.main.pygame.sprite.spritecollide(rectSprite, self.main.levers, False);
            return hits 

        def move(self):
            
            self.acc = self.main.vec(0,self.main.GRAVITY);
            
            pressed_keys = self.main.pygame.key.get_pressed();
            if pressed_keys[K_a]:
                self.acc.x = -self.ACCVAL
            if pressed_keys[K_d]:
                self.acc.x = self.ACCVAL

            self.acc.x += self.vel.x * self.main.FRIC
            self.vel += self.acc
            #self.pos += self.vel + 0.5 *self.acc
            self.temp = self.main.vec(0,0)
            delta = self.vel + 0.5 *self.acc;
            if not self.collide(self.main.vec(self.pos.x + delta.x, self.pos.y-1)) and self.pos.x > self.width/2 and self.pos.x <self.main.WIDTH:
                if self.toggle and self.collideToggle(self.main.vec(self.pos.x + delta.x, self.pos.y-1)):
                    self.vel.x = 0;
                else:
                    self.temp.x = delta.x
            else:
                # if self.pos.x < self.width/2 or self.pos.x >WIDTH:
                #     self.temp.x = -delta.x
                
                self.vel.x = 0;
            curHit = self.collide(self.main.vec(self.pos.x , self.pos.y+ delta.y));
            if not curHit:
                #self.temp.y = delta.y
                if not self.toggle or not self.collideToggle(self.main.vec(self.pos.x , self.pos.y+ delta.y)):
                    self.main.all_nonPlayerSprites.update(delta.y,False, 0)
                    self.truePos = self.main.vec(self.pos.x+ self.temp.x, self.truePos.y+delta.y )
                else:
                    self.vel.y = 0;
                    self.grounded = True;
                    self.boost = False
            else:
                self.vel.y = 0;
                self.grounded = True;
                self.boost = curHit[0].boost
            self.pos += self.temp;
            
            
                
            if self.pos.x > self.main.WIDTH-self.width/2:
                self.pos.x = self.main.WIDTH-self.width/2
            if self.pos.x < self.width/2:
                self.pos.x = self.width/2+0.5
            
            print(self.truePos)
            self.rect.midbottom = self.pos
        
        def jump(self):
            if self.collideBoostOrb(self.pos):
                self.vel.y = -self.JUMP_HEIGHT * 1.8;
            elif self.collideLever(self.pos+self.main.vec(0,10)):
                self.vel.y = -self.JUMP_HEIGHT;
                if self.toggle:
                    self.toggle = False;
                    self.main.toggleBlocks.update(0,True,(105, 77, 0))
                else:
                    
                    self.main.toggleBlocks.update(0,True,(252, 186, 3))
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
        def __init__(self,position,size,boost,color,main):
            super().__init__()
            self.main = main;
            self.width = size[0];
            self.surf = main.pygame.Surface(size)
            self.surf.fill(color)
            self.rect = self.surf.get_rect(center = position)
            self.pos = main.vec(position)
        def update(self, dy,colorChange, color):
            if colorChange:
                self.surf.fill(color)
                return
            self.pos.y -= dy;
            self.rect.center = self.main.vec(self.pos.x,self.pos.y)   
        def checkPlayer(self):
            hit = self.collideVictory();
            if hit:
                print("victory")
        def collideVictory(self):
            rectSprite = self.main.SpriteRect(self.width,self.main.vec(self.pos.x, self.pos.y),self.main)
            hits = self.main.pygame.sprite.spritecollide(rectSprite, self.main.gamers, False);
            return hits

    class platform(pygame.sprite.Sprite):
        def __init__(self,position,size,boost,color,main):
            super().__init__()
            self.main = main;
            self.surf = main.pygame.Surface(size)
            self.surf.fill(color)
            self.rect = self.surf.get_rect(center = position)
            self.pos = main.vec(position)
            self.boost = boost
        def update(self, dy,colorChange, color):
            if colorChange:
                self.surf.fill(color)
                return
            self.pos.y -= dy;
            self.rect.center = self.main.vec(self.pos.x,self.pos.y)
            
    
    def createEnviorment(self,_main):
        main = _main
        localHeight = main.HEIGHT - main.PLATFORM_SIZE/2-200
        localStart = main.PLATFORM_SIZE/2
        i = 0;
        for y in range( int(((len(main.MAP))/main.X_COUNT)-1) ,0,-1):
            prior = False;
            pos = 0; 
            counter = 0;
            for x in range(main.X_COUNT):
                
                if main.MAP[y*main.X_COUNT + x] == 1:
                    if prior:
                        counter +=1;
                    else:
                        counter+=1;
                        prior = True;
                        pos = x;
                else:
                    if prior:
                        PT = main.platform(((main.PLATFORM_SIZE*pos + main.PLATFORM_SIZE*(counter+pos))/2, localHeight - i*main.PLATFORM_SIZE), (main.PLATFORM_SIZE*counter, main.PLATFORM_SIZE), False,(255,0,0),main)
                        main.platforms.add(PT)
                        main.all_sprites.add(PT)
                        prior = False;
                        counter = 0;
                if main.MAP[y*main.X_COUNT + x] == 9:
                    main.P1.pos= main.vec(main.PLATFORM_SIZE*x,localHeight - i*main.PLATFORM_SIZE)
                    main.gamers.add(main.P1)
                if main.MAP[y*main.X_COUNT + x] == 2:
                    PT = main.platform((localStart + x*main.PLATFORM_SIZE,localHeight - i*main.PLATFORM_SIZE), (main.PLATFORM_SIZE, main.PLATFORM_SIZE), True,(0,255,0),main)
                    main.platforms.add(PT)
                    main.all_sprites.add(PT)
                if main.MAP[y*main.X_COUNT+x] == 3:
                    PT = main.platform((localStart + x*main.PLATFORM_SIZE,localHeight - i*main.PLATFORM_SIZE), (main.PLATFORM_SIZE-10, main.PLATFORM_SIZE-10), True,(0,255,170),main)
                    main.all_sprites.add(PT);
                    main.boostOrbs.add(PT)
                if main.MAP[y*main.X_COUNT+x] == 4:
                    PT = main.platform((localStart + x*main.PLATFORM_SIZE,localHeight - i*main.PLATFORM_SIZE), (main.PLATFORM_SIZE-10, main.PLATFORM_SIZE-10), False,(255,255,170),main)
                    main.all_sprites.add(PT);
                    main.levers.add(PT)
                    main.platforms.add(PT)
                if main.MAP[y*main.X_COUNT+x] == 5:
                    PT = main.platform((localStart + x*main.PLATFORM_SIZE,localHeight - i*main.PLATFORM_SIZE), (main.PLATFORM_SIZE, main.PLATFORM_SIZE), False,(105, 77, 0),main)
                    main.all_sprites.add(PT);
                    main.toggleBlocks.add(PT)
                if main.MAP[y*main.X_COUNT+x] == 8:
                        print("wat")
                        PT = main.goal((localStart + x*main.PLATFORM_SIZE,localHeight - i*main.PLATFORM_SIZE), (main.PLATFORM_SIZE, main.PLATFORM_SIZE), False,( 249, 46, 196 ),main)
                        main.winOb.append(PT)
                        main.all_sprites.add(PT);
            if prior:
                PT = main.platform(((main.PLATFORM_SIZE*pos + main.PLATFORM_SIZE*(counter+pos))/2, localHeight - i*main.PLATFORM_SIZE), (main.PLATFORM_SIZE*counter, main.PLATFORM_SIZE), False,(255,0,0),main)
                main.platforms.add(PT)
                main.all_sprites.add(PT)
            i+= 1;
            
    def render():
        print("hi"); # will do something more here

    def reset(self):
        self.pygameEnv.resetEnv();

    def step(self, action=np.zeros((2),dtype=np.float)):
        #action[0] left and right 0: nothing, 1: move left, 2: move right
        #action[1] jump 0: nothing, 1: jump

        for event in self.pygame.event.get():
            if event.type == QUIT:
                self.pygame.quit()
                self.sys.exit(0)
            if event.type == self.pygame.KEYDOWN:
                if event.key == self.pygame.K_SPACE or event.key == self.pygame.K_w:
                    self.P1.jump()
                
            

        
        self.displaysurface.fill((0,0,0))
        
        for entity in self.all_sprites:
            self.displaysurface.blit(entity.surf, entity.rect)
        #player doing stuff
        self.P1.move();
        self.P1.update();
        
        #pygame.draw.line(displaysurface,(255,255,255), (40,780), (80,720), 2)

        #agent move
        #enviorment.step(action)
        self.winOb[0].checkPlayer()
        font = self.pygame.font.SysFont(None, 24)
        img = font.render("fps: "+"{:.2f}".format(self.clock.get_fps()), True, "#20afdf")
        self.clock.tick()
        self.displaysurface.blit(img, (20, 20))
        self.pygame.display.update()
        self.FramePerSec.tick(self.FPS)

if __name__ == "__main__":
    currentGameEnv = GameEnv(1,2);
    while True:
        currentGameEnv.step();
