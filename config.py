# config.py
"""
Module này chịu trách nhiệm quản lý cấu hình của ứng dụng.
"""
import json
import os

CONFIG_FILE = "config.json"

def get_default_config():
    """
    Hàm này làm gì: Trả về một cấu trúc từ điển (dictionary) chứa cấu hình mặc định.
    """
    return {
        "facebook_credentials": {
            "email": "",
            "password": ""
        },
        "groups": [
            "https://www.facebook.com/groups/examplegroup1"
        ],
        "products": [
            {
                "name": "Sản phẩm Mẫu",
                "keywords": "keyword1,từ khóa 2",
                "link": "https://example.com/product1"
            }
        ],
        "settings": {
            "headless": False,
            "test_mode": True,
            "max_posts_per_group": 10,
            "actions_per_hour": 100,
            "chrome_binary_path": ""
        }
    }

def load_config():
    """
    Hàm này làm gì: Tải cấu hình từ file CONFIG_FILE.
    """
    if not os.path.exists(CONFIG_FILE):
        print(f"File cấu hình '{CONFIG_FILE}' không tìm thấy, tạo file mới.")
        default_config = get_default_config()
        save_config(default_config)
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # Đảm bảo cấu hình cũ tương thích với phiên bản mới
            if "chrome_binary_path" not in config_data.get("settings", {}):
                config_data["settings"]["chrome_binary_path"] = ""
            return config_data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Lỗi khi đọc file cấu hình: {e}. Sử dụng cấu hình mặc định.")
        return get_default_config()

def save_config(config_data):
    """
    Hàm này làm gì: Lưu dictionary cấu hình vào file CONFIG_FILE.
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print(f"Cấu hình đã được lưu thành công vào '{CONFIG_FILE}'.")
    except IOError as e:
        print(f"Lỗi khi lưu file cấu hình: {e}")
