#ВАРИАНТ 12
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from matplotlib.animation import FuncAnimation

def calculate_velocity(P, h, rho):
    g = 9.81
    return np.sqrt((2 * P / rho) + (2 * g * h))

def update(frame):
    global water_position, water_level, max_height, animation_running

    if water_level >= max_height:
        animation_running = False
        return

    ax.clear()
    ax.set_xlim(-2, 3)
    ax.set_ylim(-1, max_height + 2)

    ax.plot([-1.5, 1], [0, 0], color="black", lw=8)
    ax.plot([1, 1], [0, max_height], color="black", lw=8)

    ax.bar(2, water_level, width=1, color="blue", align="center", label="Резервуар")
    ax.plot([1.5, 2.5], [max_height, max_height], color="black", lw=8)

    if water_position[0] < 1 and water_position[1] == 0:
        water_position[0] += velocity * 0.02
    elif water_position[0] >= 1 and water_position[1] < max_height:
        water_position[1] += velocity * 0.02
        water_level += velocity * 0.01
    elif water_position[1] >= max_height:
        water_position = [-1.5, 0]

    if water_position[1] == 0:
        ax.scatter(water_position[0], 0, color="blue", s=100)
    else:
        ax.scatter(1, water_position[1], color="blue", s=100)

    ax.set_title("Водичка через трубу")
    ax.legend()

def start_animation():
    global velocity, water_position, water_level, ani, max_height, animation_running

    try:
        rho = float(rho_slider.get())
        if rho < 500 or rho > 1500:
            raise ValueError("Плотность должна быть от 500 до 1500 кг/м³")

        max_height = float(height_combobox.get())
        if max_height < 1 or max_height > 10:
            raise ValueError("Высота должна быть от 1 до 10 м")

        P = float(pressure_slider.get())
        if P < 10000 or P > 500000:
            raise ValueError("Давление должно быть от 10000 до 500000 Па")
    except ValueError as e:
        result_label["text"] = f"Ошибка: {e}"
        return

    velocity = calculate_velocity(P, max_height, rho)
    result_label["text"] = f"Скорость потока воды: {velocity:.2f} м/с"

    water_position[0], water_position[1] = -1.5, 0
    water_level = 0
    animation_running = True
    ani = FuncAnimation(fig, update, frames=200, interval=50, blit=False)
    canvas.draw()

def reset():
    global ani, water_position, water_level, max_height, animation_running
    if ani:
        ani.event_source.stop()
    water_position = [-1.5, 0]
    water_level = 0
    animation_running = False
    ax.clear()
    ax.set_xlim(-2, 3)
    ax.set_ylim(-1, max_height + 2)
    ax.set_title("Движение воды через трубы в резервуар")
    canvas.draw()
    result_label["text"] = ""

root = tk.Tk()
root.title("Симуляция работы водяного насоса")

rho_label = tk.Label(root, text="Плотность воды (кг/м³):")
rho_label.pack()
rho_slider = ttk.Scale(root, from_=500, to=1500, orient="horizontal")
rho_slider.set(1000)
rho_slider.pack()

height_label = tk.Label(root, text="Высота подъема воды (м):")
height_label.pack()
height_combobox = ttk.Combobox(root, values=list(range(1, 11)))
height_combobox.set(1)
height_combobox.pack()

pressure_label = tk.Label(root, text="Давление воды в системе (Па):")
pressure_label.pack()
pressure_slider = ttk.Scale(root, from_=10000, to=500000, orient="horizontal")
pressure_slider.set(100000)
pressure_slider.pack()

start_button = tk.Button(root, text="Запуск анимации", command=start_animation)
start_button.pack()

reset_button = tk.Button(root, text="Сброс", command=reset)
reset_button.pack()

result_label = tk.Label(root, text="")
result_label.pack()

fig = Figure(figsize=(6, 6))
ax = fig.add_subplot(111)
ax.set_xlim(-2, 3)
ax.set_ylim(-1, 12)
ax.set_title("Движение воды через трубы в резервуар")

canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

velocity = 0
water_position = [-1.5, 0]
water_level = 0
max_height = 10
animation_running = False
ani = None

root.mainloop()