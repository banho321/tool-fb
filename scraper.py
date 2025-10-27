# scraper.py
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
from PyQt6.QtCore import QObject, pyqtSignal
from utils import random_delay, human_scroll, simulate_typing
from logger import logger

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
        self.commented_posts = set()

    def _init_driver(self):
        try:
            options = webdriver.FirefoxOptions()
            if self.config["settings"]["headless"]:
                options.add_argument("--headless")

            firefox_binary_path = self.config.get("settings", {}).get("firefox_binary_path", "")
            if firefox_binary_path:
                options.binary_location = firefox_binary_path

            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            return True
        except Exception as e:
            self.log_signal.emit("ERROR", f"Không thể khởi tạo WebDriver (Firefox): {e}")
            return False

    def login_facebook_with_cookies(self):
        if not self._init_driver(): return False
        cookie_file = self.config["facebook_credentials"]["cookie_file_path"]
        try:
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
            self.driver.get("https://www.facebook.com/")
            time.sleep(2)
            for cookie in cookies:
                if 'sameSite' not in cookie: cookie['sameSite'] = 'Lax'
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[aria-label='Home']")))
            self.log_signal.emit("SUCCESS", "Đăng nhập bằng cookie thành công!")
            return True
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi khi đăng nhập bằng cookie: {e}")
            return False

    def run(self):
        self.log_signal.emit("INFO", "Bắt đầu tiến trình...")
        self.status_signal.emit("Đang chạy...")
        try:
            if not self.login_facebook_with_cookies():
                self.log_signal.emit("ERROR", "Đăng nhập thất bại. Dừng tiến trình.")
                return

            while self._is_running:
                self.log_signal.emit("INFO", "Bắt đầu chu kỳ quét mới...")
                for group_url in self.config["groups"]:
                    if not self._is_running: break
                    self.handle_pause()
                    self.scan_group(group_url)
                    random_delay(10, 20) # Nghỉ giữa các nhóm

                if self._is_running:
                    self.log_signal.emit("INFO", "Hoàn thành chu kỳ quét. Tạm nghỉ 1 giờ.")
                    for _ in range(3600):
                        if not self._is_running: break
                        time.sleep(1)
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi nghiêm trọng trong vòng lặp chính: {e}")
        finally:
            self.quit_driver()
            self.status_signal.emit("Đã dừng")
            self.finished_signal.emit()

    def scan_group(self, group_url):
        try:
            self.driver.get(group_url)
            self.log_signal.emit("INFO", f"Đang quét nhóm: {group_url}")
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
            for _ in range(self.config["settings"]["max_posts_per_group"] // 2):
                if not self._is_running: return
                human_scroll(self.driver)
                random_delay(2, 5)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            posts = soup.select("div.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z")
            if not posts:
                self.log_signal.emit("WARNING", "Không tìm thấy bài viết nào với selector hiện tại.")
                return
            for post in posts[:self.config["settings"]["max_posts_per_group"]]:
                if not self._is_running: return
                self.handle_pause()
                self.process_post(post)
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi khi quét nhóm {group_url}: {e}")

    def process_post(self, post_element):
        try:
            post_text_element = post_element.select_one("div[data-ad-preview='message'], .x1iorvi4")
            post_text = post_text_element.text.lower() if post_text_element else ""
            post_link_element = post_element.find("a", href=lambda href: href and "/permalink/" in href)
            post_url = "https://facebook.com" + post_link_element['href'] if post_link_element else f"unknown_{random.randint(1,9999)}"
            if post_url in self.commented_posts: return

            for product in self.config["products"]:
                keywords = [kw.strip().lower() for kw in product["keywords"].split(",") if kw.strip()]
                if any(keyword in post_text for keyword in keywords):
                    self.log_signal.emit("SUCCESS", f"Tìm thấy keyword cho '{product['name']}' trong bài viết: {post_url}")
                    if not self.config["settings"]["test_mode"]:
                        self.post_comment(post_url, product["link"])
                    else:
                        self.log_signal.emit("INFO", f"[TEST MODE] Giả lập bình luận link: {product['link']}")
                    self.commented_posts.add(post_url)
                    random_delay(15, 30)
                    break
        except Exception as e:
            self.log_signal.emit("WARNING", f"Lỗi khi xử lý bài viết: {e}")

    def post_comment(self, post_url, comment_text):
        try:
            self.driver.get(post_url)
            random_delay(5, 8)
            comment_box = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Viết bình luận']")))
            comment_box.click()
            random_delay(1, 2)
            actual_input = self.driver.switch_to.active_element
            simulate_typing(actual_input, comment_text)
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "div[aria-label='Gửi']")
            submit_button.click()
            self.log_signal.emit("SUCCESS", f"Đã bình luận thành công: {post_url}")
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi khi bình luận: {e}")

    def quit_driver(self):
        if self.driver:
            self.driver.quit()

    def stop(self): self._is_running = False
    def pause(self): self._is_paused = True; self.status_signal.emit("Đã tạm dừng")
    def resume(self): self._is_paused = False; self.status_signal.emit("Đang chạy...")
    def handle_pause(self):
        while self._is_paused:
            if not self._is_running: break
            time.sleep(1)
