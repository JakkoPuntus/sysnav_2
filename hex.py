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

def hex_next_diag_cell(horizontal: int, vertical: int, position: tuple[int, int]) -> tuple[int, int]:
    """
    Вычисляет следующую клетку на шестиугольной сетке при диагональном движении.

    Параметры:
    -----------
    horizontal : int
        Направление горизонтального движения: -1 (влево) или 1 (вправо).
    vertical : int
        Количество клеток для движения вверх (положительное) или вниз (отрицательное).
    position : tuple[int, int]
        Текущая позиция на сетке в виде кортежа (строка, столбец).

    Возвращает:
    ------------
    tuple[int, int]
        Новая позиция на сетке после движения.

    Исключения:
    ------------
    ValueError
        Если `horizontal` не равен -1 или 1.
    """
    if horizontal not in {-1, 1}:
        raise ValueError("Параметр `horizontal` должен быть -1 или 1.")

    row, col = position

    while vertical != 0:
        is_even_row = row % 2 == 0

        # Определяем изменение строки и столбца в зависимости от направления
        if vertical > 0:
            row -= 1
            vertical -= 1
            col_offset = -1 if horizontal < 0 else 0
        else:
            row += 1
            vertical += 1
            col_offset = -1 if horizontal < 0 else 0

        # Корректируем столбец для четных и нечетных строк
        if not is_even_row:
            col_offset = 1 if horizontal > 0 else 0

        col += col_offset

    return (row, col)

if __name__ == '__main__':
    # Пример использования:
    new_cell = hex_next_diag_cell(-1, 2, (3, 3))
    print(new_cell)  # (0, 1)
