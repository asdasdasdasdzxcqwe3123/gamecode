from PIL import Image, ImageDraw, ImageFont
import time
from Character import Character
from Joystick import Joystick
from Background import Background
from Arrow import Arrow
from monster import Monster
import numpy as np
import os
import Gamestart
from Gameover import display_game_over_screen

font_path = os.path.join(os.path.dirname(__file__), "../pixelpont/PressStart2P-Regular.ttf")
font_size = 15
font_size1 = 50

# Load fonts
try:
    font = ImageFont.truetype(font_path, font_size)
except IOError:
    print(f"Font load failed: {font_path}. Using default font.")
    font = ImageFont.load_default()
try:
    font1 = ImageFont.truetype(font_path, font_size1)
except IOError:
    print(f"Font load failed: {font_path}. Using default font.")
    font1 = ImageFont.load_default()


def start_game(FPS, joystick, background):
    frame_duration = 1.0 / FPS

    joystick = Joystick()
    background = Background()
    character = Character(480, 240)
    spawn_indicator_duration = 2.0
    spawn_indicators = []

    monsters = []
    spawn_interval = 5
    last_spawn_time = time.time()

    countdown_time = 300
    start_time = time.time()
    dropped_arrows_positions = []  # 드롭된 화살의 위치를 저장하는 리스트
    

    arrow_image1 = Arrow.get_arrow_icon(width=25, height=10)
    if not arrow_image1:
        print("Unable to load arrow image!")

    my_image = Image.new("RGB", (joystick.width, joystick.height))
    my_draw = ImageDraw.Draw(my_image)

    new_monster = Monster(480, character.position, "../newGameasset")
    monsters.append(new_monster)

    if new_monster.position[0] <= 0:
        spawn_indicators.append((time.time(), (10, int(new_monster.center[1])), "left"))
    elif new_monster.position[0] >= 480 - new_monster.width:
        spawn_indicators.append((time.time(), (460, int(new_monster.center[1])), "right"))

    while True:
        frame_start_time = time.time()
        current_time = time.time()

        elapsed_time = frame_start_time - start_time
        remaining_time = max(0, countdown_time - int(elapsed_time))
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        timer_text = f"{minutes:02}:{seconds:02}"

        if remaining_time <= 0:
            print("Game Clear!")
            break

        if current_time - last_spawn_time >= spawn_interval:
            new_monster = Monster(480, character.position, "../newGameasset")
            monsters.append(new_monster)
            last_spawn_time = current_time
            if new_monster.position[0] <= 0:
                spawn_indicators.append((current_time, (10, int(new_monster.center[1])), "left"))
            elif new_monster.position[0] >= 480 - new_monster.width:
                spawn_indicators.append((current_time, (460, int(new_monster.center[1])), "right"))

        command = {'move': False, 'up_pressed': False, 'down_pressed': False, 'left_pressed': False, 'right_pressed': False}

        if not joystick.button_U.value:
            command['up_pressed'] = True
            command['move'] = True
        if not joystick.button_D.value:
            command['down_pressed'] = True
            command['move'] = True
        if not joystick.button_L.value:
            command['left_pressed'] = True
            command['move'] = True
        if not joystick.button_R.value:
            command['right_pressed'] = True
            command['move'] = True
        if not joystick.button_B.value:
            command['B_button'] = True
        if not joystick.button_A.value:
            command['A_button'] = True

        character.move(command)
        character.update_state(command)
        character.update_arrows()

        background.update_scroll(character.position)

        view = background.get_view()
        tile_view = background.get_tile_view()

        my_image.paste(view, (0, 0))
        my_image.paste(tile_view, (0, 0), tile_view)

        max_health = character.max_health
        current_health = character.health

        bar_x, bar_y = 10, 10
        bar_width, bar_height = 100, 10

        my_draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill="gray")
        current_bar_width = int(bar_width * (current_health / max_health))
        my_draw.rectangle([bar_x, bar_y, bar_x + current_bar_width, bar_y + bar_height], fill="green")

        arrow_x, arrow_y = 10, 35
        if arrow_image1:
            my_image.paste(arrow_image1, (arrow_x, arrow_y), arrow_image1)
        my_draw.text((arrow_x + 25, arrow_y + 5), f"x {character.arrow_count}", fill="black", font=font)

        for spawn_time, position, direction in spawn_indicators:
            if current_time - spawn_time < spawn_indicator_duration:
                higher_position = (position[0], position[1] - 80)
                my_draw.text(higher_position, "!", fill="red", font=font1)

        spawn_indicators = [
            (spawn_time, position, direction)
            for spawn_time, position, direction in spawn_indicators
            if current_time - spawn_time < spawn_indicator_duration
        ]

        my_draw.text((130, 10), timer_text, fill="black", font=font)

        character_image = character.get_current_image()
        if character_image:
            char_x1 = int(character.center[0] - character.width // 2 - background.scroll_x)
            char_y1 = int(character.center[1] - character.height // 2 - background.scroll_y)
            my_image.paste(character_image, (char_x1, char_y1), character_image)

        for monster in monsters:
            monster.update_state(character.center)
            monster.move_towards_character(character.center)

            distance_to_player = np.linalg.norm(monster.center - character.center)
            if distance_to_player < 25 and monster.state == 'attack':
                monster.attack_player(character)
            if monster.state == 'die' and not monster.is_alive:
                print("drop")
                dropped_positions = monster.drop_arrows()  # 드롭된 화살 위치 리스트 반환
                dropped_arrows_positions.extend(dropped_positions)  # 화살 위치 추가
                continue
            monster_image = monster.get_current_image()
            if monster_image:
                monster_x1 = int(monster.center[0] - monster.width // 2 - background.scroll_x)
                monster_y1 = int(monster.center[1] - monster.height // 2 - background.scroll_y)
                my_image.paste(monster_image, (monster_x1, monster_y1), monster_image)

        monsters = [monster for monster in monsters if monster.is_alive]

        my_draw = ImageDraw.Draw(my_image)
        for monster in monsters:
            distance = np.linalg.norm(character.center - monster.center)
            if character.state == "attack" and distance < 30:
                if not monster.state == 'die':
                    monster.take_damage(50, character.center)

            for arrow in character.get_arrows():
                if arrow.is_active():
                    arrow_pos = np.array(arrow.get_position())
                    arrow_distance = np.linalg.norm(arrow_pos - monster.center)
                    if arrow_distance < 10:
                        monster.take_damage(50, character.center,arrow=arrow)
                        arrow.active = False

        for monster in monsters:
            if monster.health > 0:
                monster.draw_health_bar(my_draw, background.scroll_x, background.scroll_y)

        for arrow in character.get_arrows():
            if arrow.is_active():
                arrow_image = arrow.get_current_image()
                arrow_pos = arrow.get_position()
                arrow_x = int(arrow_pos[0] - background.scroll_x)
                arrow_y = int(arrow_pos[1] - background.scroll_y)
                my_image.paste(arrow_image, (arrow_x, arrow_y), arrow_image)
        for arrow_pos in dropped_arrows_positions:
            
            drop_image = Arrow.get_arrow_icon(width=25, height=15)  # 드롭된 화살 이미지 가져오기
            if drop_image:
                
                arrow_x = int(arrow_pos[0] - background.scroll_x)
                arrow_y = int(arrow_pos[1] - background.scroll_y)
                my_image.paste(drop_image, (arrow_x, arrow_y), drop_image)  # 드롭된 화살 이미지 그리기
            distance_to_arrow = np.linalg.norm(character.center - arrow_pos)
            if distance_to_arrow < 15:  # 특정 거리 내에 들어오면 화살을 주울 수 있음 (15 픽셀)
                print("캐릭터가 화살을 주웠습니다.")  # 디버깅 로그
                character.arrow_count += 1  # 캐릭터의 화살 개수 증가

        # NumPy 배열을 리스트에서 제거하기 위해 수동으로 탐색
                for idx, pos in enumerate(dropped_arrows_positions):
                    if np.array_equal(pos, arrow_pos):
                        del dropped_arrows_positions[idx]  # 해당 위치를 안전하게 제거
                        break

            

        
        joystick.disp.image(my_image)

        elapsed_time = time.time() - frame_start_time
        time_to_sleep = max(0, frame_duration - elapsed_time)
        time.sleep(time_to_sleep)

        if character.health <= 0:
            display_game_over_screen(joystick, background)
            character.health = character.max_health
            character.arrow_count = 10
            monsters = []
            start_time = time.time()

def main():
    joystick = Joystick()
    background = Background()
    FPS = 12

    Gamestart.display_start_screen(joystick, background)
    start_game(FPS, joystick, background)

if __name__ == '__main__':
    main()
