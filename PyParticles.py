#### MOST OF THE CREDITS OF THE PHYSICS MUST GO TO PETER COLLINRIDGE:
####            http://www.petercollingridge.co.uk/
####                            ty vry much
import math, random
try:
    import android
except ImportError:
    android = None

VIBRATE = True
SOUND = True

if SOUND:
    try:
        import pygame.mixer as mixer
    except ImportError:
        import android.mixer as mixer

    mixer.pre_init(44100, -16, 2, 2048)
    mixer.init()
    BOP_SOUND = mixer.Sound('./sound/bop.ogg')
    DEATH_SOUND = mixer.Sound('./sound/death.ogg')

def addVectors(v1, v2):
    """ Returns the sum of two vectors """
    
    (angle1, length1) = (v1[0], v1[1])
    (angle2, length2) = (v2[0], v2[1])
    x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
    
    angle  = 0.5 * math.pi - math.atan2(y, x)
    length = math.hypot(x, y)

    return (angle, length)

def combine(p1, p2):
    if math.hypot(p1.x - p2.x, p1.y - p2.y) < p1.size + p2.size:
        total_mass = p1.mass + p2.mass
        p1.x = (p1.x*p1.mass + p2.x*p2.mass)/total_mass
        p1.y = (p1.y*p1.mass + p2.y*p2.mass)/total_mass
        (p1.angle, p1.speed) = addVectors((p1.angle, p1.speed*p1.mass/total_mass), (p2.angle, p2.speed*p2.mass/total_mass))
        p1.speed *= (p1.elasticity*p2.elasticity)
        p1.mass += p2.mass
        p1.collide_with = p2

def collide(p1, p2):
    """ Tests whether two particles overlap
        If they do, make them bounce, i.e. update their angle, speed and position """
    
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    
    dist = math.hypot(dx, dy)
    if dist < p1.size + p2.size:
        angle = math.atan2(dy, dx) + 0.5 * math.pi
        if p1.mass == p2.mass:
            p1.mass += 1
        total_mass = p1.mass + p2.mass
        (p1angle, p1speed) = addVectors((p1.angle, p1.speed*(p1.mass-p2.mass)/total_mass), (angle, 2*p2.speed*p2.mass/total_mass))
        (p2angle, p2speed) = addVectors((p2.angle, p2.speed*(p2.mass-p1.mass)/total_mass), (angle+math.pi, 2*p1.speed*p1.mass/total_mass))
        (p2.angle, p2.speed, p1.angle, p1.speed) = (p2angle, p2speed, p1angle, p1speed)

        elasticity = p2.elasticity * p1.elasticity
        total_speed = (p1.speed + p2.speed)

        p1.hitpoints -= elasticity*2
        p2.hitpoints -= elasticity*2
        p1.speed *= elasticity
        p2.speed *= elasticity

        overlap = 0.5*(p1.size + p2.size - dist+1)
        p1.x += math.sin(angle)*overlap
        p1.y -= math.cos(angle)*overlap
        p2.x -= math.sin(angle)*overlap
        p2.y += math.cos(angle)*overlap
        ### VIBRATION
        if VIBRATE and p1.vibrate and p2.vibrate:
            if android:
                android.vibrate(0.05)
        if SOUND and p1.sound and p2.sound:
            if p1.hitpoints <= 0 or p2.hitpoints <= 0:
                DEATH_SOUND.play()
            if not mixer.get_busy():
                vol = float((total_speed*2)/100)
                if vol > 100:
                    vol = 100
                BOP_SOUND.set_volume(vol)
                BOP_SOUND.play()

class Particle:
    """ A circular object with a velocity, size and mass """
    
    def __init__(self, pos, size, mass=1):
        self.x = pos[0]
        self.y = pos[1]
        self.size = size
        self.colour = (0, 0, 255)
        self.thickness = 0
        self.speed = 0
        self.angle = 0
        self.mass = mass
        self.drag = 1
        self.elasticity = 0.9
        self.sound = True
        self.vibrate = True

    def move(self):
        """ Update position based on speed, angle """
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed

    def experienceDrag(self):
        self.speed *= self.drag
        if self.speed < 0.03:
            self.speed = 0

    def mouseMove(self, pos):
        """ Change angle and speed to move towards a given point """
        
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        self.angle = 0.5*math.pi + math.atan2(dy, dx)
        self.speed = math.hypot(dx, dy) * 0.1
        
    def accelerate(self, vector):
        """ Change angle and speed by a given vector """
        (self.angle, self.speed) = addVectors((self.angle, self.speed), vector)
        
    def attract(self, other):
        """" Change velocity based on gravatational attraction between two particle"""
        
        dx = (self.x - other.x)
        dy = (self.y - other.y)
        dist  = math.hypot(dx, dy)
        
        if dist < self.size + other.size:
            return True

        theta = math.atan2(dy, dx)
        force = 0.1 * self.mass * other.mass / dist**2
        self.accelerate((theta - 0.5 * math.pi, force/self.mass))
        other.accelerate((theta + 0.5 * math.pi, force/other.mass))

class Spring:
    def __init__(self, p1, p2, length=50, strength=0.5):
        self.p1 = p1
        self.p2 = p2
        self.length = length
        self.strength = strength
    
    def update(self):
        dx = self.p1.x - self.p2.x
        dy = self.p1.y - self.p2.y
        dist = math.hypot(dx, dy)
        theta = math.atan2(dy, dx)
        force = (self.length - dist) * self.strength
        
        self.p1.accelerate((theta + 0.5 * math.pi, force/self.p1.mass))
        self.p2.accelerate((theta - 0.5 * math.pi, force/self.p2.mass))

class Environment:
    """ Defines the boundary of a simulation and its properties """
    
    def __init__(self, dimensions):
        self.width = dimensions[0]
        self.height = dimensions[1]
        self.particles = []
        self.springs = []
        
        self.colour = (255,255,255)
        self.mass_of_air = 0.2
        self.global_elasticity = True
        self.elasticity = 0.75
        self.acceleration = (0,0)
        self.player = 0
        self.p2_lives, self.p1_lives = 8, 8
        
        self.particle_functions1 = []
        self.particle_functions2 = []
        self.function_dict = {
        'move': (1, lambda p: p.move()),
        'drag': (1, lambda p: p.experienceDrag()),
        'bounce': (1, lambda p: self.bounce(p)),
        'accelerate': (1, lambda p: p.accelerate(self.acceleration)),
        'collide': (2, lambda p1, p2: collide(p1, p2)),
        'combine': (2, lambda p1, p2: combine(p1, p2)),
        'attract': (2, lambda p1, p2: p1.attract(p2))}
        
    def addFunctions(self, function_list):
        for func in function_list:
            (n, f) = self.function_dict.get(func, (-1, None))
            if n == 1:
                self.particle_functions1.append(f)
            elif n == 2:
                self.particle_functions2.append(f)
            else:
                print ("No such function: %s" % f)

    def addParticles(self, n=1, **kargs):
        """ Add n particles with properties given by keyword arguments """
        
        for i in range(n):
            size = kargs.get('size', random.randint(10, 20))
            mass = kargs.get('mass', random.randint(100, 10000))
            x = kargs.get('x', random.uniform(size, self.width - size))
            y = kargs.get('y', random.uniform(size, self.height - size))

            particle = Particle((x, y), size, mass)
            particle.hitpoints = kargs.get('hp', 100)
            particle.speed = kargs.get('speed', random.random())
            particle.angle = kargs.get('angle', random.uniform(0, math.pi*2))
            particle.colour = kargs.get('colour', (0, 0, 255))
            particle.elasticity = kargs.get('elasticity', self.elasticity)
            particle.player = kargs.get('player', self.player)
            particle.drag = (particle.mass/(particle.mass + self.mass_of_air)) ** particle.size

            self.particles.append(particle)

    def addSpring(self, p1, p2, length=50, strength=0.5):
        """ Add a spring between particles p1 and p2 """
        self.springs.append(Spring(self.particles[p1], self.particles[p2], length, strength))

    def update(self):
        """  Moves particles and tests for collisions with the walls and each other """

        for i, particle in enumerate(self.particles, 1):
            for f in self.particle_functions1:
                f(particle)
            for particle2 in self.particles[i:]:
                for f in self.particle_functions2:
                    f(particle, particle2)
                    
        for spring in self.springs:
            spring.update()

    def bounce(self, particle):
        """ Tests whether a particle has hit the boundary of the environment """
        
        if particle.x > self.width - particle.size:
            particle.x = 2*(self.width - particle.size) - particle.x
            particle.angle = - particle.angle
            if self.global_elasticity:
                particle.speed *= self.elasticity
            else:
                particle.speed *= particle.elasticity

        elif particle.x < particle.size:
            particle.x = 2*particle.size - particle.x
            particle.angle = - particle.angle
            if self.global_elasticity:
                particle.speed *= self.elasticity
            else:
                particle.speed *= particle.elasticity

        if particle.y > self.height - particle.size:
            particle.y = 2*(self.height - particle.size) - particle.y
            particle.angle = math.pi - particle.angle
            if self.global_elasticity:
                particle.speed *= self.elasticity
            else:
                particle.speed *= particle.elasticity

        elif particle.y < particle.size:
            particle.y = 2*particle.size - particle.y
            particle.angle = math.pi - particle.angle
            if self.global_elasticity:
                particle.speed *= self.elasticity
            else:
                particle.speed *= particle.elasticity

    def findParticle(self, x, y):
        """ Returns any particle that occupies position x, y """
        
        for particle in self.particles:
            if math.hypot(particle.x - x, particle.y - y) <= particle.size+20:
                return particle
        return None