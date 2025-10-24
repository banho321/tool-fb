# utils.py
"""
Module này chứa các hàm tiện ích (helper functions) được sử dụng chung trong toàn bộ ứng dụng.

Chức năng:
- random_delay(): Dừng chương trình trong một khoảng thời gian ngẫu nhiên.
- human_scroll(): Cuộn trang một cách tự nhiên hơn, mô phỏng người dùng.

Ai gọi:
- scraper.py: Gọi các hàm này để mô phỏng hành vi người dùng và tránh bị phát hiện.
"""
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def random_delay(min_seconds=5, max_seconds=15):
    """
    Hàm này làm gì: Tạm dừng thực thi của chương trình trong một khoảng thời gian
    ngẫu nhiên giữa min_seconds và max_seconds.
    Ai gọi nó: scraper.py, sau mỗi hành động quan trọng (ví dụ: login, comment, scroll).
    Input:
        - min_seconds (float): Thời gian chờ tối thiểu.
        - max_seconds (float): Thời gian chờ tối đa.
    Output: Không có.
    """
    delay = random.uniform(min_seconds, max_seconds)
    print(f"--- Tạm dừng {delay:.2f} giây để giả lập hành vi người dùng ---")
    time.sleep(delay)

def human_scroll(driver):
    """
    Hàm này làm gì: Thực hiện việc cuộn trang xuống một cách từ từ và ngẫu nhiên,
    giống như cách một người dùng thật sẽ làm, thay vì cuộn tức thì.
    Ai gọi nó: scraper.py, trong lúc quét nhóm để tải thêm bài viết.
    Input:
        - driver: Instance của Selenium WebDriver.
    Output: Không có.
    """
    # Lấy chiều cao hiện tại của trang
    last_height = driver.execute_script("return document.body.scrollHeight")

    # Cuộn xuống một đoạn ngẫu nhiên
    scroll_increment = random.randint(300, 600)
    driver.execute_script(f"window.scrollBy(0, {scroll_increment});")

    random_delay(1, 3) # Chờ một chút sau khi cuộn

    # Kiểm tra xem có cần cuộn hết trang không (ví dụ)
    # new_height = driver.execute_script("return document.body.scrollHeight")
    # if new_height == last_height:
    #     # Nếu không có nội dung mới, có thể dừng lại
    #     print("Đã cuộn đến cuối trang.")
    #     return False
    # return True

def simulate_typing(element, text):
    """
    Hàm này làm gì: Giả lập hành vi gõ phím của người dùng vào một element.
    Thay vì điền ngay lập tức, hàm này sẽ gõ từng ký tự với một độ trễ nhỏ.
    Ai gọi nó: scraper.py, khi cần điền thông tin đăng nhập hoặc viết bình luận.
    Input:
        - element: WebElement của Selenium (ví dụ: input box).
        - text (str): Nội dung cần gõ.
    Output: Không có.
    """
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(0.05, 0.2)) # Trễ ngẫu nhiên giữa các lần gõ phím
