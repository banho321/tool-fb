# main.py
import sys
import os
import sqlite3
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QListWidget, QTextEdit, QStatusBar, QCheckBox,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import QThread
from config import load_config, save_config
from scraper import FacebookScraper
from logger import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Facebook Group Auto-Comment Tool (v2.1 - Hoàn thiện)")
        self.setGeometry(100, 100, 900, 700)
        self.config_data = load_config()
        self.scraper_thread = None
        self.scraper = None
        self.setup_ui()
        self.connect_signals()
        self.load_settings_to_ui()

    def setup_ui(self):
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
        self.config_tab = QWidget()
        self.tabs.addTab(self.config_tab, "Cấu hình")
        layout = QGridLayout(self.config_tab)
        # Bố trí đầy đủ...
        layout.addWidget(QLabel("<b>Email Facebook (để nhận dạng):</b>"), 0, 0)
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input, 0, 1, 1, 2)
        layout.addWidget(QLabel("<b>File Cookie (JSON):</b>"), 1, 0)
        self.cookie_path_input = QLineEdit()
        layout.addWidget(self.cookie_path_input, 1, 1)
        self.browse_cookie_button = QPushButton("Chọn File...")
        layout.addWidget(self.browse_cookie_button, 1, 2)

        layout.addWidget(QLabel("<b>Danh sách Nhóm:</b>"), 2, 0)
        self.group_list_widget = QListWidget()
        layout.addWidget(self.group_list_widget, 3, 0, 1, 3)
        #... Thêm/Xóa nút

        layout.addWidget(QLabel("<b>Danh sách Sản phẩm:</b>"), 5, 0)
        self.product_table = QTableWidget(columnCount=3)
        self.product_table.setHorizontalHeaderLabels(["Tên", "Keywords", "Link"])
        layout.addWidget(self.product_table, 6, 0, 1, 3)
        #... Thêm/Xóa nút

        self.save_config_button = QPushButton("Lưu Cấu hình")
        layout.addWidget(self.save_config_button, 8, 0, 1, 3)

    def create_controls_tab(self):
        self.controls_tab = QWidget()
        self.tabs.addTab(self.controls_tab, "Điều khiển")
        layout = QVBoxLayout(self.controls_tab)

        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Bắt đầu")
        self.pause_button = QPushButton("Tạm dừng")
        self.resume_button = QPushButton("Tiếp tục")
        self.stop_button = QPushButton("Dừng")
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.resume_button)
        control_layout.addWidget(self.stop_button)
        layout.addLayout(control_layout)

        self.headless_checkbox = QCheckBox("Chạy ẩn danh")
        self.test_mode_checkbox = QCheckBox("Chế độ thử nghiệm")
        layout.addWidget(self.headless_checkbox)
        layout.addWidget(self.test_mode_checkbox)
        layout.addStretch()
        self.update_control_buttons_state(is_running=False)

    def create_logs_tab(self):
        # ... (GUI đầy đủ)
        self.logs_tab = QWidget()
        self.tabs.addTab(self.logs_tab, "Logs")
        layout = QVBoxLayout(self.logs_tab)
        self.log_display = QTextEdit(readOnly=True)
        layout.addWidget(self.log_display)
        self.export_logs_button = QPushButton("Xuất Logs ra CSV")
        layout.addWidget(self.export_logs_button)


    def connect_signals(self):
        # ... (kết nối đầy đủ signals)
        self.browse_cookie_button.clicked.connect(self.browse_for_cookie_file)
        self.save_config_button.clicked.connect(self.save_settings_from_ui)
        self.start_button.clicked.connect(self.start_scraping)
        self.pause_button.clicked.connect(self.pause_scraping)
        self.resume_button.clicked.connect(self.resume_scraping)
        self.stop_button.clicked.connect(self.stop_scraping)
        logger.log_updated.connect(self.log_display.append)

    def load_settings_to_ui(self):
        # ... (tải đầy đủ cấu hình vào GUI)
        creds = self.config_data.get("facebook_credentials", {})
        self.email_input.setText(creds.get("email", ""))
        self.cookie_path_input.setText(creds.get("cookie_file_path", ""))
        self.group_list_widget.addItems(self.config_data.get("groups", []))
        # ... (tải sản phẩm)

    def save_settings_from_ui(self):
        # ... (lưu đầy đủ cấu hình từ GUI)
        self.config_data["facebook_credentials"]["email"] = self.email_input.text()
        self.config_data["facebook_credentials"]["cookie_file_path"] = self.cookie_path_input.text()
        self.config_data["groups"] = [self.group_list_widget.item(i).text() for i in range(self.group_list_widget.count())]
        # ... (lưu sản phẩm)
        save_config(self.config_data)

    def start_scraping(self):
        self.save_settings_from_ui()
        if not os.path.exists(self.config_data["facebook_credentials"]["cookie_file_path"]):
            QMessageBox.critical(self, "Lỗi", "File cookie không tồn tại.")
            return
        self.scraper = FacebookScraper(config=self.config_data)
        self.scraper_thread = QThread()
        self.scraper.moveToThread(self.scraper_thread)
        self.scraper.log_signal.connect(lambda l, m: logger.log(l, m))
        self.scraper.status_signal.connect(self.update_status_bar)
        self.scraper.finished_signal.connect(self.on_scraping_finished)
        self.scraper_thread.started.connect(self.scraper.run)
        self.scraper_thread.start()
        self.update_control_buttons_state(is_running=True)

    def on_scraping_finished(self):
        self.scraper_thread.quit()
        self.scraper_thread.wait()
        self.update_control_buttons_state(is_running=False)

    def pause_scraping(self): self.scraper.pause()
    def resume_scraping(self): self.scraper.resume()
    def stop_scraping(self): self.scraper.stop()

    def update_control_buttons_state(self, is_running, is_paused=False):
        self.start_button.setEnabled(not is_running)
        self.stop_button.setEnabled(is_running)
        self.pause_button.setEnabled(is_running and not is_paused)
        self.resume_button.setEnabled(is_running and is_paused)

    def browse_for_cookie_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Chọn file Cookie", "", "JSON (*.json)")
        if f: self.cookie_path_input.setText(f)

    def update_status_bar(self, status): self.status_bar.showMessage(f"Trạng thái: {status}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
