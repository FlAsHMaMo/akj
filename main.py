import pygame
import random
import sys
import os

# Pygame inicializálása
pygame.init()

# Képernyő beállításai
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 688
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Akadály Kikerülős Játék")

# Színek
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
BACKGROUND_COLOR = (240, 240, 240)

# Játékos paraméterek
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
player_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
player_y = SCREEN_HEIGHT - PLAYER_HEIGHT - 10
player_speed = 10
player_skin = "BLUE"

# Akadály paraméterek
OBSTACLE_WIDTH = 50
OBSTACLE_HEIGHT = 50
obstacle_speed = 10
obstacles = []

# Játékállapot változók
score = 0
game_over = False
current_skin = "BLUE"
skins = {"BLUE": BLUE, "GREEN": GREEN, "BLACK": BLACK, "YELLOW": YELLOW}

# Rekord fájl
high_score_file = "high_score.txt"
high_score = 0

# Időzítő
clock = pygame.time.Clock()

# Rekord betöltése
def load_high_score():
    global high_score
    if os.path.exists(high_score_file):
        with open(high_score_file, "r") as file:
            high_score = int(file.read())
    else:
        high_score = 0

# Rekord mentése
def save_high_score():
    global high_score
    with open(high_score_file, "w") as file:
        file.write(str(high_score))

# Gomb rajzolása
def draw_button(text, x, y, width, height, color, text_color, font):
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=12)
    button_text = font.render(text, True, text_color)
    text_rect = button_text.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(button_text, text_rect)
    return pygame.Rect(x, y, width, height)

# Kezdőképernyő
def start_screen():
    font = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)

    while True:
        screen.fill(BACKGROUND_COLOR)
        title = font.render("Akadály Kikerülős Játék", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3))
        
        start_button = draw_button("Start - space", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, 230, 50, GRAY, BLUE, font_medium)
        skins_button = draw_button("Skinek", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 100, 150, 50, GRAY, BLUE, font_medium)
        high_score_button = draw_button("Legjobb Eredmény", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 200, 350, 50, GRAY, BLUE, font_medium)

        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "start"
                elif skins_button.collidepoint(event.pos):
                    return "skins"
                elif high_score_button.collidepoint(event.pos):
                    return "high_score"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "start"  # A Space gomb lenyomására is indítja a játékot
                elif event.key == pygame.K_s:
                    return "skins"
                elif event.key == pygame.K_h:
                    return "high_score"

# Skin választó menü
def skin_menu():
    font_medium = pygame.font.Font(None, 48)

    while True:
        screen.fill(BACKGROUND_COLOR)
        title = font_medium.render("Válassz Skint", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4))

        back_button = draw_button("Vissza", 10, 10, 150, 50, GRAY, BLUE, font_medium)

        skin_buttons = []
        y_offset = SCREEN_HEIGHT // 3
        for i, (skin_name, color) in enumerate(skins.items()):
            skin_button = draw_button(skin_name, SCREEN_WIDTH // 4, y_offset + i * 70, 200, 50, color, WHITE, font_medium)
            skin_buttons.append((skin_button, skin_name))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return
                for button, skin_name in skin_buttons:
                    if button.collidepoint(event.pos):
                        global current_skin
                        current_skin = skin_name
                        return

# Legjobb eredmény képernyő
def high_score_screen():
    font = pygame.font.Font(None, 48)

    while True:
        screen.fill(BACKGROUND_COLOR)
        title = font.render("Legjobb Eredmény", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4))

        back_button = draw_button("Vissza", 10, 10, 150, 50, GRAY, BLUE, font)

        # Megjelenítjük a legjobb eredményt
        high_score_text = font.render(f"Rekord: {high_score}", True, BLACK)
        screen.blit(high_score_text, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    return  # Vissza a kezdőképernyőre

# Akadályok mozgása
def move_obstacles():
    global obstacles, score, game_over

    for obstacle in obstacles:
        obstacle[1] += obstacle_speed

    obstacles = [ob for ob in obstacles if ob[1] < SCREEN_HEIGHT]

    for obstacle in obstacles:
        if (
            player_x < obstacle[0] + OBSTACLE_WIDTH and
            player_x + PLAYER_WIDTH > obstacle[0] and
            player_y < obstacle[1] + OBSTACLE_HEIGHT and
            player_y + PLAYER_HEIGHT > obstacle[1]
        ):
            game_over = True

# Játék főciklus
def game_loop():
    global player_x, player_y, score, obstacles, game_over

    player_x = SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2
    obstacles = []
    score = 0
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - PLAYER_WIDTH:
            player_x += player_speed

        if random.randint(1, 100) <= 15:
            obstacle_x = random.randint(0, SCREEN_WIDTH - OBSTACLE_WIDTH)
            obstacles.append([obstacle_x, 0])

        move_obstacles()

        screen.fill(BACKGROUND_COLOR)

        # Játékos karakter rajzolása
        pygame.draw.rect(screen, skins[current_skin], (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))

        # Akadályok rajzolása
        for obstacle in obstacles:
            pygame.draw.rect(screen, RED, (obstacle[0], obstacle[1], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

        # Pontszám megjelenítése
        score += 1
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Pontszám: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        # Rekord megjelenítése
        high_score_text = font.render(f"Rekord: {high_score}", True, BLACK)
        screen.blit(high_score_text, (SCREEN_WIDTH - 200, 10))

        pygame.display.update()
        clock.tick(60)

# Program indítása
load_high_score()

while True:
    result = start_screen()
    if result == "start":
        game_loop()
        if score > high_score:
            high_score = score
            save_high_score()  # Rekord mentése a fájlba
    elif result == "skins":
        skin_menu()
    elif result == "high_score":
        high_score_screen()
