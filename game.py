import pygame
import random
from navsystem import opposite, world, sense_lidar, sense_bush, move, argmax, p

# Константы
TILE_SIZE = 40
WIDTH, HEIGHT = len(world[0]) * TILE_SIZE, len(world) * TILE_SIZE

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Navigation Simulation")

# Загрузка и масштабирование спрайтов
SPRITES = {name: pygame.transform.scale(pygame.image.load(f'{name}.png'), (TILE_SIZE, TILE_SIZE))
           for name in ['empty', 'wall', 'bush']}
player_sprite = pygame.transform.scale(pygame.image.load('player.png'), (TILE_SIZE, TILE_SIZE))
ghost_sprite = pygame.transform.scale(pygame.image.load('ghost.png'), (TILE_SIZE, TILE_SIZE))

# Настройки шрифта
font = pygame.font.SysFont(None, 20)

# Начальные параметры
real = (1, 1)
prediction = argmax(p)
orientation = (0, 0)


while (world[real[0]][real[1]] == 'wall'):
    real = (real[0]+1, real[1]+1)

# Соответствие направлений и углов поворота
ORIENTATION_ANGLE = {
    (-1, 0): 90,    # Вверх
    (1, 0): 270,   # Вниз
    (0, -1): 180,   # Влево
    (0, 1): 0    # Вправо
}
player_angle = 0

# Основной цикл
running = True
while running:
    screen.fill((0, 0, 0))
    
        # Отображение игрока и "призрака"
    screen.blit(pygame.transform.rotate(player_sprite, player_angle), (real[1] * TILE_SIZE, real[0] * TILE_SIZE))
    screen.blit(pygame.transform.rotate(ghost_sprite, player_angle), (prediction[1] * TILE_SIZE, prediction[0] * TILE_SIZE))
    
    
    # Отрисовка карты и вероятностей
    for i, row in enumerate(world):
        for j, cell in enumerate(row):
            screen.blit(SPRITES.get(cell, SPRITES['empty']), (j * TILE_SIZE, i * TILE_SIZE))
            text_surf = font.render(f"{p[i][j]:.3f}", True, (255, 255, 255))
            screen.blit(text_surf, text_surf.get_rect(center=(j * TILE_SIZE + TILE_SIZE // 2, i * TILE_SIZE + TILE_SIZE // 2)))
    

    pygame.display.flip()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            move_direction = {
                pygame.K_w: (-1, 0), pygame.K_s: (1, 0),
                pygame.K_a: (0, -1), pygame.K_d: (0, 1)
            }.get(event.key, (0, 0))
            
            if move_direction != (0, 0):
                orientation = move_direction
                player_angle = ORIENTATION_ANGLE[orientation]
                new_real = ((real[0] + orientation[0]) % len(world), (real[1] + orientation[1]) % len(world[0]))
                
                if world[new_real[0]][new_real[1]] != 'wall':
                    real = new_real
                    p = move(p, orientation)
                    prediction = argmax(p)
            
            elif event.key == pygame.K_c:  # Лидар
                forward_pos = [real[0] + orientation[0], real[1] + orientation[1]]
                forward2_pos = [real[0] + orientation[0]*2, real[1] + orientation[1]*2]
                
                if world[forward_pos[0]][forward_pos[1]] == 'wall' and random.random() < 0.8:
                    p = sense_lidar(p, 'wall', orientation)
                elif world[forward2_pos[0]][forward2_pos[1]] == 'wall' and random.random() < 0.5:
                    p = sense_lidar(p, 'wall', orientation)
                else:
                    p = sense_lidar(p, 'empty', orientation)
                
                prediction = argmax(p)
                print(real, orientation)
            
            elif event.key == pygame.K_b:  # Датчик растительности
                p = sense_bush(p, world[real[0]][real[1]] if random.random() < 0.7 else opposite(world[real[0]][real[1]], 'bush'))
                prediction = argmax(p)

pygame.quit()
