"""
Набор методов и констант для работы в шестиугольной сетке
"""



ABSOLUTE_DIRECTIONS = {
    0: (1, 0),
    1: (1, 1),
    2: (-1, 1),
    3: (-1, 0),
    4: (-1, -1),
    5: (1, 1),
}


def hex_next_diag_cell(horizontal, vertical, position):
    """
    horizontal = [-1, 1] - движение влево или вправо
    vertical : int - движение вверх на число клеток
    
    например:
    horizontal = 1, vertical = 3 — смещение на 3 клетки вправо-вверх
    """
    position = list(position)
    
    if horizontal == 0:
        raise ValueError
    
    if vertical == 0:
        return position
    
    if position[0] % 2 == 0:
        if vertical > 0:
            vertical -= 1
            position[0] -= 1
            position[1] -= horizontal < 0
        else:
            vertical += 1
            position[0] += 1
            position[1] -= horizontal < 0
            
    else:
        if vertical > 0:
            vertical -= 1
            position[0] -= 1
            position[1] += horizontal > 0
        else:
            vertical += 1
            position[0] += 1
            position[1] += horizontal > 0
            
    return hex_next_diag_cell(horizontal, vertical, position)


if __name__ == '__main__':
    # Пример использования:
    new_cell = hex_next_diag_cell(1, 2, (2, 0))
    print(new_cell)  # (0, 1)
