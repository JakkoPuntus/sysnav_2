import sys
from image_to_map import image_to_map

distribution_type = sys.argv[1] if len(sys.argv) > 1 else "uniform"
map_location = sys.argv[2] if len(sys.argv) > 2 else 'map.png'

from hex import ABSOLUTE_DIRECTIONS, hex_next_diag_cell

def add_wall_around_world(world):
    """
    Добавляет стену ('wall') по всему контуру мира.
    """
    rows = len(world)
    cols = len(world[0]) if rows > 0 else 0

    # Проходим по всем строкам
    for i in range(rows):
        # Первый и последний столбец в каждой строке
        world[i][0] = 'wall'
        world[i][cols - 1] = 'wall'

    # Проходим по всем столбцам (кроме первого и последнего, так как они уже обработаны)
    for j in range(1, cols - 1):
        # Первая и последняя строка в каждом столбце
        world[0][j] = 'wall'
        world[rows - 1][j] = 'wall'

    return world

world = image_to_map(map_location)

height = len(world)
width = len(world[0])

# world = add_wall_around_world(world)


def initialize_distribution(distribution_type):
    if distribution_type == "uniform":
        # Равномерное распределение
        free_cells = sum(1 for row in world for cell in row if cell != 'wall')
        return [[0.0 if world[i][j] == 'wall' else 1.0 / free_cells for j in range(width)] for i in range(height)]

    elif distribution_type == "single":
        p = [[0.0 for _ in range(width)] for _ in range(height)]
        p[1][1] = 1.0
        return p
    else:
        return [[1.0 / (height * width) for _ in range(width)] for _ in range(height)]

p = initialize_distribution(distribution_type)

measurements = ['empty', 'wall', 'bush']

pHitTwoBlocks_lidar = 0.5
pHitOneBlock_lidar = 0.8
pFalsePositive_lidar = 0.1
realSensorError_lidar = 0.8

pHit_bush = 0.7
pMiss_bush = 0.2
realSensorError_bush = 0.7

pExact = 0.8
pOvershoot = 0.1
pUndershoot = 0.1

orientation = (0, 1)

def normalize_p(p_new):
    total_prob = sum(sum(row) for row in p_new)
    if total_prob > 0:
        p_new = [[p_ij / total_prob for p_ij in row] for row in p_new]

    return p_new

def sense_lidar(p, Z, orientation):
    rows, cols = len(p), len(p[0])
    p_new = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for i in range(rows):
        for j in range(cols):
            if world[i][j] == 'wall':  # Робот не может быть в стене
                continue
            
            # Определяем координаты с учётом тороидальной топологии
            one_block_i = (i + orientation[0]) % rows
            one_block_j = (j + orientation[1]) % cols
            two_block_i = (i + 2 * orientation[0]) % rows
            two_block_j = (j + 2 * orientation[1]) % cols

            # Проверяем соответствие измерения лидара
            hitOneBlock = (Z == world[one_block_i][one_block_j])
            hitTwoBlocks = (Z == world[two_block_i][two_block_j])
            
            if i == 1 and j == 6:
                print(orientation, Z, hitOneBlock, hitTwoBlocks, one_block_i, one_block_j)
                

            # Обновляем вероятность
            if hitOneBlock:
                p_new[i][j] = p[i][j] * pHitOneBlock_lidar
            elif hitTwoBlocks:
                p_new[i][j] = p[i][j] * pHitTwoBlocks_lidar
            else:
                p_new[i][j] = p[i][j] * pFalsePositive_lidar

    # Нормализация вероятностей
    return normalize_p(p_new)

def sense_lidar_hex(p, Z, orientation):
    """
    Вариация работы лидара для шестиугольной сетки
    """
    rows, cols = len(p), len(p[0])
    p_new = [[0 for _ in range(cols)] for _ in range(rows)]
    
    for i in range(rows):
        for j in range(cols):
            if world[i][j] == 'wall':  # Робот не может быть в стене
                continue
            
            # Определяем координаты с учётом тороидальной топологии
            
            horizontal, vertical = ABSOLUTE_DIRECTIONS[orientation]
            if vertical != 0:
                forward_pos = hex_next_diag_cell(horizontal, vertical, (i, j))
                forward2_pos = hex_next_diag_cell(horizontal, vertical+1, (i, j))
            else:
                forward_pos = [i, j + horizontal]
                forward2_pos = [i, j + horizontal*2]
            
            one_block_i  = forward_pos[0] % rows
            one_block_j = forward_pos[1] % cols
            two_block_i = forward2_pos[0] % rows
            two_block_j = forward2_pos[1] % cols

            # Проверяем соответствие измерения лидара
            hitOneBlock = (Z == world[one_block_i][one_block_j])
            hitTwoBlocks = (Z == world[two_block_i][two_block_j])

            # Обновляем вероятность
            if hitOneBlock:
                p_new[i][j] = p[i][j] * pHitOneBlock_lidar
            elif hitTwoBlocks:
                p_new[i][j] = p[i][j] * pHitTwoBlocks_lidar
            else:
                p_new[i][j] = p[i][j] * pFalsePositive_lidar

    # Нормализация вероятностей
    return normalize_p(p_new)





def sense_bush(p, Z):
    p_new = [[0.0 for _ in range(len(p[0]))] for _ in range(len(p))]
    
    for i in range(len(p)):
        for j in range(len(p[i])):
            hit = (Z == world[i][j])
            p_new[i][j] = p[i][j] * (hit * pHit_bush + (1 - hit) * pMiss_bush)
    
    s = sum(map(sum, p_new))
    return [[x / s for x in row] for row in p_new]

def move(p, U):
    p_new = [[0.0 for _ in range(len(p[0]))] for _ in range(len(p))]
    print(U)
    for i in range(len(p)):
        for j in range(len(p[i])):
            if world[i][j] == 'wall':
                continue
            
            s = pExact * p[(i - U[0]) % len(p)][(j - U[1]) % len(p[i])]
            s += pOvershoot * p[(i - U[0]*2) % len(p)][(j - U[1]*2) % len(p[i])]
            s += pUndershoot * p[(i + U[0]*2) % len(p)][(j + U[1]*2) % len(p[i])]
            p_new[i][j] = s
    
    return normalize_p(p_new)

def argmax(values):
    max_val = max(map(max, values))
    for i in range(len(values)):
        for j in range(len(values[i])):
            if values[i][j] == max_val:
                return (i, j)
    return (0, 0)


def opposite(point, sensor):

    if sensor == "bush":
        
        return 'bush' if point == 'empty' else 'bush'
    
    if sensor == 'lidar':
        return 'wall' if point == 'empty' else 'wall'

