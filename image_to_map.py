from PIL import Image

def image_to_map(image_path):
    # Загружаем изображение
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()
    
    # Определяем размеры
    width, height = img.size
    world_map = []
    
    # Цвета для объектов
    COLOR_WALL = (100, 100, 100)  # Серый (#646464)
    COLOR_BUSH = (0, 255, 0)      # Зеленый
    COLOR_EMPTY = (255, 255, 255) # Белый

    for y in range(height):
        row = []
        for x in range(width):
            color = pixels[x, y]
            if color == COLOR_WALL:
                row.append("wall")
            elif color == COLOR_BUSH:
                row.append("bush")
            else:
                row.append("empty")
        world_map.append(row)
    
    return world_map

# Пример использования
image_path = "map.png"
world = image_to_map(image_path)

# Выводим карту в консоль
for row in world:
    print(row)
