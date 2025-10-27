# get_cookies.py
"""
Script này tự động hóa quá trình lấy cookie phiên đăng nhập Facebook.

Cách hoạt động:
1. Mở một trình duyệt Firefox mới và điều hướng đến trang chủ Facebook.
2. Hiển thị một lời nhắc trong terminal, yêu cầu người dùng đăng nhập thủ công
   (bao gồm cả việc xử lý email, mật khẩu, và mã xác thực hai yếu tố - 2FA).
3. Script sẽ kiên nhẫn chờ đợi cho đến khi người dùng đăng nhập thành công.
   Nó nhận biết điều này bằng cách tìm kiếm sự tồn tại của một phần tử
   chỉ có trên trang chủ sau khi đã đăng nhập (ví dụ: link đến trang cá nhân).
4. Một khi đăng nhập được xác nhận, script sẽ tự động trích xuất tất cả
   cookie và lưu chúng vào một file có tên `facebook_cookies.json`.
5. File cookie này sau đó sẽ được ứng dụng chính và các script test khác sử dụng.
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Tên file cookie đầu ra
COOKIE_FILE = "facebook_cookies.json"
# Phần tử để xác định đã đăng nhập thành công (link đến trang cá nhân)
# Cần kiểm tra lại nếu Facebook thay đổi cấu trúc
LOGIN_SUCCESS_SELECTOR = "a[href*='https://www.facebook.com/me']"

def get_facebook_cookies():
    """Hàm chính để lấy và lưu cookie."""
    print("--- Bắt đầu quy trình lấy cookie Facebook ---")

    driver = None
    try:
        # Khởi tạo Firefox WebDriver
        options = webdriver.FirefoxOptions()
        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

        # Mở trang Facebook
        driver.get("https://www.facebook.com/")

        # Hướng dẫn người dùng
        print("\n" + "="*50)
        print("MỘT CỬA SỔ FIREFOX ĐÃ ĐƯỢC MỞ.")
        print("VUI LÒNG THỰC HIỆN CÁC BƯỚC SAU:")
        print("1. Đăng nhập vào tài khoản Facebook của bạn trong cửa sổ đó.")
        print("2. Hoàn thành tất cả các bước xác thực (mã 2FA, checkpoint...).")
        print("3. Sau khi vào được trang chủ Facebook, hãy quay lại cửa sổ terminal này.")
        print("\nScript đang chờ bạn đăng nhập thành công...")
        print("="*50 + "\n")

        # Chờ đợi cho đến khi đăng nhập thành công (timeout sau 5 phút)
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, LOGIN_SUCCESS_SELECTOR))
        )

        print("SUCCESS: Đã phát hiện đăng nhập thành công!")

        # Lấy cookie sau một khoảng trễ nhỏ để đảm bảo tất cả cookie đã được thiết lập
        time.sleep(5)
        cookies = driver.get_cookies()

        # Lưu cookie vào file
        with open(COOKIE_FILE, 'w') as f:
            json.dump(cookies, f, indent=4)

        print(f"Đã lưu thành công {len(cookies)} cookie vào file '{COOKIE_FILE}'.")
        print("Bây giờ bạn có thể sử dụng file này để chạy ứng dụng chính và các script test.")

    except TimeoutException:
        print("\nERROR: Hết thời gian chờ. Bạn đã không đăng nhập thành công trong vòng 5 phút.")
    except Exception as e:
        print(f"\nERROR: Đã xảy ra lỗi không xác định: {e}")
    finally:
        if driver:
            print("\nTrình duyệt sẽ tự động đóng sau 10 giây.")
            time.sleep(10)
            driver.quit()
        print("--- Kết thúc quy trình ---")

if __name__ == "__main__":
    get_facebook_cookies()
