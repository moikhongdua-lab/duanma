SCHEMA_PHUCAP_THUONGPHAT = {
    "PHUCAP_THUONGPHAT": {
        "cols": {
            "MaPCP": "int",
            "MaNV": "int",
            "Loai": "str",
            "SoTien": "float",
            "NgayGhiNhan": "date",
            "LyDo": "str"
        },

        "pk": ["MaPCP"],

        "fk": {
            "MaNV": ("NHANVIEN", "MaNV")
        },

        "notnull": [
            "MaNV",
            "Loai",
            "SoTien"
        ],

        "check": {
            "Loai": ["Thưởng", "Phụ cấp", "Phạt"]
        },

        "khoang": {
            "SoTien": (0, None)
        }
    }
}