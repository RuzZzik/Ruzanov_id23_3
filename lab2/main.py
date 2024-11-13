import json
import pygame
import numpy as np

# Константы программы
WIDTH, HEIGHT = 1024, 800  #размеры окна в пикселях
FPS = 60  #частота обновления кадров в секунду

def load_config(filename='config.json'):  #функция загрузки конфигурации
    try:  #пробуем загрузить существующий файл конфигурации
        with open(filename, 'r') as f:  #открываем файл для чтения
            return json.load(f)  #преобразуем JSON в Python-объект
    
    except FileNotFoundError:  #если файл не найден, создаем конфигурацию по умолчанию
        default_config = {
            "waves": [  #параметры для трех волн
                {"amplitude": 20, "period": 50, "offset": 0},    # первая волна
                {"amplitude": 65, "period": 150, "offset": 100}, # вторая волна
                {"amplitude": 30, "period": 80, "offset": 200}   # третья волна
            ],
            "buoys": [  #параметры для трех поплавков
                {"mass": 5, "volume": 0.1, "position": 100, "wave_index": 0, "color": [255,0,0]}, # первый поплавок
                {"mass": 5, "volume": 0.5, "position": 300, "wave_index": 1, "color": [0,255,0]},  # второй поплавок
                {"mass": 5, "volume": 1, "position": 500, "wave_index": 2, "color": [255,165,0]}   # третий поплавок
            ]
        }
        with open(filename, 'w') as f:  #открываем файл для записи
            json.dump(default_config, f, indent=4)  #сохраняем конфигурацию в JSON
        return default_config

def calculate_wave_positions(t, waves):  # функция расчета положения волн
    positions = []  # список для хранения позиций всех волн
    for wave in waves:  #проходимся циклом по каждой волне
        amplitude = wave['amplitude']  #высота волны
        period = wave['period']       #длина волны
        offset = wave['offset']       #смещение волны по вертикали
        x_values = np.arange(0, WIDTH)  #создаем массив x-координат
        #вычисляем y-координаты волны используя синусоиду
        y_values = (HEIGHT // 2 + offset) + amplitude * np.sin((2 * np.pi / period) * (x_values - t * 20))
        positions.append(y_values)  #добавляем координаты в общий список
    return positions

def calculate_buoy_positions(buoys, wave_positions):  #функция расчета положения поплавков
    buoy_positions = []  #список для хранения позиций поплавков
    water_density = 1000.0  #плотность воды в кг/м³
    gravity = 9.81        #ускорение свободного падения в м/с²
    scale_factor = 0.001  #коэффициент масштабирования для визуализации

    for buoy in buoys:  #проходимся циклом по каждому поплавка
        buoy_x = buoy['position']     #получаем x-координату поплавка
        wave_index = buoy['wave_index']  #получаем индекс волны, на которой находится поплавок
        
        #проверяем, что индексы находятся в допустимых пределах
        if wave_index < len(wave_positions) and buoy_x < len(wave_positions[wave_index]):
            wave_y = wave_positions[wave_index][buoy_x]  #y-координата волны в точке поплавка
            mass = buoy['mass']     #масса поплавка
            volume = buoy['volume']  #объем поплавка
            
            weight_force = mass * gravity  #вычисляем силу тяжести
            archimedes_force = water_density * volume * gravity  #вычисляем силу Архимеда
            net_force = archimedes_force - weight_force  #вычисляем результирующую силу
            offset = net_force * scale_factor  #вычисляем смещение
            
            buoy_y = wave_y + offset  #определяем конечную позицию поплавка
            buoy_positions.append(int(buoy_y))  #добавляем позицию в список
        else:
            buoy_positions.append(HEIGHT // 2)  #если что-то пошло не так, ставим по центру
    return buoy_positions
    
def main():  #основная функция программы
    pygame.init()  #инициализируем pygame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))  #создаем окно
    pygame.display.set_caption("SIUUUUUUUU")  #задаем заголовок окна
    clock = pygame.time.Clock()  #создаем объект для управления временем
    
    config = load_config()  #загружаем конфигурацию
    waves = config['waves']  #получаем параметры волн
    buoys = config['buoys']  #получаем параметры поплавков
    
    running = True  #флаг работы программы
    t = 0  #начальное время
    
    while running:  #основной цикл программы
        for event in pygame.event.get():  #обрабатываем события
            if event.type == pygame.QUIT:  #если закрываем окно
                running = False  #завершаем работу
        
        screen.fill((255, 255, 255))  #заливаем экран белым
        
        wave_positions = calculate_wave_positions(t, waves)  #рассчитываем позиции волн
        buoy_positions = calculate_buoy_positions(buoys, wave_positions)  #рассчитываем позиции поплавков
        
        #рисуем волны
        for y_values in wave_positions:  #для каждой волны
            for x in range(WIDTH - 1):  #для каждой x-координаты
                if 0 <= y_values[x] < HEIGHT and 0 <= y_values[x + 1] < HEIGHT:  #проверяем границы
                    pygame.draw.line(screen, (0, 0, 255),(x, y_values[x]), (x + 1, y_values[x + 1])) #рисуем синюю линию
        
        #рисуем поплавки
        for i, buoy in enumerate(buoys):  #для каждого поплавка
            buoy_x = buoy['position']  #получаем x-координату
            buoy_y = buoy_positions[i]  #получаем y-координату
            buoy_color = buoy['color']
            pygame.draw.circle(screen, buoy_color, (buoy_x, buoy_y), 10) #рисуем поплавок на экране в координатах, с радиусом 10 пикселей
        
        pygame.display.flip()  #обновляем экран
        t += 1 / FPS  #увеличиваем время
        clock.tick(FPS)  #поддерживаем частоту кадров
    
    pygame.quit()  #завершаем работу pygame

if __name__ == "__main__":
    main()