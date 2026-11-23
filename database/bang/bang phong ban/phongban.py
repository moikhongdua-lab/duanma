SCHEMA_PHONGBAN = {
    "PHONGBAN": {
        "cols": {"MaPB": "int", "TenPB": "str", "SDT": "str"},
        "pk": ["MaPB"],
        "fk": {},
        "notnull": ["TenPB"],
        "unique": [["TenPB"]],
    },
}
