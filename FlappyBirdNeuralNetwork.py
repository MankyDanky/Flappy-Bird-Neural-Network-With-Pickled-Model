#Imorts
import pygame
import neat
import pickle
import os
import random
pygame.font.init()

#Generation Variable
GEN = 0

#Define Window Size
WIN_WIDTH = 500
WIN_HEIGHT = 800

#Import Images And Create Array For Bird Imgs
BIRD_IMGS = [pygame.image.load(os.path.join("imgs", "bird1.png")),
             pygame.image.load(os.path.join("imgs", "bird2.png")),
             pygame.image.load(os.path.join("imgs", "bird3.png"))]
PIPE_IMG = pygame.image.load(os.path.join("imgs", "pipe.png"))
BASE_IMG = pygame.image.load(os.path.join("imgs", "base.png"))
BG_IMG = pygame.image.load(os.path.join("imgs", "bg.png"))
PROGRAM_ICON = pygame.image.load(os.path.join("imgs", "programIcon.png"))

#Import Font
STAT_FONT = pygame.font.Font("Hardpixel.OTF", 30)

#Configure Pygame Window
pygame.display.set_icon(PROGRAM_ICON)
pygame.display.set_caption("Flappy Bird Neural Network")

#Define Bird Class
class Bird:
    #Define Constants
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    #Init Func
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    #Jump Func
    def jump(self):
        self.vel = -5
        self.tick_count = 0
        self.height = self.y

    #Move Func
    def move(self):
        self.tick_count += 1

        d = self.vel*self.tick_count + self.tick_count**1.8

        if d > 16:
            d = 16

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    #Draw Func
    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    #Mask Func
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

#Define Pipe Class
class Pipe:
    #Define Constants
    GAP = 200
    VEL = 5

    #Init Func
    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        #Get Images For Both Top And Bottom Pipe
        self.PIPE_BOTTOM = PIPE_IMG
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)

        self.passed = False
        self.set_height()

    #Set Height Fun
    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    #Move Func
    def move(self):
        self.x -= self.VEL

    #Draw Func
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    #Collide Func
    def collide(self, bird):
        #Get Masks
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        #Get Distance Between Bird And Pipes
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        #Check For Pixel Overlap
        t_point = bird_mask.overlap(top_mask, top_offset)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)

        #Return True Or False According To Above
        if t_point or b_point:
            return True
        return False

#Define Base Class
class Base:
    #Define Constants
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    #Init Func
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    #Move Func
    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    #Draw Func
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

#Draw Window Func
def draw_window(win, birds, pipes, base, score, gen):
    #Draw Background Img
    win.blit(BG_IMG, (0,0))

    #Call Draw Funcs
    for pipe in pipes:
        pipe.draw(win)

    for bird in birds:
        bird.draw(win)

    base.draw(win)

    #Draw Score
    scoreText = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(scoreText, (WIN_WIDTH - 10 - scoreText.get_width(), 10))

    #Draw Gen
    genText = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(genText, (10, 10))

    #Update Display
    pygame.display.update()

#Def Main Func
def main(genomes, config):
    #Increase Generation Every Time We Run Main
    global GEN
    GEN += 1

    #Initiliaze Neat Components, Base, Pipes, Window, and Clock
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    #Initiliaze Score
    score = 0

    #Game Loop
    run = True
    while run:
        #Set Tickrate
        clock.tick(60)
        for event in pygame.event.get():
            #Check If X Was Clicked
            if event.type == pygame.QUIT:
                # Quit If X Was Clicked
                run = False
                pygame.quit()
                quit()

        #Create An Index Of The Next Pipe
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            #End Game If Generation Dies
            run = False
            break

        # Move Birds
        for x, bird in enumerate(birds):
            bird.move()
            #Give Fitness Points For Staying Alive
            ge[x].fitness += 0.1

            #Feed Input Nodes And Read Output
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            #Check if Output Thinks We Should Jump
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        #Loop Through Each Pipe
        for pipe in pipes:
            #Loop Through Each Bird
            for x, bird in enumerate(birds):
                #Check For Collision
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                #Check If The Bird Passed The Pipe
                if not pipe.passed and pipe.x + pipe.PIPE_TOP.get_width() < bird.x:
                    pipe.passed = True
                    add_pipe = True
            #Check To Remove Pipe
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            #Call Pipe Move Func
            pipe.move()
        #Add Pipe
        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5

            pipes.append(Pipe(600))
        #Remove Pipe
        for r in rem:
            pipes.remove(r)
        #Check If Birds Hit Floor
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        #Call Base Move Func
        base.move()
        #Draw The Screen
        draw_window(win, birds, pipes, base, score, GEN)

#NEAT Config
def run(config_path):
    #Configure Config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    #Unpickle Winner
    with open("winner.pkl", "rb") as f:
        genome = pickle.load(f)
    #Save Genome To Use As Parameter
    genomes = [(1, genome)]
    #Call Main With Genome
    main(genomes, config)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)