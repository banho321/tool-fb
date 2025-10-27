# test_comment.py
"""
Script này kiểm tra chức năng bình luận, sử dụng cookie để đăng nhập.
"""
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COMMENT_BOX_SELECTOR = "div[aria-label='Viết bình luận'], div[aria-label='Write a comment...']"
SUBMIT_BUTTON_SELECTOR = "div[aria-label='Gửi'], div[aria-label='Post']"

def load_test_config():
    with open("config.testing.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def login_with_cookie(driver, cookie_file):
    with open(cookie_file, 'r') as f:
        cookies = json.load(f)
    driver.get("https://www.facebook.com/")
    time.sleep(2)
    for cookie in cookies:
        if 'sameSite' not in cookie: cookie['sameSite'] = 'Lax'
        driver.add_cookie(cookie)
    driver.refresh()
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Home']")))
    return True

def test_comment():
    print("--- Bắt đầu kiểm tra chức năng bình luận (đăng nhập bằng cookie) ---")
    config = load_test_config()
    cookie_file = config["facebook_credentials"]["cookie_file_path"]
    post_url = config.get("test_post_url")
    firefox_binary_path = config.get("settings", {}).get("firefox_binary_path", "")

    driver = None
    try:
        options = webdriver.FirefoxOptions()
        if firefox_binary_path:
            options.binary_location = firefox_binary_path

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        print("1. Đang đăng nhập bằng cookie...")
        login_with_cookie(driver, cookie_file)

        print(f"2. Đang truy cập bài viết: {post_url}")
        driver.get(post_url)
        time.sleep(5)

        print(f"3. Đang tìm ô bình luận với selector: '{COMMENT_BOX_SELECTOR}'")
        comment_box = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, COMMENT_BOX_SELECTOR)))
        comment_box.click()
        time.sleep(1)

        print("4. Đang gõ nội dung test...")
        actual_input = driver.switch_to.active_element
        actual_input.send_keys("Đây là một bình luận thử nghiệm tự động.")
        time.sleep(2)

        print(f"5. Đang tìm nút gửi với selector: '{SUBMIT_BUTTON_SELECTOR}'")
        submit_button = driver.find_element(By.CSS_SELECTOR, SUBMIT_BUTTON_SELECTOR)

        print("\nSUCCESS: Tất cả các phần tử để bình luận đều được tìm thấy!")

    except Exception as e:
        print(f"\nERROR: Đã có lỗi xảy ra: {e}")
    finally:
        if driver:
            print("\nTrình duyệt sẽ tự đóng sau 10 giây.")
            time.sleep(10)
            driver.quit()
        print("\n--- Kết thúc kiểm tra ---")

if __name__ == "__main__":
    test_comment()
