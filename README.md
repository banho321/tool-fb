# Facebook Group Auto-Comment Tool (Cookie Login Edition)

**Phiên bản:** 2.1.0 (Tự động lấy Cookie)

---

## 🚀 Hướng dẫn Cài đặt và Sử dụng

Quy trình đã được đơn giản hóa đáng kể. Bạn không cần cài thêm extension trình duyệt nữa.

### Bước 1: Cài đặt Môi trường

1.  **Cài đặt Firefox:** Đảm bảo bạn đã cài đặt trình duyệt Mozilla Firefox.
2.  **Tải mã nguồn:** Tải và giải nén project.
3.  **Cài đặt thư viện:** Mở terminal trong thư mục project và chạy:
    ```bash
    pip install -r requirements.txt
    ```

### Bước 2: Lấy File Cookie Tự động

Đây là quy trình mới thay thế cho việc export thủ công.

1.  **Chạy script:** Trong terminal, chạy lệnh sau:
    ```bash
    python get_cookies.py
    ```
2.  **Đăng nhập thủ công:**
    -   Một cửa sổ Firefox sẽ tự động mở ra, điều hướng đến trang Facebook.
    -   **Trong cửa sổ Firefox đó**, hãy đăng nhập vào tài khoản Facebook của bạn. Hoàn thành tất cả các bước (mật khẩu, mã 2FA, v.v.).
3.  **Chờ đợi:**
    -   Sau khi bạn vào được trang chủ Facebook, script sẽ tự động phát hiện.
    -   Terminal sẽ hiển thị thông báo **"SUCCESS: Đã phát hiện đăng nhập thành công!"**.
4.  **Hoàn tất:**
    -   Script sẽ tự động lưu cookie của bạn vào file `facebook_cookies.json`.
    -   Cửa sổ Firefox sẽ tự động đóng lại sau vài giây.

### Bước 3: Cấu hình và Kiểm thử

Sau khi đã có file `facebook_cookies.json`, bạn có thể kiểm tra các chức năng chính.

**a. Chuẩn bị `config.testing.json`:**

1.  Mở file `config.testing.json`.
2.  Trong `"cookie_file_path"`, hãy chắc chắn rằng nó đang trỏ đến file cookie vừa tạo (ví dụ: `"facebook_cookies.json"`).
3.  Cập nhật URL trong `"groups"` và `"test_post_url"` để phù hợp với môi trường test.

**b. Chạy các script kiểm thử:**

-   **Kiểm tra Đăng nhập:** `python test_login.py`
-   **Kiểm tra Quét & Lọc:** `python test_scan.py`
-   **Kiểm tra Bình luận:** `python test_comment.py`

### Bước 4: Chạy Ứng dụng Chính

Khi các bài test đã thành công:

1.  Mở `main.py` để khởi động giao diện.
2.  Trong tab **"Cấu hình"**, nhấn nút **"Chọn File..."** và chọn file `facebook_cookies.json` của bạn.
3.  Lưu cấu hình và bắt đầu chạy.

---

## 🔧 Gỡ lỗi

-   **Lỗi "cannot find Firefox binary":** Tìm đường dẫn cài đặt Firefox trên máy bạn và điền vào trường `"firefox_binary_path"` trong file config.
-   **Đăng nhập cookie thất bại:** File cookie có thể đã hết hạn. Chỉ cần chạy lại `python get_cookies.py` để lấy file cookie mới.
-   **Không tìm thấy bài viết/ô bình luận:** Selector của Facebook đã thay đổi. Dùng công cụ "Inspect" của Firefox để tìm selector mới và cập nhật ở đầu các file test và `scraper.py`.
