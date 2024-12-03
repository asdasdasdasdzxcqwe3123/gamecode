from PIL import Image
import os
import time
import numpy as np

class Arrow:
    # 클래스 변수로 이미지 캐싱
    images = []

    @classmethod
    def load_images(cls):
        if not cls.images:  # 이미지가 한 번도 로드되지 않은 경우에만 로드
            base_path = "../newGameasset"
            valid_extensions = (".png", ".jpg", ".jpeg")
            scale_factor = 2  # 화살 크기 조정 비율
            arrow_path = os.path.join(base_path, "Arrow")
            cls.images = []
            try:
                for img in sorted(os.listdir(arrow_path)):
                    if img.endswith(valid_extensions):
                        with Image.open(os.path.join(arrow_path, img)) as image:
                            resized_image = image.resize(
                                (int(image.width * scale_factor), int(image.height * scale_factor)),
                                Image.ANTIALIAS
                            )
                            cls.images.append(resized_image)
            except FileNotFoundError:
                print(f"Arrow images not found in {arrow_path}")

    @classmethod
    def get_arrow_icon(cls, width=20, height=20):
        cls.load_images()  # 이미지 로드
        if cls.images:
            # 첫 번째 이미지를 원하는 크기로 리사이즈
            return cls.images[0].resize((width, height), Image.ANTIALIAS)
        return None  # 이미지가 없으면 None 반환

    def __init__(self, start_position, direction):
        self.position = np.array(start_position, dtype=float)  # NumPy 배열 사용으로 벡터 연산 최적화
        self.direction = direction
        self.speed = 10
        self.active = True
        self.current_frame = 0
        self.start_time = time.time()

        Arrow.load_images()  # 클래스 이미지 로드

    def move(self):
        if not self.active:
            return

        # 일정 시간이 지나면 화살 비활성화
        if time.time() - self.start_time >= 1:
            self.active = False
            return

        # 위치 업데이트
        self.position[0] += self.speed * self.direction

        # 화면 경계를 벗어나면 비활성화
        if self.position[0] < 0 or self.position[0] > 480:
            self.active = False

        # 현재 프레임 업데이트
        if Arrow.images:
            self.current_frame = (self.current_frame + 1) % len(Arrow.images)

    def get_position(self):
        return tuple(self.position)

    def is_active(self):
        return self.active

    def get_current_image(self):
        if Arrow.images:
            return Arrow.images[self.current_frame]
        return None
    def drop(self, drop_position):
        """화살을 드롭 위치로 설정"""
        self.position = np.array(drop_position, dtype=float)  # 드롭 위치 설정
        self.active = False  # 드롭된 상태로 비활성화

    def check_collision(self, monster):
        """화살과 몬스터의 충돌 체크"""
        arrow_pos = self.position
        distance = np.linalg.norm(arrow_pos - np.array(monster.center))
        return distance < 5  # 충돌 기준 거리
