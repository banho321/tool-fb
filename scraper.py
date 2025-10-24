# scraper.py
"""
Module này chứa lớp FacebookScraper, là nơi thực hiện tất cả các logic nghiệp vụ chính
liên quan đến việc tương tác với Facebook.

Lớp FacebookScraper được thiết kế để chạy trong một luồng (thread) riêng biệt
để không làm đóng băng giao diện người dùng (GUI).

Chức năng chính:
- Khởi tạo và quản lý trình duyệt Selenium (ChromeDriver).
- Đăng nhập vào Facebook.
- Quét các nhóm được chỉ định.
- Trích xuất thông tin bài viết và bình luận.
- Đối chiếu nội dung với các từ khóa sản phẩm.
- Tự động đăng bình luận nếu tìm thấy sự trùng khớp.
- Quản lý các trạng thái: chạy, tạm dừng, dừng.
- Giao tiếp với luồng GUI thông qua cơ chế signals/slots của PyQt6.
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

# Danh sách User-Agents để xoay vòng
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
]

def get_proxies():
    """Đọc proxies từ file proxies.txt."""
    try:
        with open("proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        return proxies
    except FileNotFoundError:
        return []

# --- Cảnh báo quan trọng ---
print("CẢNH BÁO: Tự động hóa Facebook vi phạm Điều khoản dịch vụ của họ.")
print("Sử dụng cẩn thận và trên tài khoản thử nghiệm để tránh bị khóa tài khoản.")

class FacebookScraper(QObject):
    """
    Lớp chính xử lý việc scraping, kế thừa QObject để dùng signal.
    """
    # Signals để giao tiếp với GUI (luồng chính)
    log_signal = pyqtSignal(str, str) # level, message
    status_signal = pyqtSignal(str) # status message
    finished_signal = pyqtSignal() # Báo hiệu luồng đã kết thúc

    def __init__(self, config):
        """
        Hàm khởi tạo.
        Ai gọi: main.py khi người dùng nhấn nút "Start".
        Input: config (dict) - Toàn bộ cấu hình từ GUI.
        """
        super().__init__()
        self.config = config
        self.driver = None

        # Các cờ điều khiển trạng thái của luồng
        self._is_running = True
        self._is_paused = False
        self.proxies = get_proxies()
        self.current_proxy_index = 0

        # Set để lưu trữ các link bài viết đã bình luận trong phiên này, tránh spam
        self.commented_posts = set()

    def run(self):
        """
        Hàm này là entry point khi thread bắt đầu. Nó chứa vòng lặp chính.
        Ai gọi: QThread.start() trong main.py.
        """
        self.log_signal.emit("INFO", "Bắt đầu quá trình scraping...")
        self.status_signal.emit("Đang chạy...")

        try:
            if not self.login_facebook():
                self.log_signal.emit("ERROR", "Đăng nhập thất bại. Dừng tiến trình.")
                return

            # Vòng lặp chính, chạy vô tận cho đến khi bị dừng
            while self._is_running:
                for group_url in self.config["groups"]:
                    if not self._is_running: break # Kiểm tra trước mỗi group

                    self.handle_pause() # Kiểm tra nếu có lệnh tạm dừng

                    self.log_signal.emit("INFO", f"Bắt đầu quét nhóm: {group_url}")
                    self.scan_group(group_url)
                    random_delay(10, 20) # Nghỉ giữa các nhóm

                if self._is_running:
                    self.log_signal.emit("INFO", "Hoàn thành một chu kỳ quét. Tạm nghỉ 1 giờ.")
                    # Ngủ 1 giờ, nhưng kiểm tra cờ is_running mỗi giây
                    for _ in range(3600):
                        if not self._is_running: break
                        time.sleep(1)

        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi không xác định: {e}")
        finally:
            self.quit_driver()
            self.status_signal.emit("Đã dừng")
            self.finished_signal.emit()

    def _init_driver(self):
        """Khởi tạo WebDriver với các tùy chọn để tránh bị phát hiện."""
        try:
            options = webdriver.ChromeOptions()
            # Ngăn chặn các pop-up thông báo của trình duyệt
            options.add_argument("--disable-notifications")
            if self.config["settings"]["headless"]:
                options.add_argument("--headless")

            # Tích hợp User-Agent và Proxy rotation
            options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
            if self.proxies:
                proxy = self.proxies[self.current_proxy_index]
                options.add_argument(f'--proxy-server={proxy}')
                self.log_signal.emit("INFO", f"Sử dụng proxy: {proxy}")
                self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            else:
                self.log_signal.emit("INFO", "Không có proxy nào được cấu hình trong proxies.txt.")

            # Kỹ thuật quan trọng để ẩn việc đang dùng Selenium
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

            # Ẩn thuộc tính 'navigator.webdriver'
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            return True
        except Exception as e:
            self.log_signal.emit("ERROR", f"Không thể khởi tạo WebDriver: {e}")
            return False

    def login_facebook(self):
        """Thực hiện đăng nhập vào Facebook."""
        if not self._init_driver(): return False

        try:
            self.driver.get("https://www.facebook.com/")
            random_delay(2, 4)

            # Đóng popup cookie nếu có
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='cookie-policy-manage-dialog-accept-button']"))
                )
                cookie_button.click()
                self.log_signal.emit("INFO", "Đã đóng popup cookie.")
                random_delay(1,2)
            except TimeoutException:
                self.log_signal.emit("INFO", "Không tìm thấy popup cookie.")

            email_field = self.driver.find_element(By.ID, "email")
            pass_field = self.driver.find_element(By.ID, "pass")

            simulate_typing(email_field, self.config["facebook_credentials"]["email"])
            random_delay(0.5, 1)
            simulate_typing(pass_field, self.config["facebook_credentials"]["password"])

            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()

            # Chờ trang chính load, kiểm tra bằng sự hiện diện của thanh tìm kiếm
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search']"))
            )
            self.log_signal.emit("SUCCESS", "Đăng nhập thành công!")
            return True
        except (NoSuchElementException, TimeoutException) as e:
            self.log_signal.emit("ERROR", f"Lỗi khi tìm phần tử đăng nhập: {e}")
            return False
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi không xác định khi đăng nhập: {e}")
            return False

    def scan_group(self, group_url):
        """Quét một group, trích xuất bài viết và xử lý."""
        try:
            self.driver.get(group_url)
            self.log_signal.emit("INFO", "Đang tải bài viết trong nhóm...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )

            # Cuộn trang để tải một số lượng bài viết nhất định
            for _ in range(self.config["settings"]["max_posts_per_group"] // 2):
                if not self._is_running: return
                human_scroll(self.driver)
                random_delay(2, 5)

            # Lấy HTML và parse
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # --- PHẦN QUAN TRỌNG CẦN CẬP NHẬT ---
            # Selector cho các bài viết có thể thay đổi. Cần inspect thủ công.
            # Ví dụ selector: "div[data-ad-preview='message']" hoặc tương tự.
            posts = soup.select("div.x1yztbdb.x1n2onr6.xh8yej3.x1ja2u2z") # Selector ví dụ

            if not posts:
                self.log_signal.emit("WARNING", "Không tìm thấy bài viết nào với selector hiện tại. Có thể cấu trúc FB đã thay đổi.")
                return

            self.log_signal.emit("INFO", f"Tìm thấy {len(posts)} bài viết. Bắt đầu phân tích.")
            for post in posts[:self.config["settings"]["max_posts_per_group"]]:
                 if not self._is_running: return
                 self.handle_pause()
                 self.process_post(post)

        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi khi quét nhóm {group_url}: {e}")

    def process_post(self, post_element):
        """Xử lý một bài viết: trích xuất, kiểm tra keyword và bình luận."""
        try:
            # Lấy nội dung bài viết
            # TODO: Cập nhật selector cho nội dung text
            post_text_element = post_element.select_one("div[data-ad-preview='message']")
            post_text = post_text_element.text.lower() if post_text_element else ""

            # Lấy link của bài viết
            # TODO: Cập nhật selector cho link permalink
            post_link_element = post_element.find("a", href=lambda href: href and "/permalink/" in href)
            post_url = "https://facebook.com" + post_link_element['href'] if post_link_element else f"unknown_post_{random.randint(1000,9999)}"

            if post_url in self.commented_posts:
                self.log_signal.emit("INFO", f"Bỏ qua bài viết đã xử lý: {post_url}")
                return

            # Kiểm tra keyword
            for product in self.config["products"]:
                keywords = [kw.strip().lower() for kw in product["keywords"].split(",")]
                if any(keyword in post_text for keyword in keywords):
                    self.log_signal.emit("SUCCESS", f"Tìm thấy keyword cho '{product['name']}' trong bài viết: {post_url}")

                    if not self.config["settings"]["test_mode"]:
                        self.post_comment(post_url, product["link"])
                    else:
                        self.log_signal.emit("INFO", "[CHẾ ĐỘ THỬ NGHIỆM] Giả lập bình luận link: " + product['link'])

                    self.commented_posts.add(post_url) # Đánh dấu đã xử lý
                    random_delay(15, 30) # Nghỉ lâu hơn sau khi bình luận
                    break # Chuyển sang bài viết tiếp theo sau khi tìm thấy match

        except Exception as e:
            self.log_signal.emit("WARNING", f"Không thể xử lý một bài viết: {e}")

    def post_comment(self, post_url, comment_text):
        """Tìm đến bài viết và thực hiện bình luận."""
        # Chức năng này phức tạp vì cần tìm đúng ô comment của đúng bài viết.
        # Cách tiếp cận an toàn hơn là điều hướng đến URL của bài viết.
        self.log_signal.emit("INFO", f"Điều hướng đến bài viết để bình luận: {post_url}")
        self.driver.get(post_url)
        random_delay(5, 8)

        try:
            # TODO: Cập nhật selector cho ô soạn thảo bình luận
            comment_box_selector = "div[aria-label='Viết bình luận']"
            comment_box = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, comment_box_selector))
            )

            comment_box.click()
            random_delay(1, 2)

            # Tìm ô nhập liệu thực sự sau khi click
            actual_input = self.driver.switch_to.active_element
            simulate_typing(actual_input, comment_text)

            # TODO: Cập nhật selector cho nút Gửi
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "div[aria-label='Gửi']")
            submit_button.click()

            self.log_signal.emit("SUCCESS", f"Đã bình luận thành công vào bài viết: {post_url}")
        except Exception as e:
            self.log_signal.emit("ERROR", f"Lỗi khi bình luận: {e}")

    def quit_driver(self):
        """Đóng trình duyệt một cách an toàn."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                self.log_signal.emit("INFO", "Đã đóng trình duyệt.")
            except Exception as e:
                self.log_signal.emit("ERROR", f"Lỗi khi đóng trình duyệt: {e}")

    def stop(self):
        """Dừng luồng một cách an toàn."""
        self.log_signal.emit("INFO", "Nhận được yêu cầu dừng...")
        self._is_running = False
        self._is_paused = False # Thoát khỏi vòng lặp pause nếu đang tạm dừng

    def pause(self):
        """Tạm dừng luồng."""
        self.log_signal.emit("INFO", "Đang tạm dừng...")
        self.status_signal.emit("Đã tạm dừng")
        self._is_paused = True

    def resume(self):
        """Tiếp tục luồng."""
        self.log_signal.emit("INFO", "Tiếp tục chạy...")
        self.status_signal.emit("Đang chạy...")
        self._is_paused = False

    def handle_pause(self):
        """Vòng lặp kiểm tra trạng thái tạm dừng."""
        while self._is_paused:
            if not self._is_running: # Cho phép dừng hẳn ngay cả khi đang pause
                break
            time.sleep(1)
