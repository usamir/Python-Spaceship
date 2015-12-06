# program template for Spaceship
try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import math
import random

# globals for user interface
width = 800
height = 600
score = 0
hiscore = 0
lives = 3
time = 0
started = False
MAX_NUM_OF_ROCKS = 12
MIN_SPAWN_DISTANCE = 150

class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_images = [None] * 3
asteroid_images[0] = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")
asteroid_images[1] = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_brown.png")
asteroid_images[2] = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blend.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")
EXPLOSION_DIM = 64
# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0]-q[0])**2+(p[1]-q[1])**2)

# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.forward = angle_to_vector(self.angle)
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)
        
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        self.pos[1] = (self.pos[1] + self.vel[1]) % height 
       
      # update velocity
        if self.thrust:
            self.forward = angle_to_vector(self.angle)
            self.vel[0] += self.forward[0] * .1
            self.vel[1] += self.forward[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99
            
    def rotate_right(self):
        self.angle_vel += .05
        
    def rotate_left(self):
        self.angle_vel -= .05
        
    def stop_rotate(self):
        self.angle_vel = 0
     
    def thrust_start(self):
        self.thrust = True
        ship_thrust_sound.rewind()
        ship_thrust_sound.play()
        
    def thrust_stop(self):
        self.thrust = False
        ship_thrust_sound.pause()
        
    def shoot(self):
        global missile_group
        tip_position_x = self.pos[0] + (self.radius * math.cos(self.angle)) 
        tip_position_y = self.pos[1] + (self.radius * math.sin(self.angle))

        missle_vel_x = self.vel[0] + (6 * math.cos(self.angle))
        missle_vel_y = self.vel[1] + (6 * math.sin(self.angle))

        a_missile = Sprite([tip_position_x, tip_position_y], [missle_vel_x, missle_vel_y], self.angle, self.angle_vel, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
        
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
        if self.animated:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0] * self.age, self.image_center[1]], self.image_size, self.pos, self.image_size)
            self.age += 1
            
    def update(self):
        self.angle += self.angle_vel
 
        self.pos[0] = (self.pos[0] + self.vel[0]) % width
        self.pos[1] = (self.pos[1] + self.vel[1]) % height
        
        self.age += 1
        if self.age < self.lifespan:
            return True
        else:
            return False
        
    def get_velocity(self):
        return self.vel
    
    def get_angle(self):
        return self.angle
    
    def get_angle_vel(self):
        return self.angle_vel
    
    def get_position(self):
        return self.pos
    
    def get_radius(self):
        return self.radius
    
    def collide(self, other_sprite):
        if dist(self.get_position(), other_sprite.get_position()) < (self.get_radius() + other_sprite.get_radius()):
            return True
        else:
            return False
    
def draw(canvas):
    global time, lives, score, started, hiscore
        
    # animiate background
    time += 1
    center = debris_info.get_center()
    size = debris_info.get_size()
    wtime = (time / 8) % center[0]
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [width/2, height/2], [width, height])
    canvas.draw_image(debris_image, [center[0]-wtime, center[1]], [size[0]-2*wtime, size[1]], 
                                [width/2+1.25*wtime, height/2], [width-2.5*wtime, height])
    canvas.draw_image(debris_image, [size[0]-wtime, center[1]], [2*wtime, size[1]], 
                                [1.25*wtime, height/2], [2.5*wtime, height])

    # draw ship and sprites
    my_ship.draw(canvas)
    
    # update ship and sprites
    my_ship.update()
    process_sprite_group(canvas, rock_group)
    process_sprite_group(canvas, missile_group)
    process_sprite_group(canvas, explosion_group)

    # draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Score", [680, 50], 22, "White")
    canvas.draw_text("HiScore", [680, 120], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, "White")
    canvas.draw_text(str(score), [680, 80], 22, "White")
    canvas.draw_text(str(hiscore), [680, 150], 22, "White")
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [width/2, height/2], 
                          splash_info.get_size())
        
        
    # check if ship collide with rocks
    if group_collide(rock_group, my_ship) > 0:
        lives -= 1
        
    # check missile/rocks collisions
    if group_group_collide(rock_group, missile_group) > 0:
        score += 1
    hiscore = max(score, hiscore)
    
    if lives == 0:
        stop_game()
           
# key handlers to control ship 
def keydown(key):
    if key in inputs and inputs[key][0]:
        inputs[key][0]()

def keyup(key):
    if key in inputs and inputs[key][1]:
        inputs[key][1]()

# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, timer
    center = [width / 2, height / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        start_game()
    
    
def random_point():
    return [random.randrange(0, width), random.randrange(0, height)]

def scaled_point(point, scalar):
    return [x * scalar for x in point]

# timer handler that spawns a rock    
def rock_spawner():
    if len(rock_group) < MAX_NUM_OF_ROCKS:
        rock_pos = random_point()
        while dist(rock_pos, my_ship.get_position()) < MIN_SPAWN_DISTANCE:
            rock_pos = random_point()
        rock_vel = scaled_point([random.random() * .6 - .3,
                                 random.random() * .6 - .3], 
                                 score / 5 + 1)
        rock_avel = random.random() * .2 - .1
        rock_group.add(Sprite(rock_pos, rock_vel, 0, rock_avel,
                       random.choice(asteroid_images), asteroid_info))
        
# helper function for processing sprite group
def process_sprite_group(canvas, sprite_group):
    for sprite in list(sprite_group):
        sprite.draw(canvas)
        if sprite.update() == False:
            sprite_group.remove(sprite)
            
# helper function for checking collides between ship and sprites               
def group_collide(sprite_group, other_sprite):
    global explosion_group
    num_collisons = 0
    for sprite in list(sprite_group):
        if sprite.collide(other_sprite):
            sprite_group.remove(sprite)
            num_collisons += 1
            explosion = Sprite(sprite.get_position(), sprite.get_velocity(), sprite.get_angle(), sprite.get_angle_vel(), explosion_image, explosion_info, explosion_sound)
            explosion_group.add(explosion)
    return num_collisons 

# helper function for checking collides between group of sprites, example rocks and missiles
def group_group_collide(sprite_group1, sprite_group2):
    num_collisons = 0
    for sprite in list(sprite_group1):
        if group_collide(sprite_group2, sprite):
            sprite_group1.remove(sprite)
            num_collisons += 1
    return num_collisons

def start_game():
    global lives, score, started
    lives = 3
    score = 0
    soundtrack.play()
    timer.start()
    started = True

def stop_game():
    global rock_group, started
    soundtrack.rewind()
    timer.stop()
    rock_group = set()
    started = False

# initialize frame
frame = simplegui.create_frame("Asteroids", width, height)

# initialize ship and two sprites
my_ship = Ship([width / 2, height / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])
explosion_group = set([])
inputs = dict((simplegui.KEY_MAP[k], v) for (k, v) in {
    "left":  (my_ship.rotate_left,    my_ship.stop_rotate),
    "right": (my_ship.rotate_right,   my_ship.stop_rotate),
    "up":    (my_ship.thrust_start, my_ship.thrust_stop),
    "space": (None,                 my_ship.shoot)
}.items())
    
# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_keyup_handler(keyup)

timer = simplegui.create_timer(1000.0, rock_spawner)
         
# get things rolling
frame.start()


