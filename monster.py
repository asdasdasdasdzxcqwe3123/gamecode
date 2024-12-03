import numpy as np
import os
from PIL import Image
import random
import time

class Monster:
    def __init__(self, screen_width, character_position, sprite_folder):
        self.width = 38
        self.height = 40
        self.position = self.spawn_position(screen_width, character_position)
        self.center = self.calculate_center()
        self.arrows_stuck = []
        self.state = 'move'
        self.is_alive = True
        self.load_images(sprite_folder)
        self.current_frame = 0
        self.flip_image = self.position[0] > screen_width // 2
        self.max_health = 100
        self.health = self.max_health
        self.speed = 1.2
        self.attack_cooldown = 1.0
        self.last_attack_time = 0

    def spawn_position(self, screen_width, character_position):
        spawn_y_top = character_position[1]
        spawn_y_bottom = character_position[3]
        side = random.choice(['left', 'right'])
        if side == 'left':
            return np.array([0, spawn_y_top, self.width, spawn_y_bottom], dtype=float)
        else:
            return np.array([screen_width - self.width, spawn_y_top, screen_width, spawn_y_bottom], dtype=float)

    def load_images(self, sprite_folder):
        base_path = sprite_folder
        valid_extensions = (".png", ".jpg", ".jpeg")

        def sort_key(filename):
            parts = filename.split('_')
            try:
                return int(parts[-1].split('.')[0])
            except ValueError:
                return filename

        self.images = {}
        states = ['move', 'attack', 'die']
        for state in states:
            state_path = os.path.join(base_path, f"zombie{state}")
            try:
                self.images[state] = [
                    Image.open(os.path.join(state_path, img)).resize((self.width, self.height), Image.ANTIALIAS)
                    for img in sorted(os.listdir(state_path), key=sort_key)
                    if img.endswith(valid_extensions)
                ]
            except FileNotFoundError:
                print(f"Images for state '{state}' not found in {state_path}")

    def get_current_image(self):
        frames = self.images.get(self.state, [])
        if frames:
            image = frames[self.current_frame]
            if self.flip_image:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            return image
        return None

    def update_state(self, character_position):
        distance = np.linalg.norm(self.center - character_position)

        if self.state == 'die':
            for arrow in self.arrows_stuck:
                arrow.drop(self.center)
            if self.current_frame < len(self.images['die']) - 1:
                self.current_frame += 1
            else:
                self.is_alive = False
            return

        if distance < 25:
            self.state = 'attack'
        elif self.health <= 0 and self.state != 'die':
            self.state = 'die'
            self.current_frame = 0
        else:
            self.state = 'move'

        if character_position[0] < self.center[0] and not self.flip_image:
            self.flip_image = True
        elif character_position[0] > self.center[0] and self.flip_image:
            self.flip_image = False

        frames = self.images.get(self.state, [])
        if frames and self.state != 'die':
            self.current_frame = (self.current_frame + 1) % len(frames)

    def move_towards_character(self, character_position):
        if self.state == 'move':
            direction = np.sign(character_position[0] - self.center[0])
            self.position[0] += direction * self.speed
            self.position[2] += direction * self.speed
            self.center = self.calculate_center()

    def draw_health_bar(self, draw, scroll_x, scroll_y):
        bar_width, bar_height = 25, 3
        bar_x = int(self.center[0] - bar_width / 2 - scroll_x)
        bar_y = int(self.position[1] - 10 - scroll_y)
        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], fill="gray")
        current_bar_width = int(bar_width * (self.health / self.max_health))
        draw.rectangle([bar_x, bar_y, bar_x + current_bar_width, bar_y + bar_height], fill="red")

    def attack_player(self, player):
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            player.take_damage(10)

    def take_damage(self, amount, player_position, knockback_distance=10, arrow=None):
        self.health -= amount
        if arrow:
            self.arrows_stuck.append(arrow)
            print(f"화살 추가됨: {arrow}. 현재 화살 개수: {len(self.arrows_stuck)}")
        direction = np.sign(self.center[0] - player_position[0])
        self.position[0] += direction * knockback_distance
        self.position[2] += direction * knockback_distance
        self.center = self.calculate_center()

        if self.health <= 0 and self.state != 'die':
            self.state = 'die'
            self.current_frame = 0
    def drop_arrows(self):
        """죽을 때 화살을 드롭"""
        if not self.arrows_stuck:
            return []  # 저장된 화살이 없으면 빈 리스트 반환

        dropped_positions = []
        for arrow in self.arrows_stuck:
            drop_position = self.center.copy()  # 몬스터 중심 위치에 화살 드롭
            drop_position[1] -= 10  # 드롭 위치의 y 좌표를 높이기 위해 값을 감소 (20픽셀 만큼 위로 이동)
            arrow.drop(drop_position)  # 화살 위치 설정
            dropped_positions.append(drop_position)
            print("moster get position")

        self.arrows_stuck = []  # 드롭 후 초기화
        return dropped_positions
    
    def calculate_center(self):
        return np.array([(self.position[0] + self.position[2]) / 2, (self.position[1] + self.position[3]) / 2], dtype=float)
