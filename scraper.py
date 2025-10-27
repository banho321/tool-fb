# scraper.py
"""
Module này chứa lớp FacebookScraper, là nơi thực hiện tất cả các logic nghiệp vụ chính.
"""

import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from PyQt6.QtCore import QObject, pyqtSignal

from utils import random_delay, human_scroll, simulate_typing
from logger import logger

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
]

def get_proxies():
    try:
        with open("proxies.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

class FacebookScraper(QObject):
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.driver = None
        self._is_running = True
        self._is_paused = False
        self.proxies = get_proxies()
        self.current_proxy_index = 0
        self.commented_posts = set()

    def _init_driver(self):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--disable-notifications")
            if self.config["settings"]["headless"]:
                options.add_argument("--headless")

            chrome_binary_path = self.config.get("settings", {}).get("chrome_binary_path", "")
            if chrome_binary_path:
                options.binary_location = chrome_binary_path
                self.log_signal.emit("INFO", f"Sử dụng Chrome binary từ: {chrome_binary_path}")

            options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
            if self.proxies:
                proxy = self.proxies[self.current_proxy_index]
                options.add_argument(f'--proxy-server={proxy}')
                self.log_signal.emit("INFO", f"Sử dụng proxy: {proxy}")
                self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)

            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except Exception as e:
            self.log_signal.emit("ERROR", f"Không thể khởi tạo WebDriver: {e}")
            self.log_signal.emit("ERROR", "Nếu lỗi là 'cannot find Chrome binary', hãy thử điền đường dẫn Chrome vào file config.json.")
            return False

    def login_facebook(self):
        if not self._init_driver(): return False
        try:
            self.driver.get("https://www.facebook.com/")
            random_delay(2, 4)

            try:
                cookie_button = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='cookie-policy-manage-dialog-accept-button']")))
                cookie_button.click()
            except TimeoutException:
                pass

            email_field = self.driver.find_element(By.ID, "email")
            pass_field = self.driver.find_element(By.ID, "pass")
            simulate_typing(email_field, self.config["facebook_credentials"]["email"])
            simulate_typing(pass_field, self.config["facebook_credentials"]["password"])

            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()

            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
            self.log_signal.emit("SUCCESS", "Đăng nhập thành công!")
            return True
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi không xác định khi đăng nhập: {e}")
            return False

    def scan_group(self, group_url):
        try:
            self.driver.get(group_url)
            self.log_signal.emit("INFO", f"Đang tải bài viết trong nhóm: {group_url}")
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))

            for _ in range(self.config["settings"]["max_posts_per_group"] // 2):
                if not self._is_running: return
                human_scroll(self.driver)
                random_delay(2, 5)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            post_selector = "div.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z" # Selector từ test script
            posts = soup.select(post_selector)

            if not posts:
                self.log_signal.emit("WARNING", f"Không tìm thấy bài viết nào trong {group_url} với selector hiện tại.")
                return

            self.log_signal.emit("INFO", f"Tìm thấy {len(posts)} bài viết. Bắt đầu phân tích.")
            for post in posts[:self.config["settings"]["max_posts_per_group"]]:
                 if not self._is_running: return
                 self.handle_pause()
                 self.process_post(post)

        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi khi quét nhóm {group_url}: {e}")

    def process_post(self, post_element):
        try:
            content_selector = "div[data-ad-preview='message'], .x1iorvi4.x1pi30zi.x1l90r2v.x1swvt13"
            post_text_element = post_element.select_one(content_selector)
            post_text = post_text_element.text.lower() if post_text_element else ""

            post_link_element = post_element.find("a", href=lambda href: href and "/permalink/" in href)
            post_url = "https://facebook.com" + post_link_element['href'] if post_link_element else f"unknown_post_{random.randint(1000,9999)}"

            if post_url in self.commented_posts:
                return

            for product in self.config["products"]:
                keywords = [kw.strip().lower() for kw in product["keywords"].split(",")]
                if any(keyword in post_text for keyword in keywords if keyword):
                    self.log_signal.emit("SUCCESS", f"Tìm thấy keyword cho '{product['name']}' trong bài viết: {post_url}")

                    if not self.config["settings"]["test_mode"]:
                        self.post_comment(post_url, product["link"])
                    else:
                        self.log_signal.emit("INFO", f"[CHẾ ĐỘ THỬ NGHIỆM] Giả lập bình luận link: {product['link']}")

                    self.commented_posts.add(post_url)
                    random_delay(15, 30)
                    break

        except Exception as e:
            self.log_signal.emit("WARNING", f"Không thể xử lý một bài viết: {e}")

    def post_comment(self, post_url, comment_text):
        self.log_signal.emit("INFO", f"Điều hướng đến bài viết để bình luận: {post_url}")
        self.driver.get(post_url)
        random_delay(5, 8)

        try:
            comment_box_selector = "div[aria-label='Viết bình luận'], div[aria-label='Write a comment...']"
            comment_box = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, comment_box_selector)))

            comment_box.click()
            random_delay(1, 2)

            actual_input = self.driver.switch_to.active_element
            simulate_typing(actual_input, comment_text)

            submit_button_selector = "div[aria-label='Gửi'], div[aria-label='Post']"
            submit_button = self.driver.find_element(By.CSS_SELECTOR, submit_button_selector)
            submit_button.click()

            self.log_signal.emit("SUCCESS", f"Đã bình luận thành công vào bài viết: {post_url}")
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi khi bình luận: {e}")

    def run(self):
        self.log_signal.emit("INFO", "Bắt đầu quá trình scraping...")
        self.status_signal.emit("Đang chạy...")
        try:
            if not self.login_facebook():
                self.log_signal.emit("ERROR", "Đăng nhập thất bại. Dừng tiến trình.")
                return
            while self._is_running:
                for group_url in self.config["groups"]:
                    if not self._is_running: break
                    self.handle_pause()
                    self.scan_group(group_url)
                    random_delay(10, 20)
                if self._is_running:
                    self.log_signal.emit("INFO", "Hoàn thành một chu kỳ quét. Tạm nghỉ 1 giờ.")
                    for _ in range(3600):
                        if not self._is_running: break
                        time.sleep(1)
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi không xác định trong vòng lặp chính: {e}")
        finally:
            self.quit_driver()
            self.status_signal.emit("Đã dừng")
            self.finished_signal.emit()

    def quit_driver(self):
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                self.log_signal.emit("ERROR", f"Lỗi khi đóng trình duyệt: {e}")

    def stop(self):
        self._is_running = False
        self._is_paused = False

    def pause(self):
        self._is_paused = True
        self.status_signal.emit("Đã tạm dừng")

    def resume(self):
        self._is_paused = False
        self.status_signal.emit("Đang chạy...")

    def handle_pause(self):
        while self._is_paused:
            if not self._is_running: break
            time.sleep(1)
