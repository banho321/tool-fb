# test_login.py
"""
Script này dùng để kiểm tra riêng lẻ chức năng đăng nhập vào Facebook.

Cách sử dụng:
1.  Mở file `config.testing.json`.
2.  Điền email và mật khẩu của tài khoản Facebook DÙNG ĐỂ TEST vào phần "facebook_credentials".
3.  Chạy script này từ terminal: `python test_login.py`

Script sẽ:
-   Đọc file cấu hình `config.testing.json`.
-   Khởi tạo một trình duyệt Chrome bằng Selenium.
-   Tự động điền thông tin và thử đăng nhập.
-   In ra thông báo thành công hoặc thất bại.

Nếu đăng nhập thành công, bạn sẽ thấy thông báo "SUCCESS: Đăng nhập thành công!"
và trình duyệt sẽ tự đóng sau 5 giây.

Nếu thất bại, hãy kiểm tra các nguyên nhân sau:
-   Sai email hoặc mật khẩu.
-   Tài khoản bị yêu cầu xác thực 2 yếu tố (2FA) hoặc checkpoint.
-   Giao diện đăng nhập của Facebook đã thay đổi (cần cập nhật ID của các ô input).
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def load_test_config():
    """Tải cấu hình từ file config.testing.json."""
    try:
        with open("config.testing.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'config.testing.json'.")
        return None
    except json.JSONDecodeError:
        print("Lỗi: File 'config.testing.json' không đúng định dạng JSON.")
        return None

def test_login():
    """Hàm chính thực hiện việc kiểm tra đăng nhập."""
    print("--- Bắt đầu kiểm tra chức năng đăng nhập ---")

    config = load_test_config()
    if not config:
        return

    creds = config.get("facebook_credentials", {})
    email = creds.get("email")
    password = creds.get("password")

    if not email or not password or "YOUR_TEST_EMAIL" in email:
        print("Lỗi: Vui lòng cập nhật email và mật khẩu trong 'config.testing.json' trước khi chạy.")
        return

    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        # Kỹ thuật ẩn Selenium
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("1. Đang mở trang Facebook...")
        driver.get("https://www.facebook.com/")

        # Đóng popup cookie nếu có
        try:
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='cookie-policy-manage-dialog-accept-button'], [aria-label='Accept All']"))
            )
            cookie_button.click()
            print("Đã đóng popup cookie.")
            time.sleep(1)
        except TimeoutException:
            print("Không tìm thấy popup cookie, tiếp tục.")

        print("2. Đang điền thông tin đăng nhập...")
        email_field = driver.find_element(By.ID, "email")
        pass_field = driver.find_element(By.ID, "pass")

        email_field.send_keys(email)
        time.sleep(0.5)
        pass_field.send_keys(password)
        time.sleep(0.5)

        print("3. Đang nhấn nút đăng nhập...")
        login_button = driver.find_element(By.NAME, "login")
        login_button.click()

        # Chờ trang chính load, kiểm tra bằng sự hiện diện của thanh tìm kiếm hoặc một yếu tố đặc trưng khác
        print("4. Đang chờ xác nhận đăng nhập thành công...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='search'], a[aria-label='Home']"))
        )

        print("\nSUCCESS: Đăng nhập thành công!")

    except (NoSuchElementException, TimeoutException) as e:
        print(f"\nERROR: Đăng nhập thất bại. Không tìm thấy phần tử cần thiết.")
        print("Nguyên nhân có thể do Facebook đã thay đổi giao diện. Hãy kiểm tra lại các selector.")
        print(f"Chi tiết lỗi: {e}")
    except Exception as e:
        print(f"\nERROR: Đã xảy ra lỗi không xác định: {e}")
    finally:
        if driver:
            print("Trình duyệt sẽ tự đóng sau 5 giây.")
            time.sleep(5)
            driver.quit()
        print("--- Kết thúc kiểm tra ---")

if __name__ == "__main__":
    test_login()
