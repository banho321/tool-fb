# test_scan.py
"""
Script này kiểm tra chức năng quét nhóm VÀ so khớp từ khóa, sử dụng cookie để đăng nhập.
"""
import json
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

POST_SELECTOR = "div.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z" # Selector ví dụ

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
    print("Đăng nhập bằng cookie thành công.")
    return True

def check_keywords(post_text, products):
    post_text_lower = post_text.lower()
    for product in products:
        keywords = [kw.strip().lower() for kw in product.get("keywords", "").split(",") if kw.strip()]
        for keyword in keywords:
            if keyword in post_text_lower:
                print(f"    [MATCH FOUND!] -> Keyword: '{keyword}', Sản phẩm: '{product['name']}'")
                return True
    return False

def test_scan_and_match():
    print("--- Bắt đầu kiểm tra quét nhóm (đăng nhập bằng cookie) ---")
    config = load_test_config()
    cookie_file = config["facebook_credentials"]["cookie_file_path"]
    group_urls = config.get("groups", [])
    products = config.get("products", [])
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
            print("\nWARNING: Không tìm thấy bài viết nào.")
            return

        print(f"\nSUCCESS: Tìm thấy {len(posts)} bài viết. Bắt đầu phân tích:")
        for i, post in enumerate(posts):
            content_selector = "div[data-ad-preview='message'], .x1iorvi4.x1pi30zi.x1l90r2v.x1swvt13"
            post_text_element = post.select_one(content_selector)
            post_text = post_text_element.text.strip() if post_text_element else ""

            print(f"BÀI VIẾT #{i+1}: '{post_text[:100]}...'")
            check_keywords(post_text, products)

    except Exception as e:
        print(f"\nERROR: Đã có lỗi xảy ra: {e}")
    finally:
        if driver:
            driver.quit()
        print("\n--- Kết thúc kiểm tra ---")

if __name__ == "__main__":
    test_scan_and_match()
