import gym
from gym.core import ActionWrapper
from gym.spaces import space
import gym
import numpy as np
import pygame
import sys
import pygame
#import pygame
from pygame.display import get_surface
from pygame.locals import *
from math import atan2, dist, floor, radians
import map
class GameEnv(gym.Env):
    import pygame
    from pygame.display import get_surface
    #from pygame.locals import * 
    import sys
    import math;
    MAX_STEPS = 5000
    def __init__(self,env_config={}):
        self.pygame.init();
        self.vec = self.pygame.math.Vector2
        self.PI = self.math.pi;
            
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
        self.AIgamers = self.pygame.sprite.Group();
        self.winOb = []
        self.levers = self.pygame.sprite.Group();
        self.P1 = self.Player((200,self.HEIGHT - 280),30, 15, 0.5,self)
        self.agent = self.Agent((self.WIDTH -200,self.HEIGHT - 280),30, 15, 0.5,self)
        self.AIgamers.add(self.agent)
        self.createEnviorment(self);
        self.all_nonPlayerSprites = self.all_sprites.copy()
        self.all_sprites.add(self.P1)
        self.all_sprites.add(self.agent)
        self.raycastAmount = 30
        self.reward = 0
        self.huerstic = True
        self.iterateReward = -0.001
        self.highScoreReward = 0.3;
        self.victoryReward = 5;
        self.done = False;
        # first dimesion is left and right, 0 means left, 1 means right, 2 menas do nothing 
        # second dimension is jumping, 0 means do nothing , 1 means jump
        self.action_space = gym.spaces.MultiDiscrete([3,2])
        #ray cast points self.raycastAmount and colorId so that would be 60 points. Then we will give the yHeight so +1, 
        # k screw numpy lmfao
        # self.obArray = [];
        # for i in range(30):
        #     self.obArray.append((0,10000000000))
        #     self.obArray.append((0,10))
        # self.obArray.append((0,10000000))
        # print(self.obArray)
        numeric_min = np.zeros(self.raycastAmount*2 + 1)
        self.state = numeric_min
        numeric_max = np.zeros(self.raycastAmount*2 +1)
        for i in range(self.raycastAmount):
            numeric_max[i*2] = 100000000
            numeric_max[i*2 +1] = 10
        numeric_max[len(numeric_max)-1] = 100000000
        print(numeric_max)
        self.observation_space = gym.spaces.Box(numeric_min,numeric_max,dtype = np.float64)
        self.info = {}
    
    #right now just try transfer files into class and be able to run the loop through some env.step method and then env.render or smth

    def reset(self):
        self.platforms = self.pygame.sprite.Group()
        self.state = np.zeros(self.raycastAmount*2 + 1)
        self.yMapTileLength = int(len(self.MAP)/(self.X_COUNT-1))

        self.FramePerSec = self.pygame.time.Clock()

        self.displaysurface = self.pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.pygame.display.set_caption("Game")

        self.all_sprites = self.pygame.sprite.Group()

        self.boostOrbs = self.pygame.sprite.Group();
        self.done = False;
        self.toggleBlocks = self.pygame.sprite.Group();
        self.gamers = self.pygame.sprite.Group();
        self.winOb = []
        self.levers = self.pygame.sprite.Group();
        self.P1 = self.Player((200,self.HEIGHT - 280),30, 15, 0.5,self)
        self.agent = self.Agent((self.WIDTH -200,self.HEIGHT - 280),30, 15, 0.5,self)
        self.gamers.add(self.agent)
        self.createEnviorment(self);
        self.all_nonPlayerSprites = self.all_sprites.copy()
        self.all_sprites.add(self.P1)
        self.all_sprites.add(self.agent)
        self.reward = 0
        self.info = {}
        return self.state
        

    def raycast(self, pos, degAngle,rayDist):
        mx,my,mp,dof,rx,ry,xo,yo,distT = 0,0,0,0,0,0,0,0,0
        xXS,xYS, yXS, yYS = 0,0,0,0
        distY = 1000000;
        distX = 1000000; 
        dof = 0
        ang = self.PI * degAngle/180 #to radians
        colorXId = 0;
        colorYId = 0;
        aTan = -1/self.math.tan(ang);
        if ang > self.PI: #looking down 
            #rounds down so good 
            ry = floor(pos.y/self.PLATFORM_SIZE)*self.PLATFORM_SIZE - 0.0001;
            rx = (pos.y - ry) * aTan + pos.x;
            
            yo = -self.PLATFORM_SIZE
            
            #adjacent of our ray cast triangle
            xo = -yo *aTan;
            
        elif ang < self.PI: #looking up
            #needs to account for rounding down and needs to always round up, 
            ry = floor(pos.y/self.PLATFORM_SIZE)*self.PLATFORM_SIZE + self.PLATFORM_SIZE;
            
            rx = (pos.y - ry) *aTan + pos.x;
            yo = self.PLATFORM_SIZE;
            #adjacent of our ray cast triangle
            xo = -yo*aTan;
            
            
        else: #looking horizontal 
            rx = pos.x;
            ry = pos.y;
            dof = rayDist;
        hit = False
        #actual raycast
        while (dof < rayDist):
            mx = floor(rx/self.PLATFORM_SIZE);
            my = floor(ry/self.PLATFORM_SIZE);
            mp = my * self.X_COUNT + mx;
            
            #might need a check for hitting border of screen
            if mp < 0 or mp >= len(self.MAP)or  mx > self.WIDTH:
                hit = True;
                yXS = rx;
                yYS = ry;
                dof = rayDist;
            elif self.MAP[mp] > 0:
                colorYId = self.MAP[mp]
                yXS = rx; 
                yYS = ry;
                dof = rayDist;

                hit = True;
            else:
                rx += xo
                ry += yo
                dof +=1;

        if not hit:
            distY = 10000000;
        else:
            distY = dist([pos.x, pos.y], [yXS, yYS])
        
        #horizontal line check
        dof = 0
        nTan = -self.math.tan(ang);
        if(ang > self.PI/2 and ang < 3*self.PI/2): #looing left
            rx = floor(pos.x/self.PLATFORM_SIZE)*self.PLATFORM_SIZE - 0.0001
            ry = (pos.x - rx) * nTan+pos.y;
            xo = -self.PLATFORM_SIZE;
            yo = -xo * nTan;
        elif (ang < self.PI/2 or ang > 3*self.PI/2): #looking right
            rx = floor(pos.x/self.PLATFORM_SIZE)*self.PLATFORM_SIZE +self.PLATFORM_SIZE;
            ry = (pos.x - rx) * nTan+pos.y;
            
            xo = self.PLATFORM_SIZE;
            yo = -xo * nTan;
        else:
            ry = pos.x;
            rx = pos.y;
            dof = rayDist;

        hit = False;
        while(dof < rayDist):
            mx = floor(rx/self.PLATFORM_SIZE);
            my = floor(ry/self.PLATFORM_SIZE);
            mp = my * self.X_COUNT + mx;
            if mp < 0 or mp >= len(self.MAP) or mx > self.WIDTH:
                hit = True;
                xXS = rx;
                xYS = ry;
                dof = rayDist;
            elif  self.MAP[mp] > 0:
                colorXId = self.MAP[mp]
                hit = True;
                xXS = rx;
                xYS = ry;
                dof = rayDist;
            else:
                rx += xo;
                ry += yo;
                dof += 1;
        
        if not hit:
            distX = 1000000;
        else:
            distX = dist([pos.x, pos.y], [xXS, xYS])
        hitBool = True;
        tX, tY = 0,0
        tColor = 0;
        if distX < distY:
            tColor = colorXId
            tX = xXS;
            tY = xYS;
            distT = distX
            
        elif distX > distY:
            tColor = colorYId
            tX = yXS;
            tY = yYS;
            distT = distY
        else:
            hitBool = False;
            tX = xXS;
            tY = xYS;
            distT = distY
        
        return distT, tX, tY, tColor, hitBool;

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
            self.truePos = main.vec(self.pos.x, main.PLATFORM_SIZE* (main.yMapTileLength)  -(main.HEIGHT- self.pos.y));
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
                    self.main.agent.update(delta.y)
                    self.truePos.y += delta.y
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
            self.truePos.x = self.pos.x;
            #print(self.truePos)
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
    class Agent(pygame.sprite.Sprite):
        def __init__(self,pos,width, jumpHeight,acc,main):
            super().__init__()
            self.main = main; 
            self.surf = main.pygame.Surface((30, 30))
            self.surf.fill((140, 13, 62))
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
            self.highScoreY = self.pos.y; 
            
            #self.truePos = self.pos#main.vec(self.pos.x, main.PLATFORM_SIZE* (main.yMapTileLength)  -(main.HEIGHT- self.pos.y));
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

        def move(self,inputArray):
            
            #inputArray= 2 dimensional
            # 1: 0, 1, 2. Left and right and nothing
            # 2: 0, 1. nothing and jump

            self.acc = self.main.vec(0,self.main.GRAVITY);
            
            #pressed_keys = self.main.pygame.key.get_pressed();
            jumpInput = inputArray[1]
            horizontalIn = inputArray[0]
            if horizontalIn == 0:
                self.acc.x = -self.ACCVAL
            if horizontalIn == 1:
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
                    #self.main.all_nonPlayerSprites.update(delta.y,False, 0)
                    self.pos.y += delta.y
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
            #self.truePos.x = self.pos.x;
            #print(self.truePos)
            newHigh = False;
            if self.pos.y > self.highScoreY:
                newHigh = True;
                self.highScoreY = self.pos.y;

            if jumpInput == 1:
                self.jump();

            
            self.rect.midbottom = self.main.vec(self.pos.x,self.pos.y)
            return newHigh; 
        
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

        def update(self, dy):
            self.pos.y -= dy;
            #self.rect.midbottom = self.truePos
    
    class goal(pygame.sprite.Sprite):
        def __init__(self,position,size,boost,color,main):
            super().__init__()
            self.main = main;
            self.width = size[0];
            self.surf = main.pygame.Surface(size)
            self.surf.fill(color)
            self.rect = self.surf.get_rect(center = position)
            self.pos = main.vec(position)
            self.truePos = main.vec(position); 
        def update(self, dy,colorChange, color):
            if colorChange:
                self.surf.fill(color)
                return
            self.pos.y -= dy;
            self.rect.center = self.main.vec(self.pos.x,self.pos.y)   
        def checkPlayer(self):
            hit = self.collideVictory();
            if hit:
                self.main.reset();
                print("victory")
        def checkAI(self):
            hit = self.collideVictoryAI();
            return hit; 
        def collideVictory(self):
            rectSprite = self.main.SpriteRect(self.width,self.main.vec(self.pos.x, self.pos.y),self.main)
            hits = self.main.pygame.sprite.spritecollide(rectSprite, self.main.gamers, False);
            return hits
        def collideVictoryAI(self):
            rectSprite = self.main.SpriteRect(self.width,self.main.vec(self.pos.x, self.pos.y),self.main)
            hits = self.main.pygame.sprite.spritecollide(rectSprite, self.main.AIgamers, False);
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
            self.truePos = main.vec(position); 
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
                if main.MAP[y*main.X_COUNT + x] == -1:
                    main.P1.pos= main.vec(main.PLATFORM_SIZE*x,localHeight - i*main.PLATFORM_SIZE)
                    main.P1.truePos.y = y*main.PLATFORM_SIZE+(main.PLATFORM_SIZE - main.P1.width)/2; 
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
            

    def render(self):
        self.displaysurface.fill((0,0,0))
        for entity in self.all_sprites:
            self.displaysurface.blit(entity.surf, entity.rect)
        font = self.pygame.font.SysFont(None, 24)
        img = font.render("fps: "+"{:.2f}".format(self.clock.get_fps()), True, "#20afdf")
        self.clock.tick()
        self.displaysurface.blit(img, (20, 20))
        self.pygame.display.update()
        self.FramePerSec.tick(self.FPS)

    def step(self, action=np.zeros((2),dtype=np.float)):
        #action[0] left and right 0: nothing, 1: move left, 2: move right
        #action[1] jump 0: nothing, 1: jump
        
        inputArray = action;
        if(self.huerstic):
            inputArray = [2,0]
            pressed_keys = self.pygame.key.get_pressed();
            if pressed_keys[K_j]:
                inputArray[0] = 0
            elif pressed_keys[K_l]:
                inputArray[0] = 1
                    
            if pressed_keys[K_i]:
                inputArray[1] = 1
        for event in self.pygame.event.get():
            if event.type == QUIT:
                self.pygame.quit()
                self.sys.exit(0)
            if event.type == self.pygame.KEYDOWN:
                if event.key == self.pygame.K_SPACE or event.key == self.pygame.K_w:
                    self.P1.jump()
                
                # if event.key == self.pygame.K_j:
                #     inputArray[0] = 0
                # elif event.key == self.pygame.K_l:
                #     inputArray[0] = 1
                
                # if event.key == self.pygame.K_i:
                #     inputArray[1] = 1
        self.reward = 0;
        highCond = self.agent.move(inputArray) 
        if highCond:
            self.reward += self.highScoreReward
        if self.winOb[0].checkAI():
            self.done = True;
            self.reward += self.victoryReward;
        self.reward -= self.iterateReward
        
        #player doing stuff
        self.P1.move();
        self.P1.update();
        
        for i in range(self.raycastAmount):
            dist, rayX, rayY, color, hitTrue =  self.raycast(self.vec(self.agent.pos.x,self.agent.pos.y-self.agent.width/2 +10),((i*(360/self.raycastAmount))+0.0001),20) 
            self.state[i*2] = dist
            self.state[i*2 + 1] = color

        self.state[len(self.state)-1] = self.agent.pos.y;

        self.info["height"] = self.agent.pos.y

        self.winOb[0].checkAI()
        return [self.state,self.reward,self.done,self.info]
        

if __name__ == "__main__":
    currentGameEnv = GameEnv();
    while True:
        currentGameEnv.step();
        currentGameEnv.render();
