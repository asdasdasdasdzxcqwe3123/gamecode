from PIL import Image, ImageDraw, ImageFont
import time
import os

font_path = os.path.join(os.path.dirname(__file__), "../pixelpont/PressStart2P-Regular.ttf")
font_size = 10
font_size_large = 40

# 폰트 로드
try:
    font = ImageFont.truetype(font_path, font_size)
    font_large = ImageFont.truetype(font_path, font_size_large)
except IOError:
    print(f"폰트 로드 실패: {font_path}. 기본 폰트를 사용합니다.")
    font = ImageFont.load_default()
    font_large = ImageFont.load_default()

def display_start_screen(joystick, background):
    blink = True  # 깜빡임 상태
    last_blink_time = time.time()  # 마지막으로 깜빡임 상태를 변경한 시간
    blink_interval = 0.5  # 깜빡임 간격 (초)

    while True:
        # 새 이미지 생성
        my_image = Image.new("RGB", (joystick.width, joystick.height))
        my_draw = ImageDraw.Draw(my_image)

        # 배경화면 가져오기
        view = background.get_view()
        my_image.paste(view, (0, 0))

        # 텍스트 추가
        my_draw.text((35, 50), "5MIN", fill="black", font=font_large)
        if blink:  # 깜빡임 상태에 따라 텍스트 표시
            my_draw.text((35, 150), "Click Any Button", fill="white", font=font)

        # 화면 갱신
        joystick.disp.image(my_image)

        # 깜빡임 상태 변경
        current_time = time.time()
        if current_time - last_blink_time > blink_interval:
            blink = not blink
            last_blink_time = current_time

        # 버튼 입력 확인
        if not joystick.button_U.value or not joystick.button_D.value or \
           not joystick.button_L.value or not joystick.button_R.value or \
           not joystick.button_A.value or not joystick.button_B.value:
            break

        time.sleep(0.1)
