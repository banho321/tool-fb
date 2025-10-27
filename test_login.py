# test_login.py
"""
Script này kiểm tra chức năng đăng nhập bằng COOKIE.
"""
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_test_config():
    with open("config.testing.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def test_login_with_cookie():
    print("--- Bắt đầu kiểm tra đăng nhập bằng cookie ---")
    config = load_test_config()
    cookie_file = config["facebook_credentials"]["cookie_file_path"]
    firefox_binary_path = config.get("settings", {}).get("firefox_binary_path", "")

    driver = None
    try:
        options = webdriver.FirefoxOptions()
        if firefox_binary_path:
            options.binary_location = firefox_binary_path

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        with open(cookie_file, 'r') as f:
            cookies = json.load(f)

        driver.get("https://www.facebook.com/")
        time.sleep(2)
        for cookie in cookies:
            if 'sameSite' not in cookie:
                cookie['sameSite'] = 'Lax'
            driver.add_cookie(cookie)

        print("1. Đã inject cookie. Đang tải lại trang...")
        driver.refresh()

        print("2. Đang chờ xác nhận đăng nhập...")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Home']")))

        print("\nSUCCESS: Đăng nhập bằng cookie thành công!")

    except Exception as e:
        print(f"\nERROR: Đã xảy ra lỗi: {e}")
        print("Mẹo: Hãy chắc chắn file cookie còn hạn và đúng định dạng. Thử xuất lại file cookie từ trình duyệt.")
    finally:
        if driver:
            print("Trình duyệt sẽ tự đóng sau 5 giây.")
            time.sleep(5)
            driver.quit()
        print("--- Kết thúc kiểm tra ---")

if __name__ == "__main__":
    test_login_with_cookie()
