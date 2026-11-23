SCHEMA_NHANVIEN = {
    "NHANVIEN": {
        "cols": {"MaNV": "int", "HoTen": "str", "NgaySinh": "date",
                 "GioiTinh": "str", "ChucVu": "str", "LuongCoBan": "float",
                 "MaPB": "int"},
        "pk": ["MaNV"],
        "fk": {"MaPB": ("PHONGBAN", "MaPB")},
        "notnull": ["HoTen"],
        "check": {"GioiTinh": ["Nam", "Nữ", "Khác"]},
        "khoang": {"LuongCoBan": (0, None)},
    },
}
