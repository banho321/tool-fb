# logger.py
"""
Module này chịu trách nhiệm cho việc ghi log (logging) của ứng dụng.

Chức năng:
- Ghi log ra file text (log.txt) để dễ đọc.
- Lưu log vào cơ sở dữ liệu SQLite (log.db) để lưu trữ lâu dài và có cấu trúc.
- Cung cấp một signal PyQt6 để gửi thông điệp log đến GUI và cập nhật realtime.

Ai gọi:
- Bất kỳ module nào trong ứng dụng (chủ yếu là scraper.py và main.py) cần ghi lại một sự kiện.
"""
import sqlite3
import logging
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

# Cấu hình logging cơ bản của Python để ghi ra file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='log.txt',
    filemode='a', # 'a' for append
    encoding='utf-8'
)

class Logger(QObject):
    """
    Lớp Logger quản lý việc ghi log và giao tiếp với GUI.
    Kế thừa từ QObject để có thể sử dụng signals.
    """
    # Signal này sẽ được phát ra mỗi khi có một log mới.
    # GUI sẽ kết nối (connect) với signal này để cập nhật QTextEdit.
    # str: Tham số của signal, chứa thông điệp log đã được định dạng.
    log_updated = pyqtSignal(str)

    def __init__(self, db_name="log.db"):
        """
        Hàm khởi tạo của lớp Logger.
        Ai gọi nó: Được gọi một lần duy nhất trong main.py để tạo ra một instance logger toàn cục.
        Input:
            - db_name (str): Tên của file cơ sở dữ liệu SQLite.
        Output: Không có.
        """
        super().__init__()
        self.db_name = db_name
        self.setup_database()

    def setup_database(self):
        """
        Hàm này làm gì: Chuẩn bị cơ sở dữ liệu. Nó tạo file DB và bảng 'logs' nếu chúng chưa tồn tại.
        Ai gọi nó: Được gọi bởi __init__() khi Logger được khởi tạo.
        Input: Không có.
        Output: Không có.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    post_url TEXT,
                    comment_text TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            error_msg = f"Lỗi nghiêm trọng khi thiết lập cơ sở dữ liệu: {e}"
            print(error_msg)
            logging.error(error_msg)


    def log(self, level, message, post_url=None, comment_text=None):
        """
        Hàm này làm gì: Đây là hàm ghi log chính. Nó nhận thông tin sự kiện,
        định dạng nó, và gọi các hàm con để ghi vào file, DB và gửi tín hiệu tới GUI.
        Ai gọi nó: Bất kỳ phần nào của ứng dụng khi cần ghi log.
        Input:
            - level (str): Cấp độ log ('INFO', 'SUCCESS', 'WARNING', 'ERROR').
            - message (str): Nội dung chính của log.
            - post_url (str, optional): URL của bài viết liên quan.
            - comment_text (str, optional): Nội dung bình luận đã đăng.
        Output: Không có.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 1. Ghi vào file log.txt sử dụng thư viện logging
        log_entry_file = f"{message} | Post: {post_url or 'N/A'}"
        if level == 'INFO':
            logging.info(log_entry_file)
        elif level == 'SUCCESS':
            logging.info(f"SUCCESS: {log_entry_file}") # Ghi SUCCESS như INFO nhưng có tiền tố
        elif level == 'WARNING':
            logging.warning(log_entry_file)
        elif level == 'ERROR':
            logging.error(log_entry_file)

        # 2. Lưu vào cơ sở dữ liệu SQLite
        self._log_to_db(timestamp, level, message, post_url, comment_text)

        # 3. Gửi tín hiệu đến GUI để cập nhật realtime
        # Định dạng thông điệp để hiển thị đẹp hơn trên GUI
        gui_message = f"[{timestamp}] [{level}] {message}"
        if post_url:
            gui_message += f" - [Post: {post_url}]"
        self.log_updated.emit(gui_message)

    def _log_to_db(self, timestamp, level, message, post_url, comment_text):
        """
        Hàm này làm gì: Chèn một bản ghi log mới vào bảng 'logs' trong DB SQLite.
        Ai gọi nó: Được gọi từ hàm log().
        Input: Các thành phần của một bản ghi log.
        Output: Không có.
        """
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (timestamp, level, message, post_url, comment_text)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, level, message, post_url, comment_text))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            # Nếu ghi DB lỗi, ghi lại lỗi này vào file log
            error_msg = f"Lỗi khi ghi log vào cơ sở dữ liệu: {e}"
            print(error_msg)
            logging.error(error_msg)

# Tạo một instance duy nhất của Logger để có thể import và sử dụng ở mọi nơi
logger = Logger()
