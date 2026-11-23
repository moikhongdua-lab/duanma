calamvie = {
    "CALAMVIEC": {
        "cols": {
            "MaCa": "int",
            "TenCa": "str",
            "GioBatDau": "time",
            "GioKetThuc": "time",
            "HeSoCa": "float"
        },

        "pk": ["MaCa"],

        "fk": {},

        "notnull": [
            "TenCa",
            "GioBatDau",
            "GioKetThuc",
            "HeSoCa"
        ],

        "khoang": {
            "HeSoCa": (0, None)
        }
    }
}