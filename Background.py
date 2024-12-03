from PIL import Image
import os

class Background:
    def __init__(self):
        base_path = os.path.join(os.path.dirname(__file__), "../newGameasset/background")
        
        # 배경 이미지 로드
        self.main_background = Image.open(os.path.join(base_path, "Test_background.png"))
        self.tile_layer = Image.open(os.path.join(base_path, "Test_background_layer2.png"))
        
        self.view_width = 240
        self.view_height = 240
        self.map_width, self.map_height = self.main_background.size
        self.scroll_x = 0
        self.scroll_y = 0

    def update_scroll(self, character_position):
        # 캐릭터가 화면 끝부분에 도달했을 때만 스크롤 위치를 업데이트
        left_threshold = self.scroll_x + 0.4 * self.view_width
        right_threshold = self.scroll_x + 0.6 * self.view_width

        # 왼쪽 20% 경계에 도달했을 때
        if character_position[0] < left_threshold:
            self.scroll_x = max(0, character_position[0] - 0.4 * self.view_width)
        
        # 오른쪽 80% 경계에 도달했을 때
        elif character_position[0] > right_threshold:
            self.scroll_x = min(self.map_width - self.view_width, character_position[0] - 0.6 * self.view_width)

    def get_view(self):
        # 현재 스크롤 위치에 따른 화면에 보이는 배경 부분을 잘라서 반환
        view = self.main_background.crop((int(self.scroll_x), int(self.scroll_y),
                                          int(self.scroll_x + self.view_width),
                                          int(self.scroll_y + self.view_height)))
        return view

    def get_tile_view(self):
        # 타일 레이어 부분도 동일하게 잘라내기
        tile_view = self.tile_layer.crop((int(self.scroll_x), int(self.scroll_y),
                                          int(self.scroll_x + self.view_width),
                                          int(self.scroll_y + self.view_height)))
        return tile_view
