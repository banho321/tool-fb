# Facebook Group Auto-Comment Tool

**Phiên bản:** 1.3.0 (Xử lý lỗi Chrome Binary & Hoàn thiện)

---

## ⚠️ Cảnh báo Quan trọng

Việc tự động hóa có thể vi phạm Điều khoản Dịch vụ của Facebook. **Hãy luôn sử dụng trên tài khoản thử nghiệm.**

---

## 🔬 Hướng dẫn Kiểm thử Từng bước (Quan trọng!)

Trước khi chạy, hãy thực hiện các bước kiểm thử để đảm bảo mọi thứ hoạt động.

### Bước 0: Chuẩn bị file `config.testing.json`

1.  Mở file `config.testing.json`.
2.  Điền **email** và **mật khẩu** của tài khoản Facebook thử nghiệm.
3.  Cập nhật URL trong `"groups"` và `"test_post_url"`.
4.  **Nếu gặp lỗi "cannot find Chrome binary"**, hãy xem phần **"Gỡ lỗi"** ở cuối file này để biết cách điền `"chrome_binary_path"`.

### Bước 1: Kiểm tra Đăng nhập

-   **Chạy lệnh:** `python test_login.py`
-   **Kết quả mong đợi:** Terminal báo **"SUCCESS: Đăng nhập thành công!"**.

### Bước 2: Kiểm tra Quét, Lấy và Lọc Bài viết

-   **Chạy lệnh:** `python test_scan.py`
-   **Kết quả mong đợi:** Terminal in ra nội dung bài viết và báo **"[MATCH FOUND!]"** nếu có từ khóa khớp.

### Bước 3: Kiểm tra Hành động Bình luận

-   **Chạy lệnh:** `python test_comment.py`
-   **Kết quả mong đợi:** Terminal báo **"SUCCESS: Tất cả các phần tử để bình luận đều được tìm thấy!"**.

---

## ▶️ Hướng dẫn Chạy Ứng dụng Chính

**Chỉ sau khi cả 3 bước kiểm thử trên đều thành công**, bạn mới nên chạy ứng dụng chính.

1.  **Cấu hình:** Mở file `config.json` và điền thông tin của bạn.
2.  **Chạy ứng dụng:** `python main.py`

---

## 🔧 Gỡ lỗi & Bảo trì

### Xử lý lỗi "cannot find Chrome binary"

Lỗi này xảy ra khi Selenium không tìm thấy file `chrome.exe`. Để khắc phục, bạn cần chỉ đường dẫn thủ công:

**1. Tìm đường dẫn file `chrome.exe`:**

*   **Windows:**
    1.  Tìm shortcut Google Chrome trên Desktop hoặc Start Menu.
    2.  Click chuột phải vào nó -> **Properties** (Thuộc tính).
    3.  Trong ô **Target** (Mục tiêu), copy toàn bộ đường dẫn (ví dụ: `"C:\Program Files\Google\Chrome\Application\chrome.exe"`).
*   **macOS:**
    1.  Mở Finder, vào thư mục **Applications**.
    2.  Tìm Google Chrome, click chuột phải -> **Get Info**.
    3.  Tìm giá trị ở mục **Where** và ghép với `/Contents/MacOS/Google Chrome`. Đường dẫn thường là: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`.

**2. Dán đường dẫn vào file cấu hình:**

1.  Mở file `config.testing.json` (khi đang test) hoặc `config.json` (khi chạy thật).
2.  Tìm đến dòng `"chrome_binary_path": ""`.
3.  Dán đường dẫn bạn vừa copy vào giữa hai dấu ngoặc kép.
    -   **Lưu ý quan trọng cho Windows:** Bạn phải **thay đổi tất cả các dấu `\` thành `\\` hoặc `/`**.
    -   *Ví dụ đúng:* `"chrome_binary_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"`
    -   *Ví dụ đúng:* `"chrome_binary_path": "C:/Program Files/Google/Chrome/Application/chrome.exe"`
    -   *Ví dụ sai:* `"chrome_binary_path": "C:\Program Files\Google\Chrome\Application\chrome.exe"`
4.  Lưu file lại và chạy lại script test.

### Cách cập nhật Selectors

Khi các script test báo lỗi không tìm thấy phần tử (bài viết, ô bình luận), bạn cần cập nhật selector bằng cách dùng công cụ **"Inspect"** của trình duyệt. Hướng dẫn chi tiết có trong các phiên bản trước của README.
