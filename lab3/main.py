import math
import json
import random
import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIHorizontalSlider, UITextEntryLine, UILabel, UIWindow

# Настройка окна
WIDTH, HEIGHT = 1280, 1024
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Физ параметры
GRAVITY = 9.81
WATER_DENSITY = 1000
DAMPING = 0.98
WAVE_SPACING = HEIGHT / 5
MAX_VELOCITY = 200
VELOCITY_SCALE = 0.2
BASE_HORIZONTAL_SPEED = 50

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Моделирование волн и буев")
clock = pygame.time.Clock()

manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Класс волны
class Wave:
    def __init__(self, id, amplitude, frequency, phase, speed):
        self.id = id
        self.amplitude = amplitude
        self.frequency = frequency
        self.frequency = frequency
        self.phase = phase
        self.speed = speed

    def get_height(self, x, time):
        return self.amplitude * math.sin(self.frequency * (x - self.speed * time) + self.phase)

    def get_slope(self, x, time):
        return self.amplitude * self.frequency * math.cos(self.frequency * (x - self.speed * time) + self.phase)

# Класс буйка
class Buoy:
    def __init__(self, id, wave_id, mass, volume, x, y):
        self.id = id
        self.wave_id = wave_id
        self.mass = min(mass, 7)
        self.volume = volume
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.radius = 10 + int(volume * 5)

    def update_position(self, wave, waves, delta_time, time):
        wave_height = wave.get_height(self.x, time)
        wave_slope = wave.get_slope(self.x, time)
        y_offset = WAVE_SPACING * (waves.index(wave) + 1)
        target_y = y_offset + wave_height

        # Физика движения
        buoyancy_force = WATER_DENSITY * self.volume * GRAVITY
        weight = self.mass * GRAVITY
        net_force = buoyancy_force - weight

        mass_factor = max(0.5, 1 / self.mass)
        volume_factor = min(2, self.volume)

        horizontal_direction = 1 if volume_factor > mass_factor else -1
        horizontal_speed = BASE_HORIZONTAL_SPEED * abs(volume_factor - mass_factor)
        
        self.velocity_x = horizontal_speed * horizontal_direction
        self.velocity_y += ((net_force / self.mass) * VELOCITY_SCALE * volume_factor * mass_factor)

        self.velocity_x += wave_slope * VELOCITY_SCALE * volume_factor * mass_factor

        mass_damping = DAMPING * (1 - (self.mass - 1) * 0.05)
        self.velocity_x *= mass_damping
        self.velocity_y *= mass_damping

        max_velocity = MAX_VELOCITY * mass_factor * volume_factor
        self.velocity_x = max(min(self.velocity_x, max_velocity), -max_velocity)
        self.velocity_y = max(min(self.velocity_y, max_velocity), -max_velocity)

        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time

        mass_weight = max(0.1, min(0.9, 1 / self.mass))
        self.y = target_y * mass_weight + self.y * (1 - mass_weight)

        if self.x < -self.radius:
            self.x = WIDTH + self.radius
        elif self.x > WIDTH + self.radius:
            self.x = -self.radius

        if self.y > HEIGHT - self.radius:
            self.y = HEIGHT - self.radius
            self.velocity_y *= -0.5 * mass_factor
        elif self.y < self.radius:
            self.y = self.radius
            self.velocity_y *= -0.5 * mass_factor

# Ф-ия загрузки конфига
def load_config():
    default_config = {
        "waves": [
            {"id": "1", "amplitude": 40, "frequency": 0.02, "phase": 0, "speed": 100}
        ],
        "buoys": [
            {"id": "1", "wave_id": "1", "mass": 1.0, "volume": 1.0, "x": 400, "y": 300}
        ]
    }
    try:
        with open("config.json", "r") as f:
            loaded_config = json.load(f)
            for wave in loaded_config.get("waves", []):
                for key in ["id", "amplitude", "frequency", "phase", "speed"]:
                    if key not in wave:
                        wave[key] = default_config["waves"][0][key]
            for buoy in loaded_config.get("buoys", []):
                for key in ["id", "wave_id", "mass", "volume", "x", "y"]:
                    if key not in buoy:
                        buoy[key] = default_config["buoys"][0][key]
            return loaded_config
    except (FileNotFoundError, json.JSONDecodeError):
        return default_config

# Ф-ия сохранения конфига
def save_config(waves, buoys):
    config = {
        "waves": [
            {
                "id": wave.id,
                "amplitude": wave.amplitude,
                "frequency": wave.frequency,
                "phase": wave.phase,
                "speed": wave.speed
            }
            for wave in waves
        ],
        "buoys": [
            {
                "id": buoy.id,
                "wave_id": buoy.wave_id,
                "mass": buoy.mass,
                "volume": buoy.volume,
                "x": buoy.x,
                "y": buoy.y
            }
            for buoy in buoys
        ]
    }
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

# Сама загрузка конфига
config = load_config()

# Инициализация объектов
waves = [Wave(
    w["id"],
    w["amplitude"],
    w["frequency"],
    w["phase"],
    w["speed"]
) for w in config["waves"]]

buoys = [Buoy(
    b["id"],
    b["wave_id"],
    b["mass"],
    b["volume"],
    b["x"],
    b["y"]
) for b in config["buoys"]]

# Создаем элементы интерфейса
amplitude_label = UILabel(pygame.Rect((10, 10), (100, 30)), "Амплитуда", manager=manager)
amplitude_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 40), (200, 20)),
    start_value=40,
    value_range=(10, 100),
    manager=manager
)

frequency_label = UILabel(pygame.Rect((250, 10), (100, 30)), "Частота", manager=manager)
frequency_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((250, 40), (200, 20)),
    start_value=20,
    value_range=(10, 50),
    manager=manager
)

add_wave_button = UIButton(
    relative_rect=pygame.Rect((500, 30), (120, 30)),
    text="Добавить волну",
    manager=manager
)

remove_wave_button = UIButton(
    relative_rect=pygame.Rect((650, 30), (120, 30)),
    text="Удалить волну",
    manager=manager
)

save_button = UIButton(
    relative_rect=pygame.Rect((10, 70), (100, 30)),
    text="Сохранить",
    manager=manager
)

# Основной цикл
running = True
time = 0
selected_wave_index = 0
selected_buoy = None
buoy_window = None
update_button = None

while running:
    time_delta = clock.tick(FPS) / 1000.0
    time += time_delta
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN: # Проверяем клик по поплавку
            mouse_pos = pygame.mouse.get_pos()
            for buoy in buoys:
                if math.hypot(mouse_pos[0] - buoy.x, mouse_pos[1] - buoy.y) < buoy.radius:
                    selected_buoy = buoy
                    if buoy_window:
                        buoy_window.kill()
                    buoy_window = UIWindow(
                        pygame.Rect((200, 200), (300, 200)),
                        manager,
                        window_display_title="Параметры буя"
                    )

                    UILabel(
                        pygame.Rect((10, 10), (100, 30)),
                        "Масса:",
                        manager=manager,
                        container=buoy_window
                    )
                    mass_entry = UITextEntryLine(
                        pygame.Rect((120, 10), (150, 30)),
                        manager=manager,
                        container=buoy_window,
                        initial_text=str(buoy.mass)
                    )
                    
                    UILabel(
                        pygame.Rect((10, 50), (100, 30)),
                        "Объем:",
                        manager=manager,
                        container=buoy_window
                    )
                    volume_entry = UITextEntryLine(
                        pygame.Rect((120, 50), (150, 30)),
                        manager=manager,
                        container=buoy_window,
                        initial_text=str(buoy.volume)
                    )
                    
                    update_button = UIButton(
                        pygame.Rect((10, 100), (100, 30)),
                        "Обновить",
                        manager=manager,
                        container=buoy_window
                    )

            for i, wave in enumerate(waves): # Проверка клика по волне
                y_offset = WAVE_SPACING * (i + 1)
                if abs(mouse_pos[1] - y_offset) < 30: # Здесь можно изменить ренж клика
                    selected_wave_index = i
                    amplitude_slider.set_current_value(wave.amplitude)
                    frequency_slider.set_current_value(wave.frequency * 1000)
                    
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == add_wave_button:
                new_id = str(len(waves) + 1)
                new_wave = Wave(new_id, 30, 0.02, random.random() * math.pi * 2, 100)
                waves.append(new_wave)
                new_buoy = Buoy(new_id, new_id, 1.0, 1.0, WIDTH / 2, WAVE_SPACING * len(waves))
                buoys.append(new_buoy)

            elif event.ui_element == remove_wave_button:
                if waves and selected_wave_index < len(waves):
                    waves.pop(selected_wave_index)
                    buoys.pop(selected_wave_index)
                    selected_wave_index = max(0, selected_wave_index - 1)
                    for i, wave in enumerate(waves):
                        wave.id = str(i + 1)
                    new_buoys = []
                    for i, wave in enumerate(waves):
                        wave_buoys = [b for b in buoys if b.wave_id == wave.id]
                        if wave_buoys:
                            wave_buoys[0].wave_id = wave.id
                            wave_buoys[0].y = WAVE_SPACING * (i + 1)
                            new_buoys.append(wave_buoys[0])
                        else:
                            new_buoy = Buoy(wave.id, wave.id, 1.0, 1.0, WIDTH / 2, WAVE_SPACING * (i + 1))
                            new_buoys.append(new_buoy)
                    buoys = new_buoys
                    selected_wave_index = min(selected_wave_index, len(waves) - 1)
                    
            elif event.ui_element == save_button:
                save_config(waves, buoys)
                
            elif event.ui_element == update_button and selected_buoy:
                try:
                    new_mass = float(mass_entry.get_text())
                    new_volume = float(volume_entry.get_text())
                    if 0.1 <= new_mass <= 10 and 0.1 <= new_volume <= 10:
                        selected_buoy.mass = min(new_mass, 7)
                        selected_buoy.volume = new_volume
                        selected_buoy.radius = 10 + int(new_volume * 5)
                except ValueError:
                    pass
                    
        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if selected_wave_index < len(waves):
                if event.ui_element == amplitude_slider:
                    waves[selected_wave_index].amplitude = event.value
                elif event.ui_element == frequency_slider:
                    waves[selected_wave_index].frequency = event.value / 1000
                    
        manager.process_events(event)

    for buoy in buoys:
        wave = next((w for w in waves if w.id == buoy.wave_id), None)
        if wave:
            buoy.update_position(wave, waves, time_delta, time)

    screen.fill(WHITE)

    # Рисуем волну
    for i, wave in enumerate(waves):
        y_offset = WAVE_SPACING * (i + 1)
        points = []
        for x in range(0, WIDTH, 2):
            y = y_offset + wave.get_height(x, time)
            points.append((x, y))
        
        if len(points) > 1:
            color = (0, 49, 83) if i == selected_wave_index else (0, 0, 255)
            pygame.draw.lines(screen, color, False, points, 2)

    # Рисуем поплавок
    for buoy in buoys:
        pygame.draw.circle(screen, RED, (int(buoy.x), int(buoy.y)), buoy.radius)
    
    manager.update(time_delta)
    manager.draw_ui(screen)
    
    pygame.display.flip()

pygame.quit()

