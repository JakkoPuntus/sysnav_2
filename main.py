import tkinter as tk
from tkinter import filedialog
import subprocess

def run_game(game_script, distribution_type, map_location):
    """Запускает выбранную игру с заданным типом распределения и картой."""
    # Передаем выбранное распределение и путь к карте в качестве параметров
    subprocess.run(['python', game_script, distribution_type, map_location])

root = tk.Tk()
root.title("Выбор игры")

root.geometry("400x300")

# Переменная для хранения выбранного типа распределения
distribution_var = tk.StringVar(value="uniform")

# Переменная для хранения пути к выбранной карте
map_location_var = tk.StringVar()

def select_map():
    """Функция для выбора карты."""
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        map_location_var.set(file_path)

def start_game(game_script):
    """Функция для старта игры с выбранным распределением и картой."""
    map_location = map_location_var.get()
    if not map_location:
        map_location = "map.png"  # Укажите путь к карте по умолчанию, если карта не выбрана
    run_game(game_script, distribution_var.get(), map_location)

# Кнопка для игры game.py
btn_game = tk.Button(root, text="Запустить Систему навигации", command=lambda: start_game('game.py'))
btn_game.pack(pady=10)

# Кнопка для игры hex_game.py
btn_hex_game = tk.Button(root, text="Запустить Систему навигации в шестиугольной сетке", command=lambda: start_game('hex_game.py'))
btn_hex_game.pack(pady=10)

label = tk.Label(root, text="Выберите распределение:")
label.pack(pady=10)

radio_uniform = tk.Radiobutton(root, text="Равномерное", variable=distribution_var, value="uniform")
radio_uniform.pack()

radio_single = tk.Radiobutton(root, text="Однозначное (единица в начале)", variable=distribution_var, value="single")
radio_single.pack()

# Кнопка для выбора карты
btn_select_map = tk.Button(root, text="Выбрать карту", command=select_map)
btn_select_map.pack(pady=10)

# Метка для отображения выбранной карты
map_label = tk.Label(root, textvariable=map_location_var)
map_label.pack(pady=10)

root.mainloop()