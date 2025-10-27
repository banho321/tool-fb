# Facebook Group Auto-Comment Tool

Công cụ desktop được xây dựng bằng Python và PyQt6 để tự động quét các nhóm Facebook công khai, tìm kiếm các bài viết có chứa từ khóa liên quan đến sản phẩm và đăng bình luận chứa link sản phẩm tương ứng.

**Tác giả:** Jules (AI Software Engineer)
**Phiên bản:** 1.2.0 (Hoàn thiện Bộ công cụ Kiểm thử)

---

## ⚠️ Cảnh báo Quan trọng

**Việc tự động hóa các hoạt động trên nền tảng Facebook là vi phạm [Điều khoản Dịch vụ](https://www.facebook.com/terms.php) của họ.**

-   **Rủi ro:** Sử dụng công cụ này có thể dẫn đến việc tài khoản của bạn bị **hạn chế tạm thời** hoặc **khóa vĩnh viễn**.
-   **Trách nhiệm:** Công cụ này được tạo ra cho mục đích giáo dục. Người phát triển không chịu trách nhiệm về các hậu quả có thể xảy ra.
-   **Khuyến nghị:** Luôn sử dụng trên một **tài khoản Facebook thử nghiệm**.

---

## 🔬 Hướng dẫn Kiểm thử Từng bước (Quan trọng!)

Trước khi chạy ứng dụng chính, bạn **bắt buộc** phải thực hiện các bước kiểm thử sau để đảm bảo mọi chức năng cốt lõi đều hoạt động tốt với phiên bản hiện tại của Facebook.

### Bước 0: Chuẩn bị file cấu hình thử nghiệm

1.  Mở file `config.testing.json`.
2.  Điền **email** và **mật khẩu** của tài khoản Facebook **thử nghiệm** của bạn.
3.  Trong phần `"groups"`, thay thế URL mẫu bằng URL của một **nhóm Facebook công khai** mà bạn muốn dùng để test.
4.  Trong phần `"test_post_url"`, dán URL đầy đủ của một **bài viết công khai bất kỳ** để thử nghiệm chức năng bình luận.

### Bước 1: Kiểm tra Đăng nhập

Xác nhận thông tin đăng nhập và khả năng tương tác cơ bản với trang Facebook.

-   **Chạy lệnh:** `python test_login.py`
-   **Kết quả mong đợi:** Terminal hiển thị **"SUCCESS: Đăng nhập thành công!"**.
-   **Xử lý lỗi:** Kiểm tra lại thông tin đăng nhập hoặc khả năng tài khoản bị yêu cầu xác thực 2 yếu tố.

### Bước 2: Kiểm tra Quét nhóm, Lấy và Lọc Bài viết

Kiểm tra 2 vấn đề: (1) Tool có tìm được các bài viết không (selector đúng không?) và (2) Logic so khớp từ khóa có hoạt động không?

-   **Chạy lệnh:** `python test_scan.py`
-   **Kết quả mong đợi:**
    -   Terminal in ra nội dung các bài viết tìm được.
    -   Hiển thị dòng **"[MATCH FOUND!]"** nếu bài viết chứa từ khóa.
-   **Xử lý lỗi:** Nếu báo **"WARNING: Không tìm thấy bài viết nào..."**, bạn cần cập nhật `POST_SELECTOR` trong file `test_scan.py`. Xem mục **"Bảo trì và Gỡ lỗi"**.

### Bước 3: Kiểm tra Hành động Bình luận

Đây là bước cuối cùng, kiểm tra xem tool có tìm thấy ô bình luận và nút gửi hay không.

-   **Chạy lệnh:** `python test_comment.py`
-   **Kết quả mong đợi:**
    -   Trình duyệt sẽ mở ra, đi thẳng đến bài viết bạn đã chỉ định.
    -   Terminal sẽ báo cáo từng bước: "Đã tìm thấy ô bình luận", "Đã gõ nội dung", "Đã tìm thấy nút gửi".
    -   Cuối cùng, hiển thị **"SUCCESS: Tất cả các phần tử để bình luận đều được tìm thấy!"**.
-   **Xử lý lỗi:** Nếu báo lỗi không tìm thấy phần tử, bạn cần cập nhật `COMMENT_BOX_SELECTOR` và `SUBMIT_BUTTON_SELECTOR` trong file `test_comment.py`.
-   **Lưu ý:** Script này mặc định **không gửi bình luận thật**. Nếu muốn thử, bạn phải chỉnh sửa file `test_comment.py` (xóa dấu `#` ở dòng `submit_button.click()`).

---

## ▶️ Hướng dẫn Chạy Ứng dụng Chính

**Chỉ sau khi cả 3 bước kiểm thử trên đều thành công**, bạn mới nên chạy ứng dụng chính.

1.  **Cấu hình:** Mở file `config.json` và điền thông tin của bạn.
2.  **Chạy ứng dụng:** `python main.py`
3.  **Sử dụng Giao diện:**
    -   **Tab "Cấu hình":** Chỉnh sửa và nhấn **"Lưu Cấu hình"**.
    -   **Tab "Điều khiển":** **Luôn tick vào "Chế độ Thử nghiệm" trong lần chạy đầu tiên!**
    -   **Tab "Logs":** Theo dõi hoạt động của tool.

---

## 🔧 Bảo trì và Gỡ lỗi: Cách cập nhật Selectors

Khi các script test báo lỗi không tìm thấy phần tử (bài viết, ô bình luận), bạn cần cập nhật selector:

1.  Mở trang Facebook trên Chrome.
2.  Click chuột phải vào phần tử bạn muốn tìm (ví dụ: khu vực một bài viết) và chọn **"Inspect"**.
3.  Trong cửa sổ DevTools, tìm một thẻ `div` bao trọn phần tử đó.
4.  Click chuột phải vào thẻ -> **Copy** -> **Copy selector**.
5.  Mở file script tương ứng (`test_scan.py` hoặc `test_comment.py`) và dán giá trị mới vào biến selector ở đầu file.
6.  Chạy lại script test để xác nhận.

---
*Các phần khác của README như Tính năng chính, Hướng dẫn Cài đặt vẫn giữ nguyên như trước.*
