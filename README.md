# Facebook Group Auto-Comment Tool (Cookie Login Edition)

**Phiên bản:** 2.0.0

---

## ⚠️ Thay đổi Lớn ở Phiên bản 2.0

Ứng dụng đã được nâng cấp để sử dụng **phương thức đăng nhập bằng cookie thay vì mật khẩu**. Đây là cách làm **an toàn và ổn định hơn**, giúp giảm thiểu rủi ro tài khoản bị checkpoint. Quy trình cài đặt và sử dụng đã thay đổi, vui lòng đọc kỹ hướng dẫn dưới đây.

---

## 🚀 Hướng dẫn Cài đặt và Sử dụng

### Bước 1: Cài đặt Môi trường

1.  **Cài đặt Firefox:** Đảm bảo bạn đã cài đặt trình duyệt Mozilla Firefox.
2.  **Tải mã nguồn:** Tải và giải nén project.
3.  **Cài đặt thư viện:** Mở terminal trong thư mục project và chạy:
    ```bash
    pip install -r requirements.txt
    ```

### Bước 2: Lấy File Cookie từ Trình duyệt

Đây là bước quan trọng nhất.

1.  **Cài đặt Extension "Cookie Editor":**
    -   Mở Firefox, truy cập trang [Cookie Editor Add-on](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/) và thêm nó vào Firefox.

2.  **Đăng nhập Facebook:**
    -   Mở một tab mới, truy cập [www.facebook.com](https://www.facebook.com) và đăng nhập vào tài khoản **thử nghiệm** của bạn như bình thường.

3.  **Xuất File Cookie:**
    -   Sau khi đăng nhập thành công, click vào biểu tượng extension **Cookie Editor** (hình chiếc bánh quy) trên thanh công cụ.
    -   Chọn nút **"Export"** (thường ở góc dưới bên phải).
    -   Trong menu xổ ra, chọn **"Export as JSON"**.
    -   Một file tên là `cookies.json` sẽ được tải về. Hãy di chuyển file này vào cùng thư mục với project code.

### Bước 3: Cấu hình và Kiểm thử

Ứng dụng cung cấp các script để bạn kiểm tra từng chức năng trước khi chạy chính thức.

**a. Chuẩn bị file `config.testing.json`:**

1.  Mở file `config.testing.json`.
2.  Trong mục `"cookie_file_path"`, điền tên file cookie bạn vừa tải về (ví dụ: `"cookies.json"`).
3.  Cập nhật URL trong `"groups"` và `"test_post_url"` để phù hợp với môi trường test của bạn.

**b. Chạy các script kiểm thử:**

1.  **Kiểm tra Đăng nhập:**
    ```bash
    python test_login.py
    ```
    *   **Mong đợi:** Báo "SUCCESS: Đăng nhập bằng cookie thành công!".

2.  **Kiểm tra Quét & Lọc:**
    ```bash
    python test_scan.py
    ```
    *   **Mong đợi:** In ra nội dung bài viết và báo "[MATCH FOUND!]".

3.  **Kiểm tra Bình luận:**
    ```bash
    python test_comment.py
    ```
    *   **Mong đợi:** Báo "SUCCESS: Tất cả các phần tử để bình luận đều được tìm thấy!".

### Bước 4: Chạy Ứng dụng Chính

Chỉ sau khi cả 3 bước test trên đều thành công:

1.  Mở `main.py` để khởi động giao diện.
2.  Trong tab **"Cấu hình"**, điền email (chỉ để định danh), và dùng nút **"Chọn File..."** để trỏ đến file `cookies.json` của bạn.
3.  Lưu cấu hình và bắt đầu chạy.

---

## 🔧 Gỡ lỗi

-   **Lỗi "cannot find Firefox binary":** Tương tự như lỗi Chrome trước đây, hãy tìm đường dẫn cài đặt Firefox trên máy bạn và điền vào trường `"firefox_binary_path"` trong file config.
-   **Đăng nhập cookie thất bại:** File cookie có thể đã hết hạn. Hãy đăng xuất khỏi Facebook, đăng nhập lại thủ công, và xuất lại file cookie mới.
-   **Không tìm thấy bài viết/ô bình luận:** Selector của Facebook đã thay đổi. Hãy dùng công cụ "Inspect" của Firefox để tìm selector mới và cập nhật ở đầu các file `test_*.py` và `scraper.py`.
