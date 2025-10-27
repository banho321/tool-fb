# test_scan.py
"""
Script này dùng để kiểm tra chức năng quét nhóm, trích xuất dữ liệu,
VÀ kiểm tra logic so khớp từ khóa.
"""
import json
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException

POST_SELECTOR = "div.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z"

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

def check_keywords(post_text, products):
    """Kiểm tra từ khóa."""
    post_text_lower = post_text.lower()
    for product in products:
        keywords = [kw.strip().lower() for kw in product.get("keywords", "").split(",") if kw.strip()]
        for keyword in keywords:
            if keyword in post_text_lower:
                print(f"    [MATCH FOUND!] -> Keyword: '{keyword}', Sản phẩm: '{product['name']}'")
                return True
    return False

def test_scan_and_match():
    """Hàm chính để kiểm tra quét nhóm và so khớp từ khóa."""
    print("--- Bắt đầu kiểm tra quét nhóm, trích xuất VÀ so khớp từ khóa ---")
    config = load_test_config()
    if not config: return

    creds = config.get("facebook_credentials", {})
    group_urls = config.get("groups", [])
    products = config.get("products", [])
    chrome_binary_path = config.get("settings", {}).get("chrome_binary_path", "")

    if not group_urls or "your_public_test_group" in group_urls[0]:
        print("Lỗi: Vui lòng cập nhật group URL trong 'config.testing.json'.")
        return

    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        if chrome_binary_path:
            options.binary_location = chrome_binary_path
            print(f"Sử dụng Chrome binary từ: {chrome_binary_path}")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        print("1. Đang đăng nhập...")
        login(driver, creds["email"], creds["password"])
        time.sleep(2)

        target_group = group_urls[0]
        print(f"2. Đang truy cập nhóm: {target_group}")
        driver.get(target_group)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
        time.sleep(2)

        print("3. Đang cuộn trang...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))

        print("4. Đang trích xuất và kiểm tra từ khóa...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posts = soup.select(POST_SELECTOR)

        if not posts:
            print("\nWARNING: Không tìm thấy bài viết nào với selector hiện tại.")
            return

        print(f"\nSUCCESS: Tìm thấy {len(posts)} bài viết. Bắt đầu phân tích:")
        # ... (phần còn lại không đổi)

    except Exception as e:
        print(f"\nERROR: Đã có lỗi xảy ra trong quá trình quét: {e}")
        print("Mẹo: Nếu lỗi là 'cannot find Chrome binary', hãy thử điền đường dẫn Chrome vào 'chrome_binary_path' trong file config.testing.json.")
    finally:
        if driver:
            print("\n--- Kết thúc kiểm tra ---")
            driver.quit()

if __name__ == "__main__":
    test_scan_and_match()
