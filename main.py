import pygame
from pygame import transform
import PyParticles, PyButtons
import random, os
from math import pi
# Check for android module and does stuff
try:
    import android
except ImportError:
    android = None

# Android stuff
TIMEREVENT = pygame.USEREVENT

if android:
    android.init()
    android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
pygame.init()

#(WIDTH, HEIGHT) = (800, 1280)
#(WIDTH, HEIGHT) = (720, 1280)
(WIDTH, HEIGHT) = (480, 800)
L_BALLSIZE = int(HEIGHT/30)
M_BALLSIZE = int(HEIGHT/50)
S_BALLSIZE = int(HEIGHT/90)
basePath = os.path.dirname(__file__)
p1ballPath = os.path.join(basePath, "red_ball.png")
p2ballPath = os.path.join(basePath, "green_ball.png")
dmgballPath = os.path.join(basePath, "damaged_ball.png")
P1_BALL_IMG = pygame.image.load(p1ballPath)
P2_BALL_IMG = pygame.image.load(p2ballPath)
DMG_BALL_IMG = pygame.image.load(dmgballPath)
BALL_HITPOINTS = 50
WINDOW_TITLE = "LOLOL, like OLO, but it's not OLO"
FPS = 60
FONT_FILE = "./font.ttf"
OSD_FONT_FILE = "./osd_font.ttf"
FONT = pygame.font.Font(FONT_FILE, 15)
OSD_FONT = pygame.font.Font(OSD_FONT_FILE, int(HEIGHT/15))
P1_BALL_COLOUR = (220,40,40)
P2_BALL_COLOUR = (40,220,40)
P1_WEAK_COLOUR = (220,110,110)
P2_WEAK_COLOUR = (110,220,110)
P1_AREA_COLOUR = (40,30,30)
P2_AREA_COLOUR = (30,40,30)
ACTIVE_AREA_COLOUR = (50,50,50)
TEXT_COLOUR = (100,200,100)
COURT_COLOUR = (200,200,200)
P_AREA_SIZE = HEIGHT/6
RANDOM_PLAYER_START = True
BALL_SIZES = ["s", "m", "l"]

pygame.display.set_caption(WINDOW_TITLE)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# PHYSICS
universe = PyParticles.Environment((WIDTH, HEIGHT))
universe.colour = (30,30,30)
universe.addFunctions(['move','bounce','collide','drag'])
universe.mass_of_air = 0.04
universe.acceleration = (pi, 0.15)
universe.global_elasticity = False

#Button
restart_button = PyButtons.Button()
quit_button = PyButtons.Button()

# CLUTTER
def spawnBall(p, s):
    spawn = True
    if s == "s":
        size = S_BALLSIZE
        mass = 20
        elasticity = 1
    elif s == "m":
        size = M_BALLSIZE
        mass = 40
        elasticity = 0.9
    else:
        size = L_BALLSIZE
        mass = 70
        elasticity = 0.8
    if p == 1:
        player = 1
        colour = P1_BALL_COLOUR
        y = int(P_AREA_SIZE/2)
        if universe.p1_lives == 0:
            spawn = False
        else:
            universe.p1_lives -= 1
    elif p == 2:
        player = 2
        colour = P2_BALL_COLOUR
        y = int(HEIGHT - P_AREA_SIZE/2)
        if universe.p2_lives == 0:
            spawn = False
        else:
            universe.p2_lives -= 1

    if spawn:
        universe.addParticles(mass=mass, player=player, hp=BALL_HITPOINTS, size=size, speed=0, colour=colour, x=WIDTH/2, y=y, elasticity=elasticity)

def restartRound():
    p1, p2 = False, False
    if not len(universe.particles) == 0:
        del universe.particles[:]
    if RANDOM_PLAYER_START:
        coinflip = random.randrange(1,3)
        print ("Player %i begins!" % coinflip)
        if coinflip == 1:
            p1 = True
        else:
            p2 = True
    else:
        p1 = True
    if p1:
        spawnBall(1, random.choice(BALL_SIZES))
    else:
        spawnBall(2, random.choice(BALL_SIZES))

    return p1, p2

p1_turn, p2_turn = restartRound()

p1_score, p2_score, p1_balls, p2_balls, balls_in_motion = [], [], [], [], []
clock = pygame.time.Clock()
real_fps = FPS
paused = False
debug_mode = False
selected_particle = None
running = True
# MAIN LOOP LOL
while running:

    # Android-specific:
    if android:
        if android.check_pause():
            android.wait_for_resume()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            #if not selected_particle == None:
            #    real_fps = FPS / 3
            (mouseX, mouseY) = pygame.mouse.get_pos()
            selected_particle = universe.findParticle(mouseX, mouseY)
            if paused:
                if restart_button.pressed(pygame.mouse.get_pos()):
                    del p1_balls[:]
                    del p2_balls[:]
                    p1_turn, p2_turn = restartRound()
                    del p1_score[:]
                    del p2_score[:]
                    del balls_in_motion[:]
                    universe.p1_lives, universe.p2_lives = 10, 10
                    paused = False
                elif quit_button.pressed(pygame.mouse.get_pos()):
                    running = False
                elif mouseY > (HEIGHT/5)*2 and mouseY < (HEIGHT/5)*3:
                    paused = False
            else:
                if mouseY > (HEIGHT/5)*2 and mouseY < (HEIGHT/5)*3:
                    paused = True
        elif event.type == pygame.MOUSEBUTTONUP:
            real_fps = FPS
            selected_particle = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                del p1_balls[:]
                del p2_balls[:]
                p1_turn, p2_turn = restartRound()
                del p1_score[:]
                del p2_score[:]
                del balls_in_motion[:]
                universe.p1_lives, universe.p2_lives = 10, 10
            elif event.key == pygame.K_d:
                debug_mode = (True, False)[debug_mode]
            elif event.key == pygame.K_t:
                p1_turn = (True, False)[p1_turn]
                p2_turn = (True, False)[p2_turn]
            elif event.key == pygame.K_SPACE:
                paused = (True, False)[paused]
                selected_particle = None
            elif event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_1:
                spawnBall(1, random.choice(BALL_SIZES))
            elif event.key == pygame.K_2:
                spawnBall(2, random.choice(BALL_SIZES))


    # Checks if balls are inside players area, and allows for them to be moved.

    if not paused:
        if selected_particle:
            if selected_particle.y < P_AREA_SIZE and p1_turn:
                selected_particle.mouseMove(pygame.mouse.get_pos())
            elif selected_particle.y > HEIGHT-P_AREA_SIZE and p2_turn:
                selected_particle.mouseMove(pygame.mouse.get_pos())

        universe.update()

    screen.fill(universe.colour)

    # Drawing colors for areas where players score
    pygame.draw.rect(screen, P2_AREA_COLOUR, (0, P_AREA_SIZE, WIDTH, HEIGHT/2-P_AREA_SIZE), 0)
    pygame.draw.rect(screen, P1_AREA_COLOUR, (0, HEIGHT/2, WIDTH, HEIGHT/2-P_AREA_SIZE), 0)

    # Drawing the play area:
    pygame.draw.line(screen, COURT_COLOUR, (0, HEIGHT/2), (WIDTH, HEIGHT/2))
    # These are the player areas on both sides:
    pygame.draw.line(screen, COURT_COLOUR, (0, HEIGHT-(P_AREA_SIZE+1)), (WIDTH, HEIGHT-(P_AREA_SIZE+1)))
    pygame.draw.line(screen, COURT_COLOUR, (0, P_AREA_SIZE+1), (WIDTH, P_AREA_SIZE+1))
    # Highlighting active player's area
    if p1_turn:
        pygame.draw.rect(screen, ACTIVE_AREA_COLOUR, (0, 0, WIDTH, P_AREA_SIZE), 0)
    elif p2_turn:
        pygame.draw.rect(screen, ACTIVE_AREA_COLOUR, (0, HEIGHT-(P_AREA_SIZE-1), WIDTH, P_AREA_SIZE), 0)

    # PARTICLE LOGIC AND DRAWING
    for p in universe.particles:
        if p.player == 1:
            p.colour = (P1_BALL_COLOUR[0], P1_BALL_COLOUR[1]+(BALL_HITPOINTS-p.hitpoints)*2, P1_BALL_COLOUR[2]+(BALL_HITPOINTS-p.hitpoints)*2)
        elif p.player == 2:
            p.colour = (P2_BALL_COLOUR[0]+(BALL_HITPOINTS-p.hitpoints)*2, P2_BALL_COLOUR[1], P2_BALL_COLOUR[2]+(BALL_HITPOINTS-p.hitpoints)*2)

        ###### Draws the balls ######
        P2_BALL_COLOUR = (40,220,40)
        P1_WEAK_COLOUR = (220,110,110)
        #pygame.draw.circle(screen, p.colour, (int(p.x), int(p.y)), p.size, 0)
        if p.player == 1:
        	scaled_ball_img = pygame.transform.scale(P1_BALL_IMG, (p.size*2, p.size*2))
        elif p.player == 2:
        	scaled_ball_img = pygame.transform.scale(P2_BALL_IMG, (p.size*2, p.size*2))

        scaled_by_hp = int(p.size-(p.size/(BALL_HITPOINTS/p.hitpoints)))
        scaled_dmg_ball_img = pygame.transform.scale(DMG_BALL_IMG, (scaled_by_hp*2, scaled_by_hp*2))

        screen.blit(scaled_ball_img,(int(p.x)-p.size, int(p.y)-p.size))
        screen.blit(scaled_dmg_ball_img, (int(p.x)-scaled_by_hp, int(p.y)-scaled_by_hp))
        #############################

        # Score and turn
        if p.player == 1:
            if p.y < HEIGHT-P_AREA_SIZE and p.y > HEIGHT/2:    # Player 1
                if not p in p1_score:
                    p1_score.append(p)
            else:
                if p in p1_score:
                    p1_score.remove(p)

        if p.player == 2:
            if p.y > P_AREA_SIZE and p.y < HEIGHT/2:    # Player 2
                if not p in p2_score:
                    p2_score.append(p)
            else:
                if p in p2_score:
                    p2_score.remove(p)

        # CHECK FOR BALLS WITHIN PLAYER AREAS
        if p.y < P_AREA_SIZE:   # Player 1
            if not p in p1_balls:
                p1_balls.append(p)
        else:
            if p in p1_balls:
                p1_balls.remove(p)
        if p.y > HEIGHT-P_AREA_SIZE:   # Player 2
            if not p in p2_balls:
                p2_balls.append(p)
        else:
            if p in p2_balls:
                p2_balls.remove(p)


        # Removes the ball if it dies
        if p.hitpoints <= 0:
            if p in p1_score:
                p1_score.remove(p)
            if p in p1_balls:
                p1_balls.remove(p)
            if p in p2_score:
                p2_score.remove(p)
            if p in p2_balls:
                p2_balls.remove(p)
            if p in balls_in_motion:
                balls_in_motion.remove(p)
            p.speed = 0
            universe.particles.remove(p)

        # Changes turn and spawns ball if no balls are moving and none is available
        if not paused:
            if p1_turn:
                if not len(balls_in_motion) > 0 and len(p1_balls) == 0:
                    p1_turn = False
                    p2_turn = True
                    if universe.p2_lives > 0:
                        spawnBall(2, random.choice(BALL_SIZES))
                        p2_balls.append(p)
            elif p2_turn:
                if not len(balls_in_motion) > 0 and len(p2_balls) == 0:
                    p1_turn = True
                    p2_turn = False
                    if universe.p1_lives > 0:
                        spawnBall(1, random.choice(BALL_SIZES))
                        p1_balls.append(p)

        # Ends the round if no lives, no balls available and no ball is moving:
        if not len(balls_in_motion) > 0 and len(p1_balls) == 0 and len(p2_balls) == 0 and universe.p1_lives == 0 and universe.p2_lives == 0:
            p1_turn, p2_turn = False, False
            paused = True

        # Make a list of balls that are in motion
        if p.speed > 0.03:
            if not p in balls_in_motion:
                balls_in_motion.append(p)
        else:
            if p in balls_in_motion:
                balls_in_motion.remove(p)

    # RESTART BUTTON
    if paused:
        restart_button.create_button(screen, (107,142,35), WIDTH/2-155, HEIGHT/2-30, 150, 60, 0, "New Round", (255,255,255))
        quit_button.create_button(screen, (142,35,35), WIDTH/2+5, HEIGHT/2-30, 150, 60, 0, "Quit LOLOL", (255,255,255))

    clock.tick(real_fps)
    fps_label = FONT.render("FPS: %i" % round(clock.get_fps()), 1, TEXT_COLOUR)
    particles_on_screen = FONT.render("Particles: %i" % len(universe.particles), 1, TEXT_COLOUR)
    p1_balls_label = FONT.render("P1 balls: %i" % len(p1_balls), 1, TEXT_COLOUR)
    p2_balls_label = FONT.render("P2 balls: %i" % len(p2_balls), 1, TEXT_COLOUR)
    p1_lives_label = FONT.render("P1 lives: %i" % universe.p1_lives, 1, TEXT_COLOUR)
    p2_lives_label = FONT.render("P2 lives: %i" % universe.p2_lives, 1, TEXT_COLOUR)
    score_label1 = OSD_FONT.render("{0}".format(len(p1_score), len(p2_score)), 1, COURT_COLOUR)
    score_label2 = OSD_FONT.render("{1}".format(len(p1_score), len(p2_score)), 1, COURT_COLOUR)

    if not paused:
        score_label1 = pygame.transform.rotozoom(score_label1, 180, 1)
        screen.blit(score_label1, (WIDTH-WIDTH/8, 0))
        screen.blit(score_label2, (20, int(HEIGHT-HEIGHT/15)))

    if paused:
        screen.blit(score_label1, (WIDTH/15, HEIGHT/2-HEIGHT/15))
        screen.blit(score_label2, (WIDTH/15, HEIGHT/2))

    if debug_mode:
        screen.blit(fps_label, (10, 10))
        screen.blit(particles_on_screen, (10, 35))
        screen.blit(p1_balls_label, (10, 60))
        screen.blit(p2_balls_label, (10, 85))
        screen.blit(p1_lives_label, (10, 110))
        screen.blit(p2_lives_label, (10, 135))

    pygame.display.flip()