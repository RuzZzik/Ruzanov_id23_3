import tkinter as tk
import math

window = tk.Tk() #создаем окно
window.title("Окошко") #задаем имя всплывающего окна
window.geometry("600x600") #размер всплывающего окна

canvas = tk.Canvas(window, bg="white", width=600, height=600) #задаем параметры для холста, где будет нарисован круг
canvas.pack() #pack - размещает холст в окне

radius = 200 #создаем окружность с радиусом 200 и задаем кооринаты ее центра
x_center = 300
y_center = 300
canvas.create_oval(x_center - radius, y_center - radius, x_center + radius, y_center + radius, outline="black", width=2) #рисуем окружность по заданным коордианатам, outline - цвет линии окружности и параметр ширины линии

#создаем точку на окружности
angle = 0 #инициализируем угол 0 градусов, затем вычисляем координаты x_point и y_point для точки на окружности
x_point = x_center + radius * math.cos(math.radians(angle))
y_point = y_center + radius * math.sin(math.radians(angle))
point_id = canvas.create_oval(x_point - 5, y_point - 5, x_point + 5, y_point + 5, fill="red") #создаем маленькую точку

#задаем переменную скорости и направления
speed = 0.2  #пикселей в секунду
direction = 1  #направление - 1 по часовой, -1 против часовой

#обновляем положение точки
def update_point():
    global angle, x_point, y_point #используем глобал для переменных вне функции
    angle += speed * direction #изменяем угол, добавляя к нему speed * direction, что позволяет изменять направление
    x_point = x_center + radius * math.cos(math.radians(angle)) #пересчет координат x_point, y_point на основе новых координат угла
    y_point = y_center + radius * math.sin(math.radians(angle))
    canvas.coords(point_id, x_point - 5, y_point - 5, x_point + 5, y_point + 5)  #обновляем координаты точки на холсте с помощью метода coords(), чтобы переместить ее в новое положение
    window.after(10, update_point)  #after() использует задержку, которую мы можем изменить, в данном случае 10мс и вызывает функцию update_point() снова, создавая эффект анимации

update_point() #вызываем функцию для начала анимации

window.mainloop() #запускаем цикл, метод mainloop() запускает главный цикл приложения, который поддерживает окно открытым и обрабатывает события






