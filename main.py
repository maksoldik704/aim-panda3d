from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

# --- НАСТРОЙКИ ИГРЫ ---
game_running = False
score = 0
time_left = 30
target = None

# --- ИНТЕРФЕЙС ---
score_text = Text(text='', origin=(0.5, 0.5), position=(-0.6, 0.45), scale=2, color=color.white)
timer_text = Text(text='', origin=(-0.5, 0.5), position=(0.6, 0.45), scale=2, color=color.white)

# Прицел (Minecraft style)
crosshair = Entity(parent=camera.ui, enabled=False)
Entity(parent=crosshair, model='quad', scale=(0.025, 0.003), color=color.white)
Entity(parent=crosshair, model='quad', scale=(0.003, 0.025), color=color.white)

# --- ЗВУКИ ---
# Используем стандартные звуки Ursina. Если есть свой файл, замени на 'mysound.wav'
shoot_sound = Audio('gun_sound.mp3', loop=False, autoplay=False, volume=0.5)
hit_sound = Audio('coin_1', loop=False, autoplay=False, volume=0.5)

# --- МОДЕЛЬ ОРУЖИЯ ---
try:
    # Загружаем через Panda3D loader, чтобы избежать ошибки Mesh ValueError
    gun_mesh = loader.loadModel("scifi_gun.obj")

    gun = Entity(
        model=gun_mesh,
        parent=camera,  # Привязка к камере

        # --- НАСТРОЙКИ РАЗМЕРА И ПОЗИЦИИ ---
        position=(0.7, -0.7, 1.4),  # (Вправо/Влево, Вверх/Вниз, Вперед/Назад)
        rotation=(0, 180, 0),  # Разворот дулом вперед
        scale=0.03,  # <--- ИЗМЕНЯЙ ЭТО ЧИСЛО ДЛЯ РАЗМЕРА
        # ----------------------------------

        color=color.light_gray,
        enabled=False
    )
except Exception as e:
    print(f"Ошибка загрузки модели: {e}")
    gun = Entity(model='cube', parent=camera, position=(0.5, -0.5, 1), scale=(0.2, 0.2, 1), color=color.gray,
                 enabled=False)


def spawn_target(difficulty_scale):
    global target
    if target: destroy(target)

    target = Entity(
        model='sphere',
        color=color.red,
        scale=difficulty_scale,
        # Случайное появление перед игроком
        position=(random.uniform(-15, 15), random.uniform(1, 6), random.uniform(20, 45)),
        collider='sphere'
    )


def start_game(difficulty):
    global score, time_left, game_running
    menu.enabled = False
    score = 0
    time_left = 30
    game_running = True

    score_text.text = f'Score: {score}'
    player.enabled = True
    player.position = (0, 2, 0)
    mouse.locked = True
    crosshair.enabled = True
    gun.enabled = True

    spawn_target(difficulty)


def input(key):
    global score, game_running
    if key == 'left mouse down' and game_running:
        # Звук выстрела
        if shoot_sound:
            shoot_sound.pitch = random.uniform(0.9, 1.1)  # Немного меняем тон для реализма
            shoot_sound.play()

        # Анимация отдачи (пушка дергается назад)
        gun.position = (0.7, -0.65, 1.3)
        gun.animate_position((0.7, -0.7, 1.4), duration=0.1)

        if mouse.hovered_entity == target:
            score += 1
            score_text.text = f'Score: {score}'
            hit_sound.play()  # Звук попадания
            target.blink(color.white, duration=0.1)
            # Спавним новую мишень через 0.1 сек
            invoke(spawn_target, target.scale_x, delay=0.1)


def update():
    global time_left, game_running
    if game_running:
        time_left -= time.dt
        timer_text.text = f'Time: {int(time_left)}'

        if time_left <= 0:
            end_game()


def end_game():
    global game_running
    game_running = False
    player.enabled = False
    mouse.locked = False
    crosshair.enabled = False
    gun.enabled = False
    if target: destroy(target)

    end_menu.enabled = True
    final_score_text.text = f'Final Score: {score}'


# --- МЕНЮ ---
menu = Entity(parent=camera.ui)
Text(text='AIM TRAINER', parent=menu, y=0.3, origin=(0, 0), scale=3, color=color.yellow)
Button(text='Easy', color=color.azure, scale=(0.3, 0.1), y=0.1, parent=menu, on_click=lambda: start_game(1.5))
Button(text='Normal', color=color.azure, scale=(0.3, 0.1), y=-0.05, parent=menu, on_click=lambda: start_game(1.0))
Button(text='Hard', color=color.azure, scale=(0.3, 0.1), y=-0.2, parent=menu, on_click=lambda: start_game(0.5))

# --- ФИНАЛ ---
end_menu = Entity(parent=camera.ui, enabled=False)
final_score_text = Text(text='', parent=end_menu, y=0.1, origin=(0, 0), scale=2)
Button(text='Back to Menu', color=color.gray, scale=(0.3, 0.1), y=-0.1, parent=end_menu,
       on_click=lambda: [setattr(end_menu, 'enabled', False), setattr(menu, 'enabled', True)])

# --- МИР ---
Sky()
ground = Entity(model='plane', scale=100, texture='white_cube', texture_scale=(100, 100), color=color.light_gray,
                collider='box')

player = FirstPersonController(enabled=False)
player.cursor.enabled = False
player.gravity = 1

app.run()