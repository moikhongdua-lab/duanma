import pandas as pd

SCHEMA_BANGLUONG = {
    "BANGLUONG": {
        "cols": {
            "MaLuong": "int",
            "MaNV": "int",
            "ThangNam": "date",
            "TongCong": "float",
            "TongThuongPhuCap": "float",
            "TongPhat": "float",
            "LuongThucNhan": "float"
        },

        "pk": ["MaLuong"],

        "fk": {
            "MaNV": ("NHANVIEN", "MaNV")
        },

        "notnull": [
            "MaNV",
            "TongCong"
        ]
    }
}