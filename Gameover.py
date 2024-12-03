from PIL import Image, ImageDraw, ImageFont
import time
import os

font_path = os.path.join(os.path.dirname(__file__), "../pixelpont/PressStart2P-Regular.ttf")
font_size_title = 40  # 제목 글씨 크기
font_size_subtitle = 12  # 서브텍스트 글씨 크기

# 폰트 로드
try:
    font_title = ImageFont.truetype(font_path, font_size_title)
    font_subtitle = ImageFont.truetype(font_path, font_size_subtitle)
except IOError:
    print(f"폰트 로드 실패: {font_path}. 기본 폰트를 사용합니다.")
    font_title = ImageFont.load_default()
    font_subtitle = ImageFont.load_default()

def display_game_over_screen(joystick, background):
    flash_text = True  # 텍스트 깜빡임 상태
    flash_interval = 0.5  # 텍스트 깜빡임 간격 (초)

    while True:
        # 새 이미지 생성
        my_image = Image.new("RGB", (joystick.width, joystick.height))
        my_draw = ImageDraw.Draw(my_image)

        # 배경화면 가져오기
        view = background.get_view()
        my_image.paste(view, (0, 0))

        # "Game Over" 텍스트 추가
        my_draw.text((50, 50), "Game", fill="red", font=font_title)
        my_draw.text((50, 100), "Over", fill="red", font=font_title)

        # "Try Again / Click Any Button" 텍스트 추가 (깜빡임)
        if flash_text:
            my_draw.text((40, 180), "Try Again", fill="white", font=font_subtitle)
            my_draw.text((20, 210), "Click Any Button", fill="white", font=font_subtitle)

        # 화면 갱신
        joystick.disp.image(my_image)

        # 버튼 입력 확인
        if not joystick.button_U.value or not joystick.button_D.value or \
           not joystick.button_L.value or not joystick.button_R.value or \
           not joystick.button_A.value or not joystick.button_B.value:
            break  # 버튼이 눌리면 루프 종료

        # 텍스트 깜빡임
        flash_text = not flash_text
        time.sleep(flash_interval)
