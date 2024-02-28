import pygame
import random
import math
import sys
import time

pygame.init()
WIDTH = 900
HEIGHT = 600
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
fone = (0, 195, 0)
BLUE = (0, 255, 255)
vibe_count = 0  # Счетчик волн
ENEMY_HEALTH = 3  # Здоровье врагов
ENEMY_DAMAGE = 1  # Урон врагов
CASTLE_HEALTH = 20  # Здоровье замка
NUM_WAVES = 4  # Количество волн врагов
WAVE_DELAY = [15, 20, 25, 40]  # Задержка между волнами в секундах
ENEMIES_PER_WAVE = [5, 10, 15, 15]  # Количество врагов в каждой волне
BUDGET = 1500

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Treasure protection")

enemy_img = pygame.image.load("enemy.png")  # Загружаем изображение врага
tower_img = pygame.image.load("tower.png")  # Загружаем изображение башни
bullet_img = pygame.image.load("bullet.png")  # Загружаем изображение пули
castle_img = pygame.image.load("castle.png")  # Загружаем изображение замка
ship_img = pygame.image.load("ship.png")  # Загружаем изображение корабля
Heart_img = pygame.image.load("heart.png")  # Загружаем изображение сердца
Money_img = pygame.image.load("money.png")  # Загружаем изображение монет
Vibe_img = pygame.image.load("vibe.png")  # Загружаем изображение волны
image_below_vibe_img = pygame.image.load("time.png")  # Загружаем изображение часов
loading_screen_img = pygame.image.load("windowdounload.png")  # Загружаем изображение экрана загрузки
info_screen_img = pygame.image.load("info_screen.png")  # Загружаем изображение информационного экрана
tower_shot_sound = pygame.mixer.Sound("sound_gun.mp3")  # Загружаем звук выстрела из башни
no_enemy_time = None


class Ship:  # Создаем новый класс для отображения картинки корабля
    def __init__(self):
        self.x = -138  # Устанавливаем начальное значение координаты x корабля
        self.y = 130  # Устанавливаем начальное значение координаты y корабля

    def draw(self, win):  # Определяем метод, который рисует корабль на заданном экране
        win.blit(ship_img, (self.x, self.y))  # Рисуем изображение корабля на экране в заданных координатах


class Heart:
    def __init__(self):
        self.x = 100
        self.y = 10

    def draw(self, win):
        win.blit(Heart_img, (self.x, self.y))


class Money:
    def __init__(self):
        self.x = 191
        self.y = 17

    def draw(self, win):
        win.blit(Money_img, (self.x, self.y))


class Vibe:
    def __init__(self):
        self.x = 98
        self.y = 45

    def draw(self, win):
        win.blit(Vibe_img, (self.x, self.y))


class ImageBelowVibe:
    def __init__(self):
        self.x = 112
        self.y = 75
        self.image = pygame.image.load("time.png")

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = ENEMY_HEALTH  # Устанавливаем начальное значение здоровья врага
        self.max_health = ENEMY_HEALTH  # Устанавливаем максимальное значение здоровья врага
        self.vel = 1  # Устанавливаем скорость врага

    def move(self):
        self.x += self.vel  # Изменяем координату x врага на значение скорости

    def draw(self, win):  # Определяем метод, который рисует врага на заданном экране
        center_x = self.x + enemy_img.get_width() // 2  # Находим центр x координаты изображения врага
        pygame.draw.rect(win, RED,
                         (center_x - 10, self.y - 10, 20, 5))  # Рисуем красный прямоугольник (полоску здоровья врага)
        pygame.draw.rect(win, fone, (center_x - 10, self.y - 10, 20 * (self.health / self.max_health),
                                     5))  # Заполняем прямоугольник зеленым цветом в зависимости от текущего здоровья
        win.blit(enemy_img, (self.x, self.y))


class Bullet:
    def __init__(self, x, y, target_x,
                 target_y):
        self.x = x
        self.y = y
        self.target_x = target_x  # Задаем координаты цели x
        self.target_y = target_y  # Задаем координаты цели y
        self.speed = 5
        self.damage = 1
        self.is_active = True  # Задаем статус активности снаряда

    def move(self):  # Определяем метод, который перемещает снаряд в направлении цели
        if self.is_active:  # Проверяем, активен ли снаряд
            angle = math.atan2(self.target_y - self.y, self.target_x - self.x)  # Вычисляем угол между пулей и целью
            # Вычисляем изменение координаты
            self.x += self.speed * math.cos(angle)
            self.y += self.speed * math.sin(angle)
            distance_to_target = math.sqrt(
                (self.target_x - self.x) ** 2 + (self.target_y - self.y) ** 2)  # Вычисляем расстояние до цели
            if distance_to_target < self.speed:
                self.is_active = False  # Статус снаряда становится неактивным

    def draw(self, win):
        if self.is_active:  # Проверяем, активен ли снаряд
            win.blit(bullet_img, (self.x, self.y))  # Рисуем изображение снаряда на экране в заданных координатах


class Tower:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 100  # Устанавливаем дальность атаки башни на 100 пикселей
        self.damage_per_shot = 1
        self.shots_to_kill = ENEMY_HEALTH  # Устанавливаем количество выстрелов для убийства врага равным его здоровью.
        self.shots_fired = 0  # Количество выстрелов, которые уже были произведены
        self.timer = 0  # Таймер для управления периодом между выстрелами

    def find_closest_enemy(self, enemies):  # Метод для поиска ближайшего врага из списка врагов
        closest_enemy = None
        min_distance = float('inf')  # Устанавливаем начальное значение на бесконечность,
        # чтобы первый враг всегда был ближайшим
        for enemy in enemies:
            # Вычисляем расстояние до врага с помощью теоремы Пифагора и записываем в переменную distance
            distance = math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
            if distance < min_distance:
                min_distance = distance
                closest_enemy = enemy
        return closest_enemy  # Возвращаем ближайшего врага

    def shoot(self, enemies, bullets):
        # Метод для производства выстрела
        self.timer += 1
        if self.timer % 180 == 0:
            closest_enemy = self.find_closest_enemy(enemies)  # Находим ближайшего врага
            if closest_enemy:  # Если враг найден, то
                # Создаем пулю в начальной позиции башни и направлении к позиции ближайшего врага
                bullets.append(Bullet(self.x, self.y, closest_enemy.x, closest_enemy.y))
                self.shots_fired += 1  # Увеличиваем количество произведенных выстрелов
                closest_enemy.health -= self.damage_per_shot
                # Если здоровье врага меньше или равно 0, то убираем его из списка врагов и даем бонус к бюджету
                if closest_enemy.health <= 0:
                    enemies.remove(closest_enemy)
                    self.shots_fired = 0
                    global BUDGET
                    BUDGET += 100
                elif self.shots_fired >= self.shots_to_kill:  # Если количество выстрелов больше
                    # или равно для убийства, то
                    self.shots_fired = 0
                # Воспроизводим звук выстрела из башни
                tower_shot_sound.play()

    def draw(self, win):
        win.blit(tower_img, (self.x, self.y))  # Отрисовываем изображение башни


class Castle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = CASTLE_HEALTH  # Устанавливаем начальное количество здоровья замка

    def draw(self, win):
        win.blit(castle_img, (self.x, self.y))  # Отрисовываем изображение замка на экране
        font = pygame.font.Font(None, 36)
        text = font.render(f'{self.health}', True, (0, 0, 0))
        text_rect = text.get_rect(
            center=(167, 32))  # Вычисляем прямоугольник для отображения текста по центру изображения
        win.blit(text, text_rect)  # Отрисовываем текст здоровья замка на экране


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)  # Создает прямоугольник с заданными координатами и размерами
        self.color = fone
        self.text = text
        self.action = action  # Функция, которая будет вызвана при нажатии кнопки
        self.font = pygame.font.Font(None, 36)  # Загружает шрифт размером 36 пикселей
        self.radius = 20  # Радиус для округления углов

    def draw(self, win):
        # Рисует прямоугольник кнопки с закругленными углами
        pygame.draw.rect(win, self.color, self.rect, border_radius=self.radius)
        # Рисует текст на кнопке по центру
        text = self.font.render(self.text, True, (0, 0, 0))
        win.blit(text, (self.rect.x + (self.rect.width - text.get_width()) // 2,
                        self.rect.y + (self.rect.height - text.get_height()) // 2))

    def handle_event(self, event):
        # Проверяет, если произошло событие нажатия кнопки мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Проверяет, что клик произошел в пределах кнопки
            if self.rect.collidepoint(event.pos):
                # Если задана дополнительная функция для кнопки, вызывает ее
                if self.action:
                    self.action()


def is_valid_tower_position(x, y, placing_tower_mode):
    # Проверяет, находится ли игрок в режиме установки башни
    if not placing_tower_mode:
        return False
    pixel_color = win.get_at((x, y))
    # Возвращает True, если пиксель, на котором находится курсор мыши зеленый иначе False
    return pixel_color == GREEN


# Определение функции для отрисовки окна игры
def draw_window(enemies, towers, castle, bullets, tower_button, about_button, ship, heart, money,
                vibe, image_below_vibe, wave, time_paused, time_passed):
    win.fill(GREEN)
    # Рисуем прямоугольники
    pygame.draw.rect(win, BROWN, (0, 260, WIDTH, 80))
    pygame.draw.rect(win, BLUE, (0, 0, 100, 800))
    pygame.draw.rect(win, fone, (110, 10, 180, 105), border_radius=12)
    for tower in towers:
        tower.draw(win)
    for bullet in bullets:
        bullet.draw(win)
    # Отрисовка обьектов
    castle.draw(win)
    tower_button.draw(win)
    about_button.draw(win)
    ship.draw(win)
    heart.draw(win)
    money.draw(win)
    vibe.draw(win)
    image_below_vibe.draw(win)
    for enemy in enemies:
        enemy.draw(win)
    # Создание объекта шрифта для отображения текста
    font = pygame.font.Font(None, 38)
    text = font.render(f'{BUDGET}', True, (0, 0, 0))
    font_vin = pygame.font.Font(None, 120)
    win.blit(text, (225, 19))
    wave_font = pygame.font.Font(None, 30)
    wave_text = wave_font.render(f'Волна: {wave}/{NUM_WAVES}', True, (0, 0, 0))
    win.blit(wave_text, (155, 55))
    time_text = wave_font.render(f'Время: {time_passed}', True, (0, 0, 0))
    win.blit(time_text, (155, 85))

    # Проверяем, если на пути нет врагов в течение определенного времени
    if all(enemy.x >= castle.x for enemy in enemies):
        global no_enemy_time
        if no_enemy_time is None:
            no_enemy_time = time.time()
        if time.time() - no_enemy_time >= 5:
            victory_text = font_vin.render('ПОБЕДА!', True, (255, 215, 0))
            win.blit(victory_text,
                     (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - victory_text.get_height() // 2))
            pygame.display.update()
    else:
        no_enemy_time = None
    pygame.display.update()


def game_over(time_start, win, BUDGET, current_screen):
    global seconds_text
    font = pygame.font.Font(None, 50)
    bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(bg, (245, 245, 220, 100), pygame.Rect(0, 0, WIDTH, HEIGHT))
    # Выводим поверхность на экран
    win.blit(bg, (0, 0))
    # Создаем текст Игра закончена и выводим его на экран
    text = font.render("Игра закончена", True, (0, 0, 0))
    win.blit(text, (WIDTH // 2 - text.get_width() // 2, (HEIGHT // 4) - text.get_height() // 2))
    # Вычисляем, сколько времени прошло с момента начала игры
    time_passed = int(time.time() - time_start)
    k = 0
    # Определяем склонение слова секунда
    if 11 <= time_passed <= 14:
        seconds_text = "секунд"
        k += 1
    if k == 0:
        if time_passed % 10 == 1:
            seconds_text = "секунду"
        elif 2 <= time_passed % 10 <= 4:
            seconds_text = "секунды"
        else:
            seconds_text = "секунд"
    # Создаем текст о том, сколько времени игрок продержался
    time_text = font.render(f'Вы продержались {time_passed} {seconds_text}!', True, (0, 0, 0))
    # Выводим текст на экран
    win.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 3 - text.get_height() // 3))
    # Создаем кнопку "Заново"
    restart_button = Button(WIDTH // 2 - 70, HEIGHT // 2.2, 140, 50, 'Заново', loading_screen)
    restart_button.draw(win)

    # Запускаем игровой цикл, чтобы обрабатывать события кнопки
    run = True
    while run:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Обработка событий кнопки Заново
            restart_button.handle_event(event)
        # Обновление экрана
        pygame.display.update()


def show_info_screen():
    # Используем глобальную переменную для обозначения текущего экрана
    global current_screen
    # Устанавливаем текущий экран, чтобы перейти на экран информации
    current_screen = 'info'
    # Выводим изображение info_screen_img на экран
    win.blit(info_screen_img, (140, 30))
    # Создаем кнопку "Обратно" с координатами и размерами, и привязываем ее к функции loading_screen
    back_button = Button(WIDTH // 2 - 70, HEIGHT // 2 + 110, 140, 50, 'Обратно', loading_screen)
    back_button.draw(win)
    pygame.display.update()
    # Запускаем игровой цикл
    while True:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:  # Если произошло событие нажатия кнопки мыши
                # Проверяем, если произошло событие нажатия на кнопку Обратно
                if back_button.rect.collidepoint(event.pos):
                    # Если мы на экране информации, возвращаемся к игровому экрану
                    if current_screen == 'info':
                        return
        pygame.display.update()


def loading_screen():
    # Делаем доступными глобальные переменные
    global BUDGET, current_screen
    BUDGET = 1500  # Устанавливаем бюджет на 1500 при загрузке экрана
    current_screen = 'loading'  # Устанавливаем текущий экран как loading, чтобы перейти на экран загрузки
    run = True
    clock = pygame.time.Clock()  # Создаем объект для управления временем в игре
    enemies = []
    towers = []
    bullets = []
    castle = Castle(770, 135)
    # Переменная, определяющая, что режим размещения башен активирован
    placing_tower_mode = False
    start_button_pressed = False  # Переменная, определяющая, что нажата кнопка Начать
    wave = 0
    wave_countdown = 0
    wave_enemies = 0
    enemies_passed = 0
    time_paused = False
    time_start = None
    # Создаем экземпляры классов
    ship = Ship()
    heart = Heart()
    money = Money()
    vibe = Vibe()
    image_below_vibe = ImageBelowVibe()

    # Функция для переключения режима размещения башен
    def toggle_placing_tower_mode():
        nonlocal placing_tower_mode
        placing_tower_mode = not placing_tower_mode

    # Функция для начала игры
    def start_game():
        # Используем локальную переменную, чтобы изменить глобальную переменную
        nonlocal start_button_pressed
        start_button_pressed = True
        BUDGET = 1500  # Устанавливаем бюджет на 1500 при нажатии кнопки Start
        tower_shot_sound.set_volume(0.3)
        play_music()  # Вызываем функцию только после нажатия кнопки Start

    # Функция для воспроизведения музыки
    def play_music():
        pygame.mixer.music.load("Scotty He's a Pirate.mp3")
        pygame.mixer.music.set_volume(0.3)
        # Воспроизводим музыку в цикле
        pygame.mixer.music.play(loops=-1)

    # Создаем кнопки
    tower_button = Button(WIDTH - 250, 10, 240, 50, 'Поставить башню', toggle_placing_tower_mode)
    start_button = Button(WIDTH // 2 - 70, HEIGHT // 2 + 50, 140, 50, 'Start', start_game)
    about_button = Button(WIDTH - 50, (HEIGHT // 3 * 2.8), 40, 30, '?', show_info_screen)
    time_start = None
    while run:
        # Ограничиваем цикл так, чтобы он выполнялся 60 раз в секунду
        clock.tick(60)
        # Перебираем все события, которые произошли
        for event in pygame.event.get():
            # Если событие - это закрытие окна, то выходим из цикла
            if event.type == pygame.QUIT:
                run = False
            # Если произошло нажатие мыши
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Обработка событий для всех трех кнопок
                tower_button.handle_event(event)
                start_button.handle_event(event)
                about_button.handle_event(event)
                # Получаем координаты нажатия
                pos = pygame.mouse.get_pos()
                x, y = pos
                # Если нажатие допустимо для размещения башни и имеется достаточно денег
                if is_valid_tower_position(x, y, placing_tower_mode):
                    if BUDGET >= 500:
                        # Добавляем башню в список башен и вычитаем ее стоимость из бюджета
                        towers.append(Tower(x - tower_img.get_width() // 2, y - tower_img.get_height() // 2))
                        BUDGET -= 500
        # Если не нажата кнопка Start, показываем экран загрузки
        if not start_button_pressed:
            win.blit(loading_screen_img, (0, 0))
            start_button.draw(win)
            pygame.display.flip()
            continue
        # Если обратный отсчет волны равен нулю, проверяем условие победы или поражения
        if wave_countdown == 0:
            # Если волны закончились и все волны прошли, выводим экран Игра окончена
            if wave >= NUM_WAVES and enemies_passed >= sum(ENEMIES_PER_WAVE):
                game_over(time_start, win, BUDGET, current_screen)
                run = False
            # Если еще есть волны, начинаем новую волну
            elif wave < NUM_WAVES:
                wave_enemies = ENEMIES_PER_WAVE[wave]
                wave_countdown = 60 * WAVE_DELAY[wave]
                wave += 1
        # Если обратный отсчет волны больше нуля, продолжаем его отсчет и создаем новых врагов
        if wave_countdown > 0:
            wave_countdown -= 1
            if wave_countdown % 60 == 0:
                if wave_enemies > 0:
                    enemies.append(Enemy(25, HEIGHT // 2 - 50))
                    wave_enemies -= 1
        # Передвигаем всех врагов и убираем тех, которые достигли замка
        for enemy in enemies:
            enemy.move()
            if enemy.x >= castle.x:
                castle.health -= 1
                enemies.remove(enemy)
                enemies_passed += 1
            # Убираем врага из списка и добавляем деньги в бюджет, если его здоровье закончилось
            elif enemy.health <= 0:
                enemies.remove(enemy)
                BUDGET += 100
        # Стрельба из всех башен
        for tower in towers:
            tower.shoot(enemies, bullets)
        # Двигаем все снаряды и убираем те, которые вышли за пределы
        for bullet in bullets:
            bullet.move()
            bullets = [bullet for bullet in bullets if 0 <= bullet.x <= WIDTH and 0 <= bullet.y <= HEIGHT]
        # Если здоровье замка меньше или равно нулю, выводим экран Игра окончена
        if castle.health <= 0:
            game_over(time_start, win, BUDGET, current_screen)
            run = False
        # Если игра только началась, определяем сколько времени прошло с начала игры
        if time_start is not None:
            time_passed = int(time.time() - time_start)
        else:
            time_passed = 0
        # Отрисовываем окно
        draw_window(enemies, towers, castle, bullets,
                    tower_button, about_button, ship, heart, money, vibe, image_below_vibe, wave, time_paused,
                    time_passed)
        # Если обратный отсчет волны больше нуля и время начала игры не установлено, устанавливаем его
        if wave_countdown > 0 and time_start is None:
            time_start = time.time()
    pygame.quit()


if __name__ == "__main__":
    loading_screen()
