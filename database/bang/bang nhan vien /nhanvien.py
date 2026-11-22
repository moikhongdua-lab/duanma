 nhanvien = { "NhanVien": {
        "cols": {"MaNV": "int", "HoTen": "str", "NgaySinh": "date",
                 "GioiTinh": "str", "ChucVu": "str", "LuongCoBan": "float",
                 "MaPB": "int"},
        "pk": ["MaNV"], "fk": {"MaPB": ("PHONGBAN", "MaPB")},
    },
}