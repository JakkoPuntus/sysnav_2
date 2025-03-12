import pygame
import math
import random
from navsystem import opposite, sense_lidar_hex, world, sense_bush, move, argmax, p
from hex import hex_next_diag_cell, ABSOLUTE_DIRECTIONS
# Параметры окна и поля
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 780
GRID_WIDTH = 16
GRID_HEIGHT = 16
HEX_RADIUS = 30

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Navigation Simulation")
clock = pygame.time.Clock()

# Инициализация геймпада
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    joystick = None

# Начальные параметры
real = (1, 1)
prediction = argmax(p)
orientation = (0, 1)
absolute_orientation = 0

# Флаги для предотвращения многократного срабатывания
key_pressed = False
joystick_moved = False

# Цвета
COLORS = {
    "empty": (0, 0, 0),
    "wall": (144, 70, 64),
    "bush": (169, 224, 64),
    "player": (0, 0, 255),
    "prediction": (255, 0, 0)
}




player_sprite = pygame.image.load('player.png')  
player_sprite = pygame.transform.scale(player_sprite, (HEX_RADIUS, HEX_RADIUS)) 

ghost_sprite = pygame.image.load('ghost.png')  
ghost_sprite = pygame.transform.scale(ghost_sprite, (HEX_RADIUS, HEX_RADIUS)) 



# Функция для вычисления центра шестиугольника
def hex_center(i, j):
    x = (i + 0.5 * (j % 2)) * (3 ** 0.5) * HEX_RADIUS
    y = j * 1.5 * HEX_RADIUS
    return int(x + HEX_RADIUS), int(y + HEX_RADIUS)



# Функция для рисования шестиугольника
def draw_hexagon(surface, x, y, color, text):
    points = [
        (x, y - HEX_RADIUS),
        (x + HEX_RADIUS * math.cos(math.pi / 6), y - HEX_RADIUS / 2),
        (x + HEX_RADIUS * math.cos(math.pi / 6), y + HEX_RADIUS / 2),
        (x, y + HEX_RADIUS),
        (x - HEX_RADIUS * math.cos(math.pi / 6), y + HEX_RADIUS / 2),
        (x - HEX_RADIUS * math.cos(math.pi / 6), y - HEX_RADIUS / 2)
    ]
    pygame.draw.polygon(surface, color, points, 0)
    pygame.draw.polygon(surface, (0, 0, 0), points, 1)
    font = pygame.font.Font(None, 20)
    text_surface = font.render(f"{text:.3f}", True, (255, 255, 255))
    surface.blit(text_surface, (x - 10, y - 10))

def draw_player(surface, x, y, orientation, sprite):
    
    angle_map = {
        0: 0,      #вправо
        1: 60,     #вправо-вверх
        2: 120,    #влево-вверх
        3: 180,    #влево
        4: 240,     #влево-вниз
        5: 300,     #вправо-вниз
    }

    # Рассчитываем угол на основе ориентации
    angle = angle_map.get(orientation, 0)  # по умолчанию 0° (вправо)

    # Поворот спрайта
    rotated_sprite = pygame.transform.rotate(sprite, angle)
    
    # Получаем новый центр для спрайта
    new_rect = rotated_sprite.get_rect(center=(x, y))
    
    # Отображаем спрайт
    surface.blit(rotated_sprite, new_rect.topleft)

# Функция отрисовки
def draw_grid():
    screen.fill(COLORS['empty'])
    for i in range(GRID_WIDTH):
        for j in range(GRID_HEIGHT):
            x, y = hex_center(i, j)
            cell_type = world[j % len(world)][i % len(world[0])]
            draw_hexagon(screen, x, y, COLORS[cell_type], p[j % len(p)][i % len(p[0])])
    
    # Отрисовка игрока и предсказания
    x_real, y_real = hex_center(real[1], real[0])
    x_pred, y_pred = hex_center(prediction[1], prediction[0])
    draw_player(screen, x_pred, y_pred, absolute_orientation, ghost_sprite)
    draw_player(screen, x_real, y_real, absolute_orientation, player_sprite)

# Обработчик ввода
def handle_input():
    global real, prediction, p, orientation, key_pressed, joystick_moved, absolute_orientation
    keys = pygame.key.get_pressed()
    move_direction = None
    
    if not key_pressed:
        if keys[pygame.K_w]:
            move_direction = (-1, 0 if real[0] % 2 == 0 else 1)
            absolute_orientation = 1
        if keys[pygame.K_s]: 
            move_direction = (1, 0 if real[0] % 2 == 0 else 1)
            absolute_orientation = 5
        if keys[pygame.K_a]:
            move_direction = (0, -1)
            absolute_orientation = 3
        if keys[pygame.K_d]:
            move_direction = (0, 1)
            absolute_orientation = 0
        if keys[pygame.K_q]:
            move_direction = (-1, -1 if real[0] % 2 == 0 else 0)
            absolute_orientation = 2
        if keys[pygame.K_e]:
            move_direction = (1, -1 if real[0] % 2 == 0 else 0)
            absolute_orientation = 4
        if keys[pygame.K_c]:
            sense_lidar()
        if keys[pygame.K_b]:
            p = sense_bush(p, world[real[0]][real[1]] if random.random() < 0.7 else opposite(world[real[0]][real[1]], 'bush'))
    
    if joystick and not joystick_moved:
        axis_x = joystick.get_axis(0)
        axis_y = joystick.get_axis(1)
                
        # Пороговое значение для определения наклона стика
        threshold = 0.5

        # Определяем направление
        if abs(axis_x) > threshold or abs(axis_y) > threshold:
            if axis_x > threshold:  # Вправо
                if axis_y < -threshold:  # Вправо-вверх
                    move_direction = (-1, 0 if real[0] % 2 == 0 else 1)
                    absolute_orientation = 1
                elif axis_y > threshold:  # Вправо-вниз
                    move_direction = (1, 0 if real[0] % 2 == 0 else 1)
                    absolute_orientation = 5
                else:  # Просто вправо
                    move_direction = (0, 1)
                    absolute_orientation = 0
            elif axis_x < -threshold:  # Влево
                if axis_y < -threshold:  # Влево-вверх
                    move_direction = (-1, -1 if real[0] % 2 == 0 else 0)
                    absolute_orientation = 2
                elif axis_y > threshold:  # Влево-вниз
                    move_direction = (1, -1 if real[0] % 2 == 0 else 0)
                    absolute_orientation = 4
                else:  # Просто влево
                    move_direction = (0, -1)
                    absolute_orientation = 3

        joystick_moved = True
        
    if joystick:
        if joystick.get_button(0):  # Кнопка A
            sense_lidar()
        if joystick.get_button(1):  # Кнопка B
            p = sense_bush(p, world[real[0]][real[1]] if random.random() < 0.7 else opposite(world[real[0]][real[1]], 'bush'))

    
    if move_direction:
        new_real = ((real[0] + move_direction[0]) % len(world), (real[1] + move_direction[1]) % len(world[real[0]]))
        if (real[0] + move_direction[0]) > len(world) and len(world) % 2 == 1:
            new_real[1] += 1
        orientation = move_direction
        if world[new_real[0]][new_real[1]] != 'wall':
            real = new_real
            p = move(p, move_direction)
            prediction = argmax(p)
            key_pressed = True
            joystick_moved = True

def sense_lidar():
    global p
    horizontal, vertical = ABSOLUTE_DIRECTIONS[absolute_orientation]
    if vertical != 0:
        forward_pos = hex_next_diag_cell(horizontal, vertical, real)
        forward2_pos = hex_next_diag_cell(horizontal, vertical, real)
    else:
        forward_pos = [real[0], real[1] + horizontal]
        forward2_pos = [real[0], real[1] + horizontal*2]
                
    if world[forward_pos[0]][forward_pos[1]] == 'wall' and random.random() < 0.8:
        p = sense_lidar_hex(p, 'wall', absolute_orientation)
    elif world[forward2_pos[0]][forward2_pos[1]] == 'wall' and random.random() < 0.5:
        p = sense_lidar_hex(p, 'wall', absolute_orientation)
    else:
        p = sense_lidar_hex(p, 'empty', absolute_orientation)
    
# Главный цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            key_pressed = False
        if event.type == pygame.JOYAXISMOTION:
            joystick_moved = False    
            
    
    handle_input()
    draw_grid()
    pygame.display.flip()
    clock.tick(30)

pygame.quit()