# test_comment.py
"""
Script này dùng để kiểm tra riêng lẻ chức năng BÌNH LUẬN vào một bài viết cụ thể.

Cách sử dụng:
1.  Đảm bảo bạn đã điền đúng thông tin trong `config.testing.json`.
    -   Điền tài khoản test.
    -   Quan trọng: Mở file `config.testing.json` và thay thế giá trị của
        `"test_post_url"` bằng URL của một bài viết CÔNG KHAI thực tế mà bạn
        muốn dùng để thử nghiệm.
2.  Chạy script từ terminal: `python test_comment.py`

Script sẽ:
-   Đăng nhập vào Facebook.
-   Đi thẳng đến URL bài viết bạn đã cung cấp.
-   Cố gắng tìm ô soạn thảo bình luận, click vào đó, và mô phỏng việc gõ chữ.
-   Cố gắng tìm nút "Gửi" (Post/Submit).
-   Báo cáo thành công nếu tìm thấy tất cả các phần tử.

Quan trọng:
-   Mặc định, script này CHỈ KIỂM TRA, không gửi bình luận thật.
-   Nếu bạn muốn THỬ GỬI BÌNH LUẬN THẬT, hãy tìm đến cuối hàm `test_comment`
    và bỏ comment (xóa dấu #) ở dòng `submit_button.click()`.

Nếu script báo lỗi không tìm thấy phần tử, bạn cần cập nhật các biến
`COMMENT_BOX_SELECTOR` và `SUBMIT_BUTTON_SELECTOR` trong script này.
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

# --- PHẦN CẦN CHÚ Ý ---
# Các selector cho hành động bình luận. Rất dễ bị thay đổi.
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

    if not post_url or "your_post_id" in post_url:
        print("Lỗi: Vui lòng cập nhật `test_post_url` trong 'config.testing.json'.")
        return

    driver = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features=AutomationControlled")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        # 1. Đăng nhập
        print("1. Đang đăng nhập...")
        login(driver, creds["email"], creds["password"])
        time.sleep(2)

        # 2. Truy cập bài viết
        print(f"2. Đang truy cập bài viết: {post_url}")
        driver.get(post_url)
        time.sleep(5) # Chờ trang tải hoàn tất

        # 3. Tìm và tương tác với ô bình luận
        print(f"3. Đang tìm ô bình luận với selector: '{COMMENT_BOX_SELECTOR}'")
        comment_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, COMMENT_BOX_SELECTOR))
        )
        print("   -> Đã tìm thấy ô bình luận.")
        comment_box.click()
        time.sleep(1)

        # Sau khi click, ô nhập liệu thực sự có thể là một phần tử khác
        print("4. Đang gõ nội dung test...")
        actual_input = driver.switch_to.active_element
        test_message = "Đây là một bình luận thử nghiệm tự động."
        actual_input.send_keys(test_message)
        print(f"   -> Đã gõ: '{test_message}'")
        time.sleep(2)

        # 5. Tìm nút gửi
        print(f"5. Đang tìm nút gửi với selector: '{SUBMIT_BUTTON_SELECTOR}'")
        submit_button = driver.find_element(By.CSS_SELECTOR, SUBMIT_BUTTON_SELECTOR)
        print("   -> Đã tìm thấy nút gửi.")

        # --- GỬI BÌNH LUẬN THẬT (MẶC ĐỊNH VÔ HIỆU HÓA) ---
        # Bỏ comment (xóa dấu #) ở dòng dưới đây nếu bạn muốn thử gửi bình luận thật
        # submit_button.click()
        # print("   -> ĐÃ GỬI BÌNH LUẬN THẬT!")

        print("\nSUCCESS: Tất cả các phần tử để bình luận đều được tìm thấy!")
        print("   -> Selector cho ô bình luận và nút gửi có vẻ chính xác.")

    except Exception as e:
        print(f"\nERROR: Đã có lỗi xảy ra trong quá trình test bình luận: {e}")
        print("   -> Hãy kiểm tra lại các selector hoặc đảm bảo URL bài viết là công khai.")
    finally:
        if driver:
            print("\nTrình duyệt sẽ tự đóng sau 10 giây.")
            time.sleep(10)
            driver.quit()
        print("--- Kết thúc kiểm tra ---")

if __name__ == "__main__":
    test_comment()
