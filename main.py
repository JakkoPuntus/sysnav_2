import tkinter as tk
import subprocess

def run_game(game_script, distribution_type):
    """Запускает выбранную игру с заданным типом распределения."""
    # Передаем выбранное распределение в качестве параметра
    subprocess.run(['python', game_script, distribution_type])

root = tk.Tk()
root.title("Выбор игры")

root.geometry("300x250")

# Переменная для хранения выбранного типа распределения
distribution_var = tk.StringVar(value="uniform")

def start_game(game_script):
    """Функция для старта игры с выбранным распределением."""
    run_game(game_script, distribution_var.get())

# кнопка для игры game.py
btn_game = tk.Button(root, text="Запустить Систему навигации", command=lambda: start_game('game.py'))
btn_game.pack(pady=10)

# кнопка для игры hex_game.py
btn_hex_game = tk.Button(root, text="Запустить Систему навигации в шестиугольной сетке", command=lambda: start_game('hex_game.py'))
btn_hex_game.pack(pady=10)

label = tk.Label(root, text="Выберите распределение:")
label.pack(pady=10)

radio_uniform = tk.Radiobutton(root, text="Равномерное", variable=distribution_var, value="uniform")
radio_uniform.pack()

radio_single = tk.Radiobutton(root, text="Однозначное (единица в начале)", variable=distribution_var, value="single")
radio_single.pack()

root.mainloop()
