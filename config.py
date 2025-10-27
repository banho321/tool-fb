# config.py
"""
Module này chịu trách nhiệm quản lý cấu hình của ứng dụng.
"""
import json
import os

CONFIG_FILE = "config.json"

def get_default_config():
    """
    Trả về một cấu trúc từ điển chứa cấu hình mặc định.
    """
    return {
        "facebook_credentials": {
            "email": "",
            "cookie_file_path": ""
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
            "firefox_binary_path": ""
        }
    }

def load_config():
    """
    Tải cấu hình từ file, đảm bảo các trường mới tồn tại.
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
            if "cookie_file_path" not in config_data.get("facebook_credentials", {}):
                config_data["facebook_credentials"]["cookie_file_path"] = ""
            if "password" in config_data.get("facebook_credentials", {}):
                del config_data["facebook_credentials"]["password"] # Xóa trường cũ
            if "firefox_binary_path" not in config_data.get("settings", {}):
                config_data["settings"]["firefox_binary_path"] = ""
            if "chrome_binary_path" in config_data.get("settings", {}):
                del config_data["settings"]["chrome_binary_path"] # Xóa trường cũ

            return config_data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Lỗi khi đọc file cấu hình: {e}. Sử dụng cấu hình mặc định.")
        return get_default_config()

def save_config(config_data):
    """
    Lưu dictionary cấu hình vào file CONFIG_FILE.
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print(f"Cấu hình đã được lưu thành công vào '{CONFIG_FILE}'.")
    except IOError as e:
        print(f"Lỗi khi lưu file cấu hình: {e}")
