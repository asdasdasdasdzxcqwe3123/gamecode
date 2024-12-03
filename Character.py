from Arrow import Arrow
import numpy as np
import os
from PIL import Image
import time

class Character:
    def __init__(self, width, height):
        # 캐릭터 크기를 현재보다 2배로 설정
        self.width = 38  # 기존보다 2배 크기
        self.height = 40  # 기존보다 2배 크기
        self.position = np.array([width // 2 - self.width // 2, height - self.height - 32, 
                                  width // 2 + self.width // 2, height - 32])  # 화면 하단 타일 위에 위치
        self.center = np.array([(self.position[0] + self.position[2]) / 2, (self.position[1] + self.position[3]) / 2])
        self.state = 'idle'
        self.load_images()
        self.max_health = 100  # 최대 체력
        self.health = 100  # 현재 체력
        self.current_frame = 0
        self.flip_image = False  # 왼쪽으로 이동 시 이미지를 반전
        self.arrows = []  # 발사된 화살을 저장할 리스트
        self.arrow_fired = False  # 화살 발사 여부 추적

        self.arrow_count = 10  # 초기 화살 개수

        self.is_jumping = False
        self.is_falling = False
        self.jump_height = 40  # 점프 높이
        self.jump_speed = 5  # 점프 속도
        self.jump_target_y = None  # 목표 y 위치 저장
        self.ground_y = self.position[1]  # 지면 y 위치 저장

        self.is_attackable = False  # 피격 상태 활성화 여부
        self.attackable_start_time = None  # 피격 상태 시작 시간
        self.attackable_duration = 0.5  # 피격 애니메이션 지속 시간 (초)

    def load_images(self):
        base_path = "../newGameasset"  # 상대 경로 설정
        valid_extensions = (".png", ".jpg", ".jpeg")  # 이미지 확장자만 허용

    # 각 동작 폴더의 이미지 파일만 오름차순으로 로드
        def sort_key(filename):
        # 파일 이름에서 숫자 추출 (예: "Hero_pull_bow_0.png" -> 0)
            parts = filename.split('_')
            try:
                return int(parts[-1].split('.')[0])  # 숫자를 추출하여 정수로 변환
            except ValueError:
                return filename  # 숫자가 없는 경우 원래 이름으로 정렬

        self.images = {
                'run': [Image.open(os.path.join(base_path, "Run", img)).resize((self.width, self.height), Image.ANTIALIAS)
                    for img in sorted(os.listdir(os.path.join(base_path, "Run")), key=sort_key)
                    if img.endswith(valid_extensions)],
                'attack': [Image.open(os.path.join(base_path, "attack", img)).resize((self.width, self.height), Image.ANTIALIAS)
                   for img in sorted(os.listdir(os.path.join(base_path, "attack")), key=sort_key)
                   if img.endswith(valid_extensions)],
                'attackable': [Image.open(os.path.join(base_path, "attackable", img)).resize((self.width, self.height), Image.ANTIALIAS)
                    for img in sorted(os.listdir(os.path.join(base_path, "attackable")), key=sort_key)
                    if img.endswith(valid_extensions)],
                'pullbow': [Image.open(os.path.join(base_path, "pullbow", img)).resize((self.width, self.height), Image.ANTIALIAS)
                    for img in sorted(os.listdir(os.path.join(base_path, "pullbow")), key=sort_key)
                    if img.endswith(valid_extensions)]
    }

        # idle 상태도 리스트로 설정하여 문제가 발생하지 않도록 함
        if self.images['run']:
            self.images['idle'] = [self.images['run'][0]]
        else:
            self.images['idle'] = [Image.new("RGBA", (self.width, self.height), (255, 0, 0, 0))]  # 투명 배경 기본 이미지

    def get_current_image(self):
        # 현재 상태에 맞는 프레임 목록을 가져와 현재 프레임 이미지를 반환
        frames = self.images.get(self.state, [])
        if frames:
            image = frames[self.current_frame]
            # 왼쪽으로 이동할 때 이미지를 반전
            if self.flip_image:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
            return image
        return None  # 이미지가 없는 경우 None 반환

    def update_state(self, command):

        if self.is_attackable and time.time() - self.attackable_start_time > self.attackable_duration:
            self.is_attackable = False
            self.state = 'idle'  # 상태를 원래 상태로 복구
        if not self.is_attackable: 
            if command.get('move'):
                self.state = 'run'
            elif command.get('A_button'):
                self.state = 'attack'
            elif command.get('B_button'):
                self.state = 'pullbow'
                self.arrow_fired = False  # 새로 활을 당길 때마다 화살 발사 상태 초기화
            elif command.get('attacked'):
                self.state = 'attackable'
            else:
                self.state = 'idle'
        
        frames = self.images.get(self.state, [])
        
        if self.state == 'pullbow' and frames:
            # 15번째 프레임에서 화살을 발사하고 발사 상태를 `True`로 설정
            if self.current_frame == 11 and not self.arrow_fired:  # 11번째 인덱스는 14
                self.shoot_arrow()  # 화살 발사
                self.arrow_fired = True  # 화살이 발사되었음을 기록

        # 프레임 업데이트
        if frames:
            self.current_frame = (self.current_frame + 1) % len(frames) if self.state != 'idle' else 0

    def shoot_arrow(self):
    # 캐릭터 방향에 따라 화살의 시작 위치를 설정 (캐릭터보다 조금 앞에서 발사되도록)
        if self.arrow_count > 0:  # 화살 개수가 남아 있을 때만 발사
            self.arrow_count -= 1  # 화살 개수 감소
            offset_distance = 6  # 화살이 캐릭터 앞에서 발사될 거리
            direction = 1 if not self.flip_image else -1  # 캐릭터 방향에 따라 화살 방향 결정
            arrow_y_offset = -6  # 화살 y 위치를 캐릭터 중심에서 위로 이동

        # 화살의 시작 위치를 캐릭터 중심에서 offset 거리만큼 이동
            arrow_start_position = self.center + np.array([direction * offset_distance, arrow_y_offset])

        # 화살 생성 및 추가
            arrow = Arrow(arrow_start_position, direction)
            self.arrows.append(arrow)
        else:
            print("화살이 없습니다!")  # 디버그 메시지 출력

    def move(self, command):
        # 좌우 이동만 허용
        if command.get('left_pressed'):
            self.position[0] -= 5
            self.position[2] -= 5
            self.flip_image = True  # 왼쪽으로 이동 시 반전
            self.state = "run"  # 상태를 직접 설정

        elif command.get('right_pressed'):
            self.position[0] += 5
            self.position[2] += 5
            self.flip_image = False  # 오른쪽으로 이동 시 반전 해제
            self.state = "run"  # 상태를 직접 설정

        if command.get('up_pressed') and not self.is_jumping and not self.is_falling:
            self.is_jumping = True
            self.jump_target_y = self.position[1] - self.jump_height  # 목표 y 위치 설정
            self.state = "jump"  # 점프 상태 설정

        # 점프 중
        if self.is_jumping:
            if self.position[1] > self.jump_target_y:  # 위로 이동
                self.position[1] -= self.jump_speed
                self.position[3] -= self.jump_speed
            else:  # 목표 위치 도달 후 하강 상태로 전환
                self.is_jumping = False
                self.is_falling = True

        # 낙하 중
        if self.is_falling:
            if self.position[1] < self.ground_y:  # 아래로 이동
                self.position[1] += self.jump_speed
                self.position[3] += self.jump_speed
            else:  # 지면 도달
                self.position[1] = self.ground_y  # 정확히 지면에 위치
                self.position[3] = self.ground_y + self.height
                self.is_falling = False
                self.state = "idle"  # 상태 복귀
        self.center = np.array([(self.position[0] + self.position[2]) / 2,
                            (self.position[1] + self.position[3]) / 2])    

    def update_arrows(self):
        # 모든 화살 이동 및 비활성화된 화살 제거
        for arrow in self.arrows:
            arrow.move()
        self.arrows = [arrow for arrow in self.arrows if arrow.is_active()]

    def get_arrows(self):
        # 현재 활성화된 화살들 반환
        return self.arrows
    
    

    def take_damage(self, amount):
        # 체력을 감소시키고 최소값을 0으로 유지
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            print("플레이어가 죽었습니다!")
        else:
            # 피격 상태로 전환
            self.state = 'attackable'
            self.is_attackable = True
            self.attackable_start_time = time.time()

    def heal(self, amount):
        # 체력을 회복하고 최대 체력을 초과하지 않도록 유지
        self.current_health = min(self.max_health, self.current_health + amount)
