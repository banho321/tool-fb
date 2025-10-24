# Facebook Group Auto-Comment Tool

Công cụ desktop được xây dựng bằng Python và PyQt6 để tự động quét các nhóm Facebook công khai, tìm kiếm các bài viết có chứa từ khóa liên quan đến sản phẩm và đăng bình luận chứa link sản phẩm tương ứng.

**Tác giả:** Jules (AI Software Engineer)
**Phiên bản:** 1.0.0

---

## ⚠️ Cảnh báo Quan trọng

**Việc tự động hóa các hoạt động trên nền tảng Facebook là vi phạm [Điều khoản Dịch vụ](https://www.facebook.com/terms.php) của họ.**

- **Rủi ro:** Sử dụng công cụ này, đặc biệt là với tài khoản chính, có thể dẫn đến việc tài khoản của bạn bị **hạn chế tạm thời** hoặc **khóa vĩnh viễn**.
- **Trách nhiệm:** Công cụ này được tạo ra cho mục đích giáo dục và thử nghiệm. Người phát triển không chịu bất kỳ trách nhiệm nào về các hậu quả có thể xảy ra với tài khoản Facebook của bạn.
- **Khuyến nghị:**
    - **Luôn sử dụng trên một tài khoản Facebook thử nghiệm (clone/test account).**
    - Bắt đầu với các cài đặt an toàn (ít nhóm, tần suất quét thấp).
    - Giám sát hoạt động của tool thường xuyên.

---

## 🚀 Tính năng chính

-   **Giao diện đồ họa (GUI):** Dễ dàng quản lý cấu hình và điều khiển tool thông qua giao diện desktop thân thiện.
-   **Quét nhóm tự động:** Tự động truy cập vào danh sách các nhóm Facebook công khai bạn đã cung cấp.
-   **Phân tích bài viết:** Trích xuất nội dung các bài viết mới để phân tích.
-   **Đối chiếu từ khóa:** So sánh nội dung bài viết với danh sách từ khóa sản phẩm của bạn.
-   **Bình luận tự động:** Nếu tìm thấy từ khóa khớp, công cụ sẽ tự động đăng bình luận với link sản phẩm bạn đã cấu hình.
-   **An toàn và tránh bị phát hiện:**
    -   Sử dụng độ trễ ngẫu nhiên giữa các hành động.
    -   Mô phỏng hành vi người dùng (cuộn chuột, gõ phím từ từ).
    -   Các kỹ thuật che giấu việc sử dụng Selenium.
    -   Chế độ "Thử nghiệm" (Test Mode) cho phép bạn chạy thử mà không đăng bình luận thật.
-   **Quản lý và Logging:**
    -   Lưu và tải lại toàn bộ cấu hình.
    -   Ghi log chi tiết ra file `log.txt` và cơ sở dữ liệu `log.db`.
    -   Hiển thị log thời gian thực trên giao diện.
    -   Xuất lịch sử hoạt động ra file CSV.
-   **Đa luồng:** Tác vụ scraping chạy trên một luồng riêng biệt để đảm bảo giao diện luôn phản hồi.

---

## 🛠️ Hướng dẫn Cài đặt và Sử dụng

### 1. Yêu cầu hệ thống

-   Python 3.10 trở lên.
-   Trình duyệt Google Chrome đã được cài đặt.

### 2. Các bước cài đặt

**a. Clone repository (hoặc tải mã nguồn):**

```bash
git clone https://your-repository-url.git
cd your-project-directory
```

**b. Tạo và kích hoạt môi trường ảo (khuyến khích):**

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**c. Cài đặt các thư viện cần thiết:**

Chạy lệnh sau để cài đặt tất cả các gói Python được liệt kê trong file `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Cách chạy ứng dụng

Sau khi cài đặt xong, chạy file `main.py`:

```bash
python main.py
```

### 4. Hướng dẫn cấu hình trên giao diện

1.  **Tab "Cấu hình":**
    -   **Email và Mật khẩu Facebook:** Nhập thông tin đăng nhập tài khoản Facebook (thử nghiệm) của bạn.
    -   **Danh sách Nhóm:** Sử dụng nút "Thêm Group" và "Xóa Group" để quản lý danh sách URL các nhóm công khai bạn muốn quét.
    -   **Danh sách Sản phẩm:**
        -   **Tên sản phẩm:** Tên định danh cho sản phẩm của bạn.
        -   **Keywords:** Nhập các từ khóa liên quan đến sản phẩm, **cách nhau bởi dấu phẩy (,)**. Tool sẽ tìm kiếm các từ khóa này trong bài viết.
        -   **Link bình luận:** URL hoặc nội dung bạn muốn bình luận khi tìm thấy từ khóa trùng khớp.
    -   **Lưu Cấu hình:** Sau khi chỉnh sửa, nhấn nút **"Lưu Cấu hình"**. Các cài đặt sẽ được lưu vào file `config.json` và tự động tải lại vào lần mở ứng dụng tiếp theo.

2.  **Tab "Điều khiển":**
    -   **Chế độ Headless:** Tick vào ô này nếu bạn muốn trình duyệt chạy ở chế độ nền (không hiển thị cửa sổ). Hữu ích khi chạy chính thức, nhưng nên bỏ tick khi cần gỡ lỗi.
    -   **Chế độ Thử nghiệm:** **Highly Recommended for the first run!** Tick vào ô này, tool sẽ thực hiện mọi thao tác nhưng **sẽ không đăng bình luận thật**. Thay vào đó, nó sẽ ghi log "Giả lập bình luận...".
    -   **Bắt đầu Chạy:** Bắt đầu quá trình quét và bình luận.
    -   **Tạm dừng / Tiếp tục:** Dừng hoặc tiếp tục tác vụ đang chạy.
    -   **Dừng:** Dừng hoàn toàn tác vụ và đóng trình duyệt.

3.  **Tab "Logs":**
    -   Hiển thị các hoạt động, lỗi, và thành công của tool trong thời gian thực.
    -   **Xuất Logs ra CSV:** Lưu lại toàn bộ lịch sử từ cơ sở dữ liệu `log.db` ra một file CSV.

---

## 🔧 Bảo trì và Gỡ lỗi

Facebook thường xuyên cập nhật cấu trúc HTML của họ. Điều này có thể làm cho các **selectors** (đoạn mã dùng để tìm các phần tử như bài viết, ô bình luận) trong file `scraper.py` trở nên lỗi thời.

Nếu tool không tìm thấy bài viết hoặc không thể bình luận, bạn cần:

1.  Mở Facebook trên trình duyệt Chrome.
2.  Nhấn `F12` để mở "Developer Tools".
3.  Sử dụng công cụ "Inspect" (biểu tượng con trỏ chuột ở góc trên bên trái của Developer Tools) để tìm các class hoặc ID mới của các phần tử.
4.  Mở file `scraper.py`, tìm đến các dòng có bình luận `# TODO: Cập nhật selector...` và thay thế các giá trị cũ bằng giá trị mới bạn vừa tìm được.
