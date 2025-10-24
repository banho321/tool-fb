# config.py
"""
Module này chịu trách nhiệm quản lý cấu hình của ứng dụng.

Chức năng:
- load_config(): Tải cấu hình từ file JSON. Nếu file không tồn tại, tạo cấu hình mặc định.
- save_config(): Lưu cấu hình hiện tại vào file JSON.

Ai gọi:
- main.py: Gọi load_config() khi khởi động để điền dữ liệu vào GUI.
- main.py: Gọi save_config() khi người dùng thay đổi cài đặt và muốn lưu lại.
"""
import json
import os

CONFIG_FILE = "config.json"

def get_default_config():
    """
    Hàm này làm gì: Trả về một cấu trúc từ điển (dictionary) chứa cấu hình mặc định.
    Ai gọi nó: Được gọi bởi load_config() khi file config.json không tồn tại.
    Input: Không có.
    Output: Một dictionary với các giá trị mặc định.
    """
    return {
        "facebook_credentials": {
            "email": "",
            "password": ""
        },
        "groups": [
            "https://www.facebook.com/groups/examplegroup1",
            "https://www.facebook.com/groups/examplegroup2"
        ],
        "products": [
            {
                "name": "Sản phẩm Mẫu 1",
                "keywords": "keyword1,từ khóa 2",
                "link": "https://example.com/product1"
            },
            {
                "name": "Sản phẩm Mẫu 2",
                "keywords": "keyword3,từ khóa 4",
                "link": "https://example.com/product2"
            }
        ],
        "settings": {
            "headless": False,
            "test_mode": True,
            "max_posts_per_group": 10,
            "actions_per_hour": 100
        }
    }

def load_config():
    """
    Hàm này làm gì: Tải cấu hình từ file CONFIG_FILE. Nếu file không tồn tại,
    nó sẽ tạo một file mới với cấu hình mặc định.
    Ai gọi nó: Được gọi từ main.py khi ứng dụng khởi động.
    Input: Không có.
    Output: Một dictionary chứa cấu hình của ứng dụng.
    """
    if not os.path.exists(CONFIG_FILE):
        print(f"File cấu hình '{CONFIG_FILE}' không tìm thấy, tạo file mới với giá trị mặc định.")
        default_config = get_default_config()
        save_config(default_config)
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Lỗi khi đọc file cấu hình: {e}. Sử dụng cấu hình mặc định.")
        return get_default_config()

def save_config(config_data):
    """
    Hàm này làm gì: Lưu dictionary cấu hình vào file CONFIG_FILE.
    Ai gọi nó: Được gọi từ main.py khi người dùng muốn lưu các thay đổi trong GUI.
    Input: config_data (dictionary) - Dữ liệu cấu hình cần lưu.
    Output: Không có.
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        print(f"Cấu hình đã được lưu thành công vào '{CONFIG_FILE}'.")
    except IOError as e:
        print(f"Lỗi khi lưu file cấu hình: {e}")
