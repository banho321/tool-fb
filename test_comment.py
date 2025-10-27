# test_comment.py
"""
Script này dùng để kiểm tra riêng lẻ chức năng BÌNH LUẬN vào một bài viết cụ thể.
"""
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

COMMENT_BOX_SELECTOR = "div[aria-label='Viết bình luận'], div[aria-label='Write a comment...']"
SUBMIT_BUTTON_SELECTOR = "div[aria-label='Gửi'], div[aria-label='Post']"

def load_test_config():
    """Tải cấu hình từ file config.testing.json."""
    try:
        with open("config.testing.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'config.testing.json'.")
        return None
    return None

def login(driver, email, password):
    """Hàm phụ trợ để đăng nhập."""
    driver.get("https://www.facebook.com/")
    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='cookie-policy-manage-dialog-accept-button']"))).click()
    except TimeoutException: pass

    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.NAME, "login").click()

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
    print("Đăng nhập thành công.")
    return True

def test_comment():
    """Hàm chính để kiểm tra chức năng bình luận."""
    print("--- Bắt đầu kiểm tra chức năng bình luận ---")
    config = load_test_config()
    if not config: return

    creds = config.get("facebook_credentials", {})
    post_url = config.get("test_post_url")
    chrome_binary_path = config.get("settings", {}).get("chrome_binary_path", "")

    if not post_url or "your_post_id" in post_url:
        print("Lỗi: Vui lòng cập nhật `test_post_url` trong 'config.testing.json'.")
        return

    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        if chrome_binary_path:
            options.binary_location = chrome_binary_path
            print(f"Sử dụng Chrome binary từ: {chrome_binary_path}")

        options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        print("1. Đang đăng nhập...")
        login(driver, creds["email"], creds["password"])
        time.sleep(2)

        print(f"2. Đang truy cập bài viết: {post_url}")
        driver.get(post_url)
        time.sleep(5)

        print(f"3. Đang tìm ô bình luận với selector: '{COMMENT_BOX_SELECTOR}'")
        comment_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, COMMENT_BOX_SELECTOR))
        )
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
        print(f"\nERROR: Đã có lỗi xảy ra trong quá trình test bình luận: {e}")
        print("Mẹo: Nếu lỗi là 'cannot find Chrome binary', hãy thử điền đường dẫn Chrome vào 'chrome_binary_path' trong file config.testing.json.")
    finally:
        if driver:
            print("\nTrình duyệt sẽ tự đóng sau 10 giây.")
            time.sleep(10)
            driver.quit()
        print("--- Kết thúc kiểm tra ---")

if __name__ == "__main__":
    test_comment()
