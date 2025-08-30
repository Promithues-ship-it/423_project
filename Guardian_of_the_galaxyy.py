from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Game stats
score = 0
total_points = 0
score_multiplier = 1
level = 1
last_level_up_score = 0
frame_counter = 0

# Resource management
resources = []  # [x, y, z, rotation, creation_frame]
MAX_RESOURCES = 5
MIN_RESOURCES = 2
RESOURCE_LIFETIME_FRAMES = 300  # 5 seconds at 60 FPS
GAME_Z_LEVEL = 0

# Player variables
player_pos = [0, 200, 0]
player_max_health = 100
player_health = 100

GRID_LENGTH = 600

def update_resources():
    global resources, score, total_points, score_multiplier, frame_counter

    # Remove resources that have expired (older than 5 seconds)
    resources[:] = [r for r in resources if frame_counter - r[4] <= RESOURCE_LIFETIME_FRAMES]
    
    for r in resources[:]:
        r[3] += 5  # rotation
        
        dist = math.sqrt((r[0] - player_pos[0])**2 + (r[1] - player_pos[1])**2)
        if dist < 35:
            resources.remove(r)
            points = 8 * score_multiplier
            score += points

def manage_resources():
    """Control golden crystal spawning."""
    global resources, frame_counter
    
    # Ensure a minimum number of resources are always available
    if len(resources) < MIN_RESOURCES:
        for _ in range(MIN_RESOURCES - len(resources)):
            rx = random.uniform(-GRID_LENGTH//2, GRID_LENGTH//2)
            ry = random.uniform(-GRID_LENGTH//2, GRID_LENGTH//2)
            resources.append([rx, ry, GAME_Z_LEVEL, 0, frame_counter])
    
    # Spawn new resources if below the maximum limit
    if len(resources) < MAX_RESOURCES and random.random() < 0.1:
        rx = random.uniform(-GRID_LENGTH//2, GRID_LENGTH//2)
        ry = random.uniform(-GRID_LENGTH//2, GRID_LENGTH//2)
        resources.append([rx, ry, GAME_Z_LEVEL, 0, frame_counter])

def update_level_progression():
    global score, level, last_level_up_score, score_multiplier, player_health, player_max_health

    # Level up every 15 points
    if score - last_level_up_score >= 15:
        level += 1
        last_level_up_score = score
        score_multiplier = level
        player_health = min(player_max_health, player_health + 20)

def idle():
    global frame_counter
    frame_counter += 1

    # Time-based difficulty: call progression and resource management
    update_level_progression()
    manage_resources()
    update_resources()

# Example usage in a game loop:
# while True:
#     idle()