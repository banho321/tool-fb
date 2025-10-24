# main.py
"""
Đây là file entry point (điểm khởi đầu) của ứng dụng.
"""

import sys
import os
import sqlite3
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QListWidget, QListWidgetItem, QTextEdit, QStatusBar, QCheckBox,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import QThread
from config import load_config, save_config
from scraper import FacebookScraper
from logger import logger # Import a instance logger

class MainWindow(QMainWindow):
    """
    Lớp cửa sổ chính của ứng dụng.
    """
    def __init__(self):
        """
        Hàm khởi tạo cửa sổ chính.
        """
        super().__init__()
        self.setWindowTitle("Facebook Group Auto-Comment Tool")
        self.setGeometry(100, 100, 900, 700)

        self.show_startup_warning()

        self.config_data = load_config()
        self.scraper_thread = None
        self.scraper = None

        self.setup_ui()
        self.connect_signals()

        self.load_settings_to_ui()
        logger.log("INFO", "Ứng dụng đã sẵn sàng.")

    def show_startup_warning(self):
        """Hiển thị cảnh báo khi khởi động."""
        QMessageBox.warning(
            self, "Cảnh báo Quan trọng",
            "Việc tự động hóa tương tác trên Facebook có thể vi phạm Điều khoản Dịch vụ của họ "
            "và có thể dẫn đến việc tài khoản của bạn bị hạn chế hoặc khóa vĩnh viễn.\n\n"
            "Hãy sử dụng công cụ này một cách có trách nhiệm và trên tài khoản thử nghiệm."
        )

    def setup_ui(self):
        """Xây dựng toàn bộ giao diện người dùng."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        self.create_config_tab()
        self.create_controls_tab()
        self.create_logs_tab()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar("Dừng")

    def create_config_tab(self):
        """Tạo tab 'Cấu hình'."""
        self.config_tab = QWidget()
        self.tabs.addTab(self.config_tab, "Cấu hình")
        layout = QGridLayout(self.config_tab)
        layout.addWidget(QLabel("<b>Email Facebook:</b>"), 0, 0)
        self.email_input = QLineEdit(placeholderText="Nhập email của bạn")
        layout.addWidget(self.email_input, 0, 1)
        layout.addWidget(QLabel("<b>Mật khẩu:</b>"), 1, 0)
        self.password_input = QLineEdit(placeholderText="Nhập mật khẩu của bạn", echoMode=QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input, 1, 1)
        layout.addWidget(QLabel("<b>Danh sách các nhóm Public:</b>"), 2, 0, 1, 2)
        self.group_list_widget = QListWidget()
        layout.addWidget(self.group_list_widget, 3, 0, 1, 2)
        group_button_layout = QHBoxLayout()
        self.add_group_button = QPushButton("Thêm Group")
        self.remove_group_button = QPushButton("Xóa Group")
        group_button_layout.addWidget(self.add_group_button)
        group_button_layout.addWidget(self.remove_group_button)
        layout.addLayout(group_button_layout, 4, 0, 1, 2)
        layout.addWidget(QLabel("<b>Danh sách Sản phẩm và Keywords:</b>"), 5, 0, 1, 2)
        self.product_table = QTableWidget(columnCount=3)
        self.product_table.setHorizontalHeaderLabels(["Tên sản phẩm", "Keywords (cách nhau bởi dấu phẩy)", "Link bình luận"])
        self.product_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.product_table, 6, 0, 1, 2)
        product_button_layout = QHBoxLayout()
        self.add_product_button = QPushButton("Thêm Sản phẩm")
        self.remove_product_button = QPushButton("Xóa Sản phẩm")
        product_button_layout.addWidget(self.add_product_button)
        product_button_layout.addWidget(self.remove_product_button)
        layout.addLayout(product_button_layout, 7, 0, 1, 2)
        self.save_config_button = QPushButton("Lưu Cấu hình")
        layout.addWidget(self.save_config_button, 8, 0, 1, 2)

    def create_controls_tab(self):
        """Tạo tab 'Điều khiển'."""
        self.controls_tab = QWidget()
        self.tabs.addTab(self.controls_tab, "Điều khiển")
        layout = QVBoxLayout(self.controls_tab)
        control_buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Bắt đầu Chạy")
        self.start_button.setStyleSheet("background-color: lightgreen;")
        self.pause_button = QPushButton("Tạm dừng")
        self.resume_button = QPushButton("Tiếp tục")
        self.stop_button = QPushButton("Dừng")
        self.stop_button.setStyleSheet("background-color: lightcoral;")
        control_buttons_layout.addWidget(self.start_button)
        control_buttons_layout.addWidget(self.pause_button)
        control_buttons_layout.addWidget(self.resume_button)
        control_buttons_layout.addWidget(self.stop_button)
        layout.addLayout(control_buttons_layout)
        options_layout = QHBoxLayout()
        self.headless_checkbox = QCheckBox("Chạy ở chế độ Headless (ẩn trình duyệt)")
        self.test_mode_checkbox = QCheckBox("Chế độ Thử nghiệm (chỉ log, không bình luận)")
        options_layout.addWidget(self.headless_checkbox)
        options_layout.addWidget(self.test_mode_checkbox)
        layout.addLayout(options_layout)
        layout.addStretch()
        self.update_control_buttons_state(is_running=False)

    def create_logs_tab(self):
        """Tạo tab 'Logs'."""
        self.logs_tab = QWidget()
        self.tabs.addTab(self.logs_tab, "Logs")
        layout = QVBoxLayout(self.logs_tab)
        self.log_display = QTextEdit(readOnly=True)
        layout.addWidget(self.log_display)
        self.export_logs_button = QPushButton("Xuất Logs ra file CSV")
        layout.addWidget(self.export_logs_button)

    def connect_signals(self):
        """Kết nối signals với slots."""
        # Tab Cấu hình
        self.save_config_button.clicked.connect(self.save_settings_from_ui)
        self.add_group_button.clicked.connect(self.add_group)
        self.remove_group_button.clicked.connect(self.remove_group)
        self.add_product_button.clicked.connect(self.add_product_row)
        self.remove_product_button.clicked.connect(self.remove_product_row)
        # Tab Điều khiển
        self.start_button.clicked.connect(self.start_scraping)
        self.stop_button.clicked.connect(self.stop_scraping)
        self.pause_button.clicked.connect(self.pause_scraping)
        self.resume_button.clicked.connect(self.resume_scraping)
        # Tab Logs
        self.export_logs_button.clicked.connect(self.export_logs)
        # Logger
        logger.log_updated.connect(self.log_display.append)

    def update_control_buttons_state(self, is_running, is_paused=False):
        """Cập nhật trạng thái của các nút điều khiển."""
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        self.pause_button.setEnabled(is_running and not is_paused)
        self.resume_button.setEnabled(is_running and is_paused)
        self.config_tab.setEnabled(not is_running)

    # --- Slots cho Scraper ---

    def start_scraping(self):
        """Bắt đầu tiến trình scraping trong một luồng mới."""
        self.save_settings_from_ui() # Luôn lấy cấu hình mới nhất

        if not self.config_data["facebook_credentials"]["email"] or not self.config_data["facebook_credentials"]["password"]:
            QMessageBox.critical(self, "Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu Facebook.")
            return

        self.scraper = FacebookScraper(config=self.config_data)
        self.scraper_thread = QThread()
        self.scraper.moveToThread(self.scraper_thread)

        # Kết nối signals từ scraper đến slots trong GUI
        self.scraper.log_signal.connect(lambda level, msg: logger.log(level, msg))
        self.scraper.status_signal.connect(self.update_status_bar)
        self.scraper.finished_signal.connect(self.on_scraping_finished)

        # Bắt đầu luồng
        self.scraper_thread.started.connect(self.scraper.run)
        self.scraper_thread.start()

        self.update_control_buttons_state(is_running=True)
        self.tabs.setCurrentWidget(self.logs_tab)

    def stop_scraping(self):
        """Gửi tín hiệu dừng đến luồng scraper."""
        if self.scraper:
            self.scraper.stop()
        self.status_bar.showMessage("Đang yêu cầu dừng...")
        self.stop_button.setEnabled(False) # Vô hiệu hóa để tránh click nhiều lần

    def pause_scraping(self):
        if self.scraper:
            self.scraper.pause()
            self.update_control_buttons_state(is_running=True, is_paused=True)

    def resume_scraping(self):
        if self.scraper:
            self.scraper.resume()
            self.update_control_buttons_state(is_running=True, is_paused=False)

    def on_scraping_finished(self):
        """Dọn dẹp sau khi luồng scraper kết thúc."""
        logger.log("INFO", "Tiến trình scraping đã kết thúc.")
        self.scraper_thread.quit()
        self.scraper_thread.wait()
        self.scraper_thread = None
        self.scraper = None
        self.update_control_buttons_state(is_running=False)
        self.update_status_bar("Dừng")

    # --- Slots và các hàm khác ---

    def update_status_bar(self, status):
        """Cập nhật thanh trạng thái."""
        self.status_bar.showMessage(f"Trạng thái: {status}")

    def load_settings_to_ui(self):
        """Tải dữ liệu từ self.config_data và điền vào các trường trên GUI."""
        creds = self.config_data.get("facebook_credentials", {})
        self.email_input.setText(creds.get("email", ""))
        self.password_input.setText(creds.get("password", ""))
        self.group_list_widget.clear()
        self.group_list_widget.addItems(self.config_data.get("groups", []))
        products = self.config_data.get("products", [])
        self.product_table.setRowCount(len(products))
        for row, prod in enumerate(products):
            self.product_table.setItem(row, 0, QTableWidgetItem(prod.get("name", "")))
            self.product_table.setItem(row, 1, QTableWidgetItem(prod.get("keywords", "")))
            self.product_table.setItem(row, 2, QTableWidgetItem(prod.get("link", "")))
        settings = self.config_data.get("settings", {})
        self.headless_checkbox.setChecked(settings.get("headless", False))
        self.test_mode_checkbox.setChecked(settings.get("test_mode", True))

    def save_settings_from_ui(self):
        """Lấy dữ liệu từ GUI và lưu vào file."""
        self.config_data["facebook_credentials"]["email"] = self.email_input.text()
        self.config_data["facebook_credentials"]["password"] = self.password_input.text()
        self.config_data["groups"] = [self.group_list_widget.item(i).text() for i in range(self.group_list_widget.count())]
        products = []
        for row in range(self.product_table.rowCount()):
            products.append({
                "name": self.product_table.item(row, 0).text() if self.product_table.item(row, 0) else "",
                "keywords": self.product_table.item(row, 1).text() if self.product_table.item(row, 1) else "",
                "link": self.product_table.item(row, 2).text() if self.product_table.item(row, 2) else ""
            })
        self.config_data["products"] = products
        self.config_data["settings"]["headless"] = self.headless_checkbox.isChecked()
        self.config_data["settings"]["test_mode"] = self.test_mode_checkbox.isChecked()
        save_config(self.config_data)
        logger.log("INFO", "Cấu hình đã được lưu.")

    def add_group(self): self.group_list_widget.addItem("https://facebook.com/groups/new_group")
    def remove_group(self): self.group_list_widget.takeItem(self.group_list_widget.currentRow())
    def add_product_row(self): self.product_table.insertRow(self.product_table.rowCount())
    def remove_product_row(self): self.product_table.removeRow(self.product_table.currentRow())

    def export_logs(self):
        """Xuất dữ liệu từ SQLite ra file CSV."""
        db_name = "log.db"
        if not os.path.exists(db_name):
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy file log.db. Hãy chạy tool để tạo log trước.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Lưu file CSV", "", "CSV Files (*.csv)")
        if not save_path:
            return

        try:
            conn = sqlite3.connect(db_name)
            df = pd.read_sql_query("SELECT * FROM logs", conn)
            conn.close()
            df.to_csv(save_path, index=False, encoding='utf-8-sig')
            QMessageBox.information(self, "Thành công", f"Đã xuất logs thành công ra file:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Xuất logs thất bại: {e}")
            logger.log("ERROR", f"Xuất logs thất bại: {e}")

    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ."""
        if self.scraper_thread and self.scraper_thread.isRunning():
            reply = QMessageBox.question(self, 'Thoát', "Tiến trình scraping đang chạy. Bạn có chắc chắn muốn thoát?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_scraping()
                self.scraper_thread.quit()
                self.scraper_thread.wait(5000) # Chờ tối đa 5s
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
