

1 of 12
(no subject)
External
Spam
Promit Hasan <promitheushasanullah024062002@gmail.com>
Attachments
10:50 AM (0 minutes ago)
to me

This message might be dangerous
Messages like this one were used to steal personal information. Don't click links, download attachments, or reply with personal information.

Looks safe

 One attachment
  •  Scanned by Gmail
Downloading this attachment is disabled. This email has been identified as phishing. If you want to download it and you trust this message, click "Not spam" in the banner above.
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Game objects and player variables
player_pos = [0, 200, 0]
player_max_health = 100
player_health = 100
shield_active = False
shield_end_frame = 0
cheat_mode = False
gun_angle = 0
weapon_level = 1
frame_counter = 0

# Enemy and boss lists
enemies = []  # [x, y, z, size, type]
enemy_spaceships = []  # [x, y, z, health, last_shoot_frame]
boss_enemies = []  # [x, y, z, health, last_shoot_frame, movement_phase]
bullets = []  # [x, y, z, angle, speed]
enemy_bullets = []  # [x, y, z, angle, speed]
explosions = []  # [x, y, z, size, frames_left]

# Healing center
earth_angle = 0
GAME_Z_LEVEL = 0

def draw_healing_center():
    glPushMatrix()
    glTranslatef(0, 0, GAME_Z_LEVEL)
    glColor3f(0, 1, 0)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glRotatef(earth_angle * 2, 0, 0, 1)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 80, 80, 8, 24, 1)
    glPopMatrix()
    glColor3f(0, 0.9, 0)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glRotatef(-earth_angle * 3, 0, 0, 1)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 60, 60, 8, 20, 1)
    glPopMatrix()
    glColor3f(0, 0.8, 0)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glRotatef(earth_angle * 4, 0, 0, 1)
    quadric = gluNewQuadric()
    gluCylinder(quadric, 40, 40, 8, 16, 1)
    glPopMatrix()
    glColor3f(0, 1, 0.5)
    glutSolidSphere(25, 20, 20)
    dist_to_center = math.sqrt(player_pos[0]**2 + player_pos[1]**2)
    if dist_to_center < 150:
        glColor3f(0, 1, 0.7)
        for i in range(12):
            angle = i * 30 + earth_angle * 5
            x = 70 * math.cos(math.radians(angle))
            y = 70 * math.sin(math.radians(angle))
            glPushMatrix()
            glTranslatef(x, y, 15)
            glutSolidSphere(4, 10, 10)
            glPopMatrix()
    glPopMatrix()

def draw_enemy_spaceship(x, y, z, health):
    glPushMatrix()
    glTranslatef(x, y, z)
    health_ratio = health / 30.0
    glColor3f(1, 0.2 + 0.8 * health_ratio, 0.2 + 0.8 * health_ratio)
    glutSolidCube(22)
    glColor3f(0.8, 0, 0)
    glPushMatrix()
    glTranslatef(18, 0, 0)
    glScalef(0.6, 2.5, 0.4)
    glutSolidCube(12)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-18, 0, 0)
    glScalef(0.6, 2.5, 0.4)
    glutSolidCube(12)
    glPopMatrix()
    glColor3f(0.2, 0.2, 1)
    glutSolidSphere(8, 12, 12)
    glPopMatrix()

def draw_boss_enemy(x, y, z, health):
    glPushMatrix()
    glTranslatef(x, y, z)
    health_ratio = health / 150.0
    glColor3f(0.5 + 0.5 * health_ratio, 0, 0.5 + 0.5 * health_ratio)
    glutSolidSphere(45, 24, 24)
    glColor3f(1, 0, 1)
    for i in range(12):
        angle = i * 30 + earth_angle * 3
        glPushMatrix()
        glRotatef(angle, 0, 0, 1)
        glTranslatef(55, 0, 0)
        glScalef(2.5, 0.6, 0.6)
        glutSolidCube(12)
        glPopMatrix()
    glColor3f(1, 0.5, 1)
    glPushMatrix()
    glRotatef(-earth_angle * 5, 0, 0, 1)
    glutSolidSphere(20, 16, 16)
    glPopMatrix()
    glPopMatrix()

def find_closest_enemy():
    min_dist = float('inf')
    closest = None
    for e in enemies:
        dx = e[0] - player_pos[0]
        dy = e[1] - player_pos[1]
        dist = dx*dx + dy*dy
        if dist < min_dist:
            min_dist = dist
            closest = {'x': e[0], 'y': e[1], 'type': 'asteroid'}
    for e in enemy_spaceships:
        dx = e[0] - player_pos[0]
        dy = e[1] - player_pos[1]
        dist = dx*dx + dy*dy
        if dist < min_dist:
            min_dist = dist
            closest = {'x': e[0], 'y': e[1], 'type': 'ship'}
    for b in boss_enemies:
        dx = b[0] - player_pos[0]
        dy = b[1] - player_pos[1]
        dist = dx*dx + dy*dy
        if dist < min_dist:
            min_dist = dist
            closest = {'x': b[0], 'y': b[1], 'type': 'boss'}
    return closest

def update_cheat_mode():
    global gun_angle, frame_counter
    if not cheat_mode:
        return
    closest = find_closest_enemy()
    if closest:
        dx = closest['x'] - player_pos[0]
        dy = closest['y'] - player_pos[1]
        target_angle = math.degrees(math.atan2(dy, dx))
        angle_diff = (target_angle - gun_angle + 180) % 360 - 180
        gun_angle += angle_diff * 0.2
    else:
        gun_angle += 1

def shoot_bullets():
    global bullets
    bx = player_pos[0] + 35 * math.cos(math.radians(gun_angle))
    by = player_pos[1] + 35 * math.sin(math.radians(gun_angle))
    bz = GAME_Z_LEVEL
    if weapon_level == 1:
        bullets.append([bx, by, bz, gun_angle, 15])
    elif weapon_level == 2:
        bullets.append([bx, by, bz, gun_angle, 15])
        bullets.append([bx, by, bz, gun_angle + 12, 15])
        bullets.append([bx, by, bz, gun_angle - 12, 15])
    elif weapon_level == 3:
        for i in range(5):
            angle = gun_angle + (i - 2) * 18
            bullets.append([bx, by, bz, angle, 15])
    elif weapon_level == 4:
        for i in range(7):
            angle = gun_angle + (i - 3) * 22
            bullets.append([bx, by, bz, angle, 15])
    else:
        for i in range(16):
            angle = gun_angle + i * 22.5
            bullets.append([bx, by, bz, angle, 15])

def update_bullets():
    global bullets, enemies, enemy_spaceships, boss_enemies, explosions
    for b in bullets[:]:
        b[0] += b[4] * math.cos(math.radians(b[3]))
        b[1] += b[4] * math.sin(math.radians(b[3]))
        hit = False
        for e in enemies[:]:
            dist = math.sqrt((e[0] - b[0])**2 + (e[1] - b[1])**2)
            if dist < e[3] + 8:
                enemies.remove(e)
                bullets.remove(b)
                explosions.append([e[0], e[1], GAME_Z_LEVEL, e[3] * 1.5, 25])
                hit = True
                break
        if hit:
            continue
        for e in enemy_spaceships[:]:
            dist = math.sqrt((e[0] - b[0])**2 + (e[1] - b[1])**2)
            if dist < 25:
                e[3] -= 8
                bullets.remove(b)
                if e[3] <= 0:
                    enemy_spaceships.remove(e)
                    explosions.append([e[0], e[1], GAME_Z_LEVEL, 35, 30])
                hit = True
                break
        if hit:
            continue
        for boss in boss_enemies[:]:
            dist = math.sqrt((boss[0] - b[0])**2 + (boss[1] - b[1])**2)
            if dist < 50:
                boss[3] -= 3
                bullets.remove(b)
                if boss[3] <= 0:
                    boss_enemies.remove(boss)
                    explosions.append([boss[0], boss[1], GAME_Z_LEVEL, 80, 40])
                hit = True
                break
        if hit:
            continue
        if abs(b[0]) > 700 or abs(b[1]) > 700:
            bullets.remove(b)

def update_enemy_bullets():
    global enemy_bullets, player_health, shield_active
    for b in enemy_bullets[:]:
        b[0] += b[4] * math.cos(math.radians(b[3]))
        b[1] += b[4] * math.sin(math.radians(b[3]))
        dist = math.sqrt((b[0] - player_pos[0])**2 + (b[1] - player_pos[1])**2)
        if dist < 25:
            enemy_bullets.remove(b)
            if not shield_active:
                player_health -= 3
        if abs(b[0]) > 700 or abs(b[1]) > 700:
            enemy_bullets.remove(b)

def update_enemy_spaceships():
    global enemy_spaceships, enemy_bullets, explosions, player_health, shield_active, frame_counter
    for e in enemy_spaceships[:]:
        dx = player_pos[0] - e[0]
        dy = player_pos[1] - e[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            speed = 1.0
            e[0] += (dx / dist) * speed
            e[1] += (dy / dist) * speed
        if dist < 300 and frame_counter - e[4] > 180:
            angle = math.degrees(math.atan2(dy, dx))
            enemy_bullets.append([e[0], e[1], GAME_Z_LEVEL, angle, 4])
            e[4] = frame_counter
        if dist < 30:
            enemy_spaceships.remove(e)
            explosions.append([e[0], e[1], GAME_Z_LEVEL, 35, 30])
            if not shield_active:
                player_health -= 8

def update_boss_enemies():
    global boss_enemies, enemy_bullets, frame_counter
    for b in boss_enemies[:]:
        b[5] += 1
        if b[5] % 360 < 180:
            angle = b[5] * 1
            b[0] = 250 * math.cos(math.radians(angle))
            b[1] = 250 * math.sin(math.radians(angle))
        else:
            dx = player_pos[0] - b[0]
            dy = player_pos[1] - b[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                speed = 0.3
                b[0] += (dx / dist) * speed
                b[1] += (dy / dist) * speed
        if frame_counter - b[4] > 150:
            base_angle = math.degrees(math.atan2(player_pos[1] - b[1], player_pos[0] - b[0]))
            for i in range(5):
                angle = base_angle + (i - 2) * 25
                enemy_bullets.append([b[0], b[1], GAME_Z_LEVEL, angle, 4])
            b[4] = frame_counter

def update_power_ups(power_ups):
    global player_health, weapon_level, shield_active, shield_end_frame, frame_counter
    for p in power_ups[:]:
        p[4] += 4
        dist = math.sqrt((p[0] - player_pos[0])**2 + (p[1] - player_pos[1])**2)
        if dist < 40:
            power_ups.remove(p)
            if p[3] == 0:  # HEALTH_POWERUP
                player_health = min(player_max_health, player_health + 35)
            elif p[3] == 1:  # WEAPON_POWERUP
                weapon_level = min(5, weapon_level + 1)
            elif p[3] == 3:  # SHIELD_POWERUP
                shield_active = True
                shield_end_frame = frame_counter