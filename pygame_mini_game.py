import pygame
import sys
import random
import os

# 초기화
pygame.init()
pygame.mixer.init()  # 오디오 초기화

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rhythm RPG")
clock = pygame.time.Clock()
FPS = 60

# 색상/폰트
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
GRAY = (150, 150, 150)
FONT = pygame.font.SysFont("malgungothic", 48)
SMALL_FONT = pygame.font.SysFont("malgungothic", 32)
BIG_FONT = pygame.font.SysFont("Arial", 72)

# 이미지 로드 함수 (상대경로)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def load_image(filename):
    return pygame.image.load(os.path.join(BASE_DIR, filename)).convert_alpha()

# 배경음악 추가
music_path = os.path.join(BASE_DIR, "any_background_music.wav")
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)  # 무한 반복 재생

# 이미지 로드
background = load_image("any_background_image.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# 영웅 이미지
hero_img_raw = load_image("any_hero_image.png")
hero = pygame.transform.scale(hero_img_raw, (int(hero_img_raw.get_width() * 0.15), int(hero_img_raw.get_height() * 0.15)))

# 몬스터 이미지
monster_img_raw = load_image("any_monster_image.png")
monster = pygame.transform.scale(monster_img_raw, (int(monster_img_raw.get_width() * 0.4), int(monster_img_raw.get_height() * 0.4)))

# 위치 계산
hero_pos = (50, HEIGHT - hero.get_height() - 50)
monster_pos = (WIDTH - monster.get_width() - 50, HEIGHT - monster.get_height() - 0)

# 방향키 문자열 매핑
KEY_MAP = {
    pygame.K_LEFT: "←",
    pygame.K_RIGHT: "→",
    pygame.K_UP: "↑",
    pygame.K_DOWN: "↓"
}

# 체력 바 그리기(보스)
def draw_boss_hp_bar(hp, max_hp):
    bar_x = 600
    bar_y = 30
    for i in range(max_hp):
        color = GREEN if i < hp else GRAY
        pygame.draw.rect(screen, color, (bar_x + i * 40, bar_y, 30, 30))

# 체력 바 그리기(용사)
def draw_hero_hp_bar(hp, max_hp):
    # hero_pos 기준으로 체력 바 위치 계산
    bar_x = hero_pos[0] + 20
    bar_y = hero_pos[1] - 40  # 머리 위 40픽셀 위에 표시
    for i in range(max_hp):
        color = RED if i < hp else GRAY
        pygame.draw.rect(screen, color, (bar_x + i * 40, bar_y, 30, 30))

# 텍스트 렌더링
def draw_text(text, font, color, surface, x, y):
    render = font.render(text, True, color)
    rect = render.get_rect(center=(x, y))
    surface.blit(render, rect)

# 방향키 시퀀스 그리기
def draw_directions(direction_list, user_input, start_y):
    box_size = 50
    margin = 8
    max_per_row = 10
    for idx, key in enumerate(direction_list):
        row = idx // max_per_row
        col = idx % max_per_row
        total_width = (box_size + margin) * min(len(direction_list), max_per_row)
        start_x = WIDTH // 2 - total_width // 2
        x = start_x + col * (box_size + margin)
        y = start_y + row * (box_size + margin)
        rect = pygame.Rect(x, y, box_size, box_size)
        if direction_list is user_input:
            color = (0, 200, 0)
        else:
            if idx < len(user_input):
                if user_input[idx] == key:
                    color = (0, 200, 0)
                else:
                    color = (200, 0, 0)
            else:
                color = (100, 100, 100)
        pygame.draw.rect(screen, color, rect, border_radius=6)
        if key in KEY_MAP:
            key_text = KEY_MAP[key]
            text_surf = SMALL_FONT.render(key_text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)

# 라운드별 난이도/시간 설정
def get_round_settings(round_num):
    input_length = 5 + max(0, round_num - 1)
    time_limit = max(1.0, 10 - (round_num - 1) * 1)  # 라운드마다 1초씩 감소, 최소 1초
    if round_num == 1:
        allowed_keys = [pygame.K_LEFT, pygame.K_RIGHT]
    elif round_num == 2:
        allowed_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP]
    else:
        allowed_keys = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
    return input_length, time_limit, allowed_keys

# 랜덤 방향키 시퀀스 생성
def generate_random_directions(length, allowed_keys):
    return [random.choice(allowed_keys) for _ in range(length)]

# 게임 시작 대기 화면
def wait_for_start():
    screen.blit(background, (0, 0))
    draw_text("게임을 시작하려면 Y를 누르세요", SMALL_FONT, (255, 255, 255), screen, WIDTH // 2, HEIGHT // 2)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return

# 미니게임(방향키 입력) 세션
def direction_mini_game(round_num):
    input_length, time_limit, allowed_keys = get_round_settings(round_num)
    target = generate_random_directions(input_length, allowed_keys)
    user_input = []
    start_time = pygame.time.get_ticks()
    input_completed = False
    result_show_start = None
    correct_count = 0
    timer_stopped = False
    while True:
        screen.blit(background, (0, 0))
        screen.blit(hero, hero_pos)
        screen.blit(monster, monster_pos)
        draw_text(f"방향키 입력 미니게임 (라운드 {round_num})", SMALL_FONT, (200, 200, 200), screen, WIDTH // 2, 100)
        draw_hero_hp_bar(hero_hp, max_hero_hp)
        draw_boss_hp_bar(enemy_hp, max_hp)
        current_time = pygame.time.get_ticks()
        if not timer_stopped:
            elapsed_time = (current_time - start_time) / 1000
            remaining_time = max(0, time_limit - elapsed_time)
        elif result_show_start is not None:
            remaining_time = max(0, time_limit - (result_show_start - start_time) / 1000)
        else:
            remaining_time = 0
        draw_text(f"남은 시간: {remaining_time:.1f} / {time_limit:.1f} 초", SMALL_FONT, (255, 100, 100), screen, WIDTH // 2, HEIGHT // 4 - 40)
        draw_text("입력할 방향:", SMALL_FONT, (255, 255, 255), screen, WIDTH // 2, HEIGHT // 4)
        draw_directions(target, user_input, HEIGHT // 4 + 40)
        draw_text("입력한 방향:", SMALL_FONT, (200, 200, 200), screen, WIDTH // 2, HEIGHT // 2 + 80)
        draw_directions(user_input, user_input, HEIGHT // 2 + 110)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not input_completed:
                if event.key in allowed_keys and len(user_input) < len(target):
                    user_input.append(event.key)
                    if len(user_input) == len(target):
                        input_completed = True
                        timer_stopped = True
                        correct_count = sum(1 for i in range(len(target)) if user_input[i] == target[i])
                        result_show_start = pygame.time.get_ticks()
        if not input_completed and not timer_stopped and elapsed_time >= time_limit:
            input_completed = True
            timer_stopped = True
            correct_count = 0  # 시간 초과면 무조건 MISS
            result_show_start = pygame.time.get_ticks()
        if input_completed:
            color = (100, 255, 100) if correct_count == len(target) else (255, 200, 50)
            draw_text(f"정답 수: {correct_count}/{len(target)}", FONT, color, screen, WIDTH // 2, HEIGHT * 0.8)
            if result_show_start is not None and pygame.time.get_ticks() - result_show_start > 1200:
                return correct_count, len(target)
        pygame.display.flip()
        clock.tick(60)

# RPG 메인 루프
def main():
    global hero_hp, max_hero_hp, enemy_hp, max_hp
    round_num = 1
    enemy_hp = 10
    max_hp = 10
    hero_hp = 3
    max_hero_hp = 3
    running = True
    monsound = pygame.mixer.Sound(os.path.join(BASE_DIR, "any_monsterSound.wav"))
    sword1a = pygame.mixer.Sound(os.path.join(BASE_DIR, "any_swordSound.wav"))
    monster_die = pygame.mixer.Sound(os.path.join(BASE_DIR, "any_monsterDieSound.wav"))
    punch = pygame.mixer.Sound(os.path.join(BASE_DIR, "any_punchSound.wav"))
    die = pygame.mixer.Sound(os.path.join(BASE_DIR, "any_dieSound.wav"))
    defense = pygame.mixer.Sound(os.path.join(BASE_DIR, "any_defenseSound.mp3"))
    while running:
        wait_for_start()
        while enemy_hp > 0 and hero_hp > 0:
            screen.blit(background, (0, 0))
            screen.blit(hero, hero_pos)
            screen.blit(monster, monster_pos)
            draw_text(f"Round {round_num}", SMALL_FONT, (0,0,0), screen, 1100, 40)
            draw_hero_hp_bar(hero_hp, max_hero_hp)
            draw_boss_hp_bar(enemy_hp, max_hp)
            pygame.display.flip()
            pygame.time.wait(800)

            # 미니게임
            correct, total = direction_mini_game(round_num)
            # 판정 및 HP 처리
            if correct == total:
                result = "PERFECT!"
                damage = 2
                hero_damage = 0
                sword1a.play()  # perfect일 때 효과음 재생
            elif correct >= total * 0.8:
                result = "GOOD!"
                damage = 1
                hero_damage = 0
                punch.play()  # good일 때 효과음 재생
            elif correct >= total * 0.6:
                result = "BAD!"
                damage = 0
                hero_damage = 0
                defense.play()  # bad일 때 효과음 재생
            else:
                result = "MISS!"
                damage = 0
                hero_damage = 1
                monsound.play()  # miss일 때 효과음 재생
            enemy_hp -= damage
            hero_hp -= hero_damage

            # 판정 표시
            screen.blit(background, (0, 0))
            screen.blit(hero, hero_pos)
            screen.blit(monster, monster_pos)
            draw_text(result, BIG_FONT, RED if result == "PERFECT!" else (255,200,50), screen, WIDTH // 2, HEIGHT // 2)
            draw_hero_hp_bar(hero_hp, max_hero_hp)
            draw_boss_hp_bar(max(0, enemy_hp), max_hp)
            pygame.display.flip()
            pygame.time.wait(1200)

            round_num += 1

        # 승리/패배 화면
        screen.blit(background, (0, 0))
        if enemy_hp <= 0:
            pygame.mixer.music.stop()  # 배경음악 먼저 정지
            monster_die.play()         # 몬스터 죽음 효과음 재생
            draw_text("YOU WIN!", BIG_FONT, RED, screen, WIDTH // 2, HEIGHT // 2 - 50)
        else:
            pygame.mixer.music.stop()  # 배경음악 먼저 정지
            die.play()                 # 플레이어가 죽을 때 효과음 재생
            draw_text("YOU LOSE!", BIG_FONT, RED, screen, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text("다시 하려면 Y, 종료는 N", FONT, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 80)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        round_num = 1
                        enemy_hp = max_hp
                        hero_hp = max_hero_hp
                        waiting = False
                    elif event.key == pygame.K_n:
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    main()
