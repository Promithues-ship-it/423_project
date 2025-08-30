from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Window and grid settings
WINDOW_WIDTH, WINDOW_HEIGHT = 960, 720
GRID_LENGTH = 600

# Camera system
camera_pos = (0, 500, 500)
first_person_view = False
fovY = 120

# Player and spaceship
player_pos = [0, 200, 0]
gun_angle = 0
player_max_health = 100
player_health = 100
shield_active = False

# Power-ups
HEALTH_POWERUP = 0
WEAPON_POWERUP = 1
SPEED_POWERUP = 2
SHIELD_POWERUP = 3
MAX_POWERUPS = 5
POWERUP_LIFETIME_FRAMES = 900
power_ups = []  # [x, y, z, type, rotation, creation_frame]

# Speed booster
player_speed = 6
speed_boost_active = False
speed_boost_end_frame = 0
frame_counter = 0

# Game stats
score = 0
level = 1
score_multiplier = 1
total_points = 0

# Enemies for mini-map
enemies = []
enemy_spaceships = []
boss_enemies = []

GAME_Z_LEVEL = 0

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_health_bar():
    bar_width = 250
    bar_height = 25
    bar_x = 15
    bar_y = WINDOW_HEIGHT - 200

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    health_ratio = player_health / player_max_health
    if health_ratio > 0.6:
        glColor3f(0, 1, 0)
    elif health_ratio > 0.3:
        glColor3f(1, 1, 0)
    else:
        glColor3f(1, 0, 0)

    glBegin(GL_QUADS)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width * health_ratio, bar_y)
    glVertex2f(bar_x + bar_width * health_ratio, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()

    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    glVertex2f(bar_x, bar_y)
    glVertex2f(bar_x + bar_width, bar_y)
    glVertex2f(bar_x + bar_width, bar_y + bar_height)
    glVertex2f(bar_x, bar_y + bar_height)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_mini_map():
    map_size = 150
    map_x = WINDOW_WIDTH - map_size - 10
    map_y = 10

    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor4f(0, 0, 0, 0.7)
    glEnable(GL_BLEND)
    glBegin(GL_QUADS)
    glVertex2f(map_x, map_y)
    glVertex2f(map_x + map_size, map_y)
    glVertex2f(map_x + map_size, map_y + map_size)
    glVertex2f(map_x, map_y + map_size)
    glEnd()

    glColor3f(0, 1, 1)
    glBegin(GL_LINES)
    glVertex2f(map_x, map_y)
    glVertex2f(map_x + map_size, map_y)
    glVertex2f(map_x + map_size, map_y + map_size)
    glVertex2f(map_x, map_y + map_size)
    glEnd()

    scale = map_size / (GRID_LENGTH * 2)
    center_x = map_x + map_size / 2
    center_y = map_y + map_size / 2

    glColor3f(0, 1, 0)
    glPointSize(8)
    glBegin(GL_POINTS)
    glVertex2f(center_x, center_y)
    glEnd()

    px = center_x + player_pos[0] * scale
    py = center_y + player_pos[1] * scale
    if px >= map_x and px <= map_x + map_size and py >= map_y and py <= map_y + map_size:
        glColor3f(0, 1, 1)
        glPointSize(6)
        glBegin(GL_POINTS)
        glVertex2f(px, py)
        glEnd()

    glColor3f(1, 0, 0)
    glPointSize(4)
    glBegin(GL_POINTS)
    for e in enemies:
        ex = center_x + e[0] * scale
        ey = center_y + e[1] * scale
        if ex >= map_x and ex <= map_x + map_size and ey >= map_y and ey <= map_y + map_size:
            glVertex2f(ex, ey)
    for e in enemy_spaceships:
        ex = center_x + e[0] * scale
        ey = center_y + e[1] * scale
        if ex >= map_x and ex <= map_x + map_size and ey >= map_y and ey <= map_y + map_size:
            glVertex2f(ex, ey)
    for b in boss_enemies:
        ex = center_x + b[0] * scale
        ey = center_y + b[1] * scale
        if ex >= map_x and ex <= map_x + map_size and ey >= map_y and ey <= map_y + map_size:
            glVertex2f(ex, ey)
    glEnd()

    glDisable(GL_BLEND)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def draw_power_up(x, y, z, power_type, rotation):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 1, 1, 0)
    if power_type == HEALTH_POWERUP:
        glColor3f(1, 0, 0)
        glutSolidCube(25)
        glColor3f(1, 1, 1)
        glPushMatrix()
        glScalef(0.2, 1.8, 0.2)
        glutSolidCube(18)
        glPopMatrix()
        glPushMatrix()
        glScalef(1.8, 0.2, 0.2)
        glutSolidCube(18)
        glPopMatrix()
    elif power_type == WEAPON_POWERUP:
        glColor3f(1, 1, 0)
        glutSolidCube(25)
        glColor3f(1, 0.5, 0)
        for i in range(4):
            glPushMatrix()
            glRotatef(i * 90, 0, 0, 1)
            glTranslatef(15, 0, 0)
            glutSolidSphere(3, 8, 8)
            glPopMatrix()
    elif power_type == SPEED_POWERUP:
        glColor3f(0, 0.5, 1)
        glutSolidCube(25)
        glColor3f(0.5, 0.8, 1)
        glPushMatrix()
        glScalef(0.3, 2, 0.3)
        glutSolidCube(20)
        glPopMatrix()
    elif power_type == SHIELD_POWERUP:
        glColor3f(1, 0, 1)
        glutSolidCube(25)
        glColor3f(0.7, 0, 1)
        glutSolidSphere(18, 12, 12)
    glPopMatrix()

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 2500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if first_person_view:
        look_x = player_pos[0] + 100 * math.cos(math.radians(gun_angle))
        look_y = player_pos[1] + 100 * math.sin(math.radians(gun_angle))
        look_z = player_pos[2]
        pos_x = player_pos[0] - 25 * math.cos(math.radians(gun_angle))
        pos_y = player_pos[1] - 25 * math.sin(math.radians(gun_angle))
        pos_z = player_pos[2] + 40
        gluLookAt(pos_x, pos_y, pos_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        x, y, z = camera_pos
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)

def keyboardListener(key, x, y):
    global first_person_view, speed_boost_active, speed_boost_end_frame, frame_counter
    if key == b'v':
        first_person_view = not first_person_view
    elif key == b'c':
        if not speed_boost_active:
            speed_boost_active = True
            speed_boost_end_frame = frame_counter + 360  # 6 seconds

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.0, 0.0, 0.15, 1.0)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()
    glEnable(GL_DEPTH_TEST)
    draw_health_bar()
    draw_mini_map()
    glColor3f(1, 1, 0.8)
    draw_text(15, WINDOW_HEIGHT - 35, f"SCORE: {score}  |  LEVEL: {level}  |  MULTIPLIER: x{score_multiplier}", GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(1, 1, 0)
    draw_text(15, WINDOW_HEIGHT - 65, f"*** TOTAL CAREER POINTS: {total_points + score} ***", GLUT_BITMAP_TIMES_ROMAN_24)
    glColor3f(0.8, 1, 0.8)
    draw_text(15, WINDOW_HEIGHT - 90, f"HEALTH: {int(player_health)}/{player_max_health}")
    glColor3f(0.8, 0.8, 1)
    effects_text = ""
    if speed_boost_active:
        effects_text += "SPEED BOOST ACTIVE"
    if shield_active:
        effects_text += "  |  SHIELD ACTIVE"
    draw_text(15, WINDOW_HEIGHT - 115, effects_text)
    glColor3f(1, 0.8, 1)
    draw_text(15, WINDOW_HEIGHT - 140, f"{len(power_ups)}/{MAX_POWERUPS} Power-ups")
    for p in power_ups:
        draw_power_up(p[0], p[1], GAME_Z_LEVEL, p[3], p[4])
    glutSwapBuffers()