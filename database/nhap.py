"""
Tạo các bảng của database LUONG bằng pandas (không kết nối DB).
Mỗi bảng = 1 DataFrame + 1 file CSV. Chỉ dùng pandas + thư viện chuẩn.

Quy tắc nghiệp vụ:
  - Cong (1 dòng chấm công):
      giờ làm = giờ ra - giờ vào (ca đêm: giờ ra < giờ vào thì cộng thêm 24h)
      giờ làm <= 8h : Cong = giờ làm / 8 * HeSoCa
      giờ làm  > 8h : Cong = 1 * HeSoCa + (giờ làm - 8) / 8 * 1.5   (tăng ca KHÔNG nhân HeSoCa)
      VD ca 2 (1.2) làm 10h: 1*1.2 + 2/8*1.5 = 1.575
  - BANGLUONG:
      TongCong         = tổng Cong của nhân viên trong tháng
      TongThuongPhuCap = tổng SoTien có Loai in (Thưởng, Phụ cấp)
      TongPhat         = tổng SoTien có Loai = Phạt
      LuongThucNhan    = LuongCoBan * TongCong - TongPhat + TongThuongPhuCap
"""
import pandas as pd

HE_SO_TANG_CA = 1.5
GIO_CHUAN = 8.0
LOAI_CONG_THEM = {"Thưởng", "Phụ cấp"}
LOAI_PHAT = {"Phạt"}

# ---------------------------------------------------------------------------
# 1. ĐỊNH NGHĨA SCHEMA (kiểu dữ liệu, khóa chính, khóa ngoại, NOT NULL)
#    Kiểu: int | float | str | date | time(chuỗi HH:MM:SS)
# ---------------------------------------------------------------------------
SCHEMA = {
    "CALAMVIEC": {
        "cols": {"MaCa": "int", "TenCa": "str", "GioBatDau": "time",
                 "GioKetThuc": "time", "HeSoCa": "float"},
        "pk": ["MaCa"], "fk": {},
    },
    "PHONGBAN": {
        "cols": {"MaPB": "int", "TenPB": "str", "SDT": "str"},
        "pk": ["MaPB"], "fk": {},
    },
    "NhanVien": {
        "cols": {"MaNV": "int", "HoTen": "str", "NgaySinh": "date",
                 "GioiTinh": "str", "ChucVu": "str", "LuongCoBan": "float",
                 "MaPB": "int"},
        "pk": ["MaNV"], "fk": {"MaPB": ("PHONGBAN", "MaPB")},
    },
    "PHUCAP_THUONGPHAT": {
        "cols": {"MaPCP": "int", "MaNV": "int", "Loai": "str",
                 "SoTien": "float", "NgayGhiNhan": "date", "LyDo": "str"},
        "pk": ["MaPCP"], "fk": {"MaNV": ("NhanVien", "MaNV")},
    },
    "BANGCHAMCONG": {
        "cols": {"MaCC": "int", "MaNV": "int", "MaCa": "int",
                 "GioVaoThucTe": "time", "GioRaThucTe": "time",
                 "NgayChamCong": "date", "Cong": "float"},   # Cong: tự tính
        "pk": ["MaCC"],
        "fk": {"MaNV": ("NhanVien", "MaNV"), "MaCa": ("CALAMVIEC", "MaCa")},
    },
    "BANGLUONG": {
        "cols": {"MaLuong": "int", "MaNV": "int", "ThangNam": "date",
                 "TongCong": "float", "TongThuongPhuCap": "float",
                 "TongPhat": "float", "LuongThucNhan": "float"},
        "pk": ["MaLuong"], "fk": {"MaNV": ("NhanVien", "MaNV")},
    },
    "LICHSULUONG": {
        "cols": {"MaLSL": "int", "MaNV": "int", "LuongCoBan": "float",
                 "NgayApDung": "date", "NgayKetThuc": "date",
                 "LyDoThayDoi": "str"},
        "pk": ["MaLSL"], "fk": {"MaNV": ("NhanVien", "MaNV")},
    },
}

# Thứ tự tạo bảng (bảng cha trước, bảng con sau)
THU_TU = ["CALAMVIEC", "PHONGBAN", "NhanVien", "PHUCAP_THUONGPHAT",
          "BANGCHAMCONG", "BANGLUONG", "LICHSULUONG"]

# Giới hạn độ dài varchar giống bản SQL
VARCHAR_LEN = {
    ("CALAMVIEC", "TenCa"): 50, ("PHONGBAN", "TenPB"): 50,
    ("PHONGBAN", "SDT"): 15, ("NhanVien", "HoTen"): 50,
    ("NhanVien", "GioiTinh"): 10, ("NhanVien", "ChucVu"): 50,
    ("PHUCAP_THUONGPHAT", "Loai"): 50, ("PHUCAP_THUONGPHAT", "LyDo"): 1500,
    ("LICHSULUONG", "LyDoThayDoi"): 500,
}


# ---------------------------------------------------------------------------
# 2. CHUẨN HÓA KIỂU + KIỂM TRA KHÓA
# ---------------------------------------------------------------------------
def _parse_time(value) -> str | None:
    """Chuẩn hóa về 'HH:MM:SS'. Chấp nhận 'HH:MM' hoặc 'HH:MM:SS'."""
    if pd.isna(value):
        return None
    parts = str(value).strip().split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"Giờ không hợp lệ: {value!r}")
    h, m = int(parts[0]), int(parts[1])
    s = int(parts[2]) if len(parts) == 3 else 0
    if not (0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60):
        raise ValueError(f"Giờ không hợp lệ: {value!r}")
    return f"{h:02d}:{m:02d}:{s:02d}"


def _to_minutes(t: str) -> float:
    h, m, s = (int(x) for x in t.split(":"))
    return h * 60 + m + s / 60


def ep_kieu(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Ép DataFrame về đúng kiểu dữ liệu theo SCHEMA."""
    spec = SCHEMA[name]["cols"]
    df = df.reindex(columns=list(spec))          # đúng thứ tự & đủ cột
    for col, kind in spec.items():
        if kind == "int":
            df[col] = pd.to_numeric(df[col]).astype("Int64")
        elif kind == "float":
            df[col] = pd.to_numeric(df[col]).astype("Float64")
        elif kind == "date":
            df[col] = pd.to_datetime(df[col]).dt.normalize()
        elif kind == "time":
            df[col] = df[col].map(_parse_time).astype("string")
        else:
            df[col] = df[col].astype("string")
            limit = VARCHAR_LEN.get((name, col))
            if limit and (df[col].str.len() > limit).any():
                raise ValueError(f"{name}.{col} vượt quá varchar({limit})")
    return df


def kiem_tra_khoa_chinh(name: str, df: pd.DataFrame) -> None:
    pk = SCHEMA[name]["pk"]
    if df[pk].isna().any().any():
        raise ValueError(f"{name}: khóa chính {pk} có giá trị NULL")
    if df.duplicated(subset=pk).any():
        raise ValueError(f"{name}: khóa chính {pk} bị trùng")


def kiem_tra_khoa_ngoai(name: str, df: pd.DataFrame,
                        db: dict[str, pd.DataFrame]) -> None:
    for col, (bang_cha, col_cha) in SCHEMA[name]["fk"].items():
        gia_tri = df[col].dropna()                # FK cho phép NULL như SQL
        thieu = set(gia_tri) - set(db[bang_cha][col_cha].dropna())
        if thieu:
            raise ValueError(
                f"{name}.{col} tham chiếu {bang_cha}.{col_cha} không tồn tại: "
                f"{sorted(thieu)}")


# ---------------------------------------------------------------------------
# 3. TỰ ĐỘNG TÍNH TOÁN
# ---------------------------------------------------------------------------
def so_gio_lam(vao: str | None, ra: str | None) -> float:
    """Số giờ làm; ca đêm (ra < vao) tự cộng thêm 24h."""
    if vao is None or ra is None or pd.isna(vao) or pd.isna(ra):
        return 0.0
    phut_vao, phut_ra = _to_minutes(vao), _to_minutes(ra)
    if phut_ra < phut_vao:
        phut_ra += 24 * 60
    return (phut_ra - phut_vao) / 60


def tinh_cong(vao, ra, he_so_ca) -> float:
    gio = so_gio_lam(vao, ra)
    if gio <= GIO_CHUAN:
        cong = gio / GIO_CHUAN * he_so_ca
    else:
        cong = 1.0 * he_so_ca + (gio - GIO_CHUAN) / GIO_CHUAN * HE_SO_TANG_CA
    return round(cong, 4)


def cap_nhat_cong(chamcong: pd.DataFrame, calamviec: pd.DataFrame) -> pd.DataFrame:
    """Tính lại cột Cong cho toàn bộ BANGCHAMCONG (đã nhân hệ số ca)."""
    he_so = calamviec.set_index("MaCa")["HeSoCa"]
    chamcong = chamcong.copy()
    chamcong["Cong"] = [
        tinh_cong(v, r, he_so.loc[ca])
        for v, r, ca in zip(chamcong["GioVaoThucTe"],
                            chamcong["GioRaThucTe"], chamcong["MaCa"])
    ]
    return ep_kieu("BANGCHAMCONG", chamcong)


def tinh_bang_luong(nhanvien: pd.DataFrame, chamcong: pd.DataFrame,
                    pcp: pd.DataFrame) -> pd.DataFrame:
    """Sinh BANGLUONG theo từng (nhân viên, tháng)."""
    cc = chamcong.assign(
        ThangNam=chamcong["NgayChamCong"].dt.to_period("M").dt.to_timestamp())
    tong_cong = (cc.groupby(["MaNV", "ThangNam"], as_index=False)["Cong"]
                   .sum().rename(columns={"Cong": "TongCong"}))

    p = pcp.assign(
        ThangNam=pcp["NgayGhiNhan"].dt.to_period("M").dt.to_timestamp())
    p["Thuong"] = p["SoTien"].where(p["Loai"].isin(LOAI_CONG_THEM), 0.0)
    p["Phat"] = p["SoTien"].where(p["Loai"].isin(LOAI_PHAT), 0.0)
    tong_pcp = (p.groupby(["MaNV", "ThangNam"], as_index=False)[["Thuong", "Phat"]]
                  .sum().rename(columns={"Thuong": "TongThuongPhuCap",
                                         "Phat": "TongPhat"}))

    bl = tong_cong.merge(tong_pcp, on=["MaNV", "ThangNam"], how="outer")
    bl = bl.merge(nhanvien[["MaNV", "LuongCoBan"]], on="MaNV", how="left")
    for col in ("TongCong", "TongThuongPhuCap", "TongPhat"):
        bl[col] = bl[col].astype("float64").fillna(0.0)

    bl["LuongThucNhan"] = (bl["LuongCoBan"].astype("float64") * bl["TongCong"]
                           - bl["TongPhat"] + bl["TongThuongPhuCap"]).round(2)
    bl["TongCong"] = bl["TongCong"].round(4)

    bl = bl.sort_values(["ThangNam", "MaNV"]).reset_index(drop=True)
    bl["MaLuong"] = range(1, len(bl) + 1)
    return ep_kieu("BANGLUONG", bl)


# ---------------------------------------------------------------------------
# 4. DỮ LIỆU MẪU
# ---------------------------------------------------------------------------
def du_lieu_mau() -> dict[str, pd.DataFrame]:
    return {
        "CALAMVIEC": pd.DataFrame([
            (1, "Ca sáng", "06:00", "14:00", 1.0),
            (2, "Ca tối", "18:00", "02:00", 1.2),
        ], columns=["MaCa", "TenCa", "GioBatDau", "GioKetThuc", "HeSoCa"]),
        "PHONGBAN": pd.DataFrame([
            (1, "Kỹ thuật", "0241234567"),
            (2, "Kinh doanh", "0247654321"),
        ], columns=["MaPB", "TenPB", "SDT"]),
        "NhanVien": pd.DataFrame([
            (1, "Nguyễn Văn An", "1995-03-12", "Nam", "Kỹ sư", 300000, 1),
            (2, "Trần Thị Bình", "1998-07-25", "Nữ", "Nhân viên", 250000, 2),
        ], columns=["MaNV", "HoTen", "NgaySinh", "GioiTinh", "ChucVu",
                    "LuongCoBan", "MaPB"]),
        "PHUCAP_THUONGPHAT": pd.DataFrame([
            (1, 1, "Phụ cấp", 500000, "2026-11-01", "Phụ cấp ăn trưa"),
            (2, 1, "Thưởng", 1000000, "2026-11-10", "Hoàn thành dự án"),
            (3, 2, "Phạt", 200000, "2026-11-05", "Đi muộn nhiều lần"),
        ], columns=["MaPCP", "MaNV", "Loai", "SoTien", "NgayGhiNhan", "LyDo"]),
        "BANGCHAMCONG": pd.DataFrame([
            (1, 1, 1, "06:00", "14:00", "2026-11-02"),   # 8h ca 1   -> 1.0
            (2, 1, 1, "06:00", "16:00", "2026-11-03"),   # 10h ca 1  -> 1 + 2/8*1.5 = 1.375
            (3, 2, 2, "18:00", "02:00", "2026-11-02"),   # 8h ca 2   -> 1.2
            (4, 2, 2, "18:00", "04:00", "2026-11-03"),   # 10h ca 2  -> 1.2 + 0.375 = 1.575
            (5, 2, 1, "06:00", "10:00", "2026-11-04"),   # 4h ca 1   -> 0.5
        ], columns=["MaCC", "MaNV", "MaCa", "GioVaoThucTe", "GioRaThucTe",
                    "NgayChamCong"]),
        "LICHSULUONG": pd.DataFrame([
            (1, 1, 280000, "2025-01-01", "2026-06-30", "Lương khởi điểm"),
            (2, 1, 300000, "2026-07-01", None, "Tăng lương định kỳ"),
            (3, 2, 250000, "2025-06-01", None, "Lương khởi điểm"),
        ], columns=["MaLSL", "MaNV", "LuongCoBan", "NgayApDung", "NgayKetThuc",
                    "LyDoThayDoi"]),
    }


# ---------------------------------------------------------------------------
# 5. XÂY DỰNG TOÀN BỘ DATABASE + XUẤT FILE
# ---------------------------------------------------------------------------
def xay_dung_database(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    db: dict[str, pd.DataFrame] = {}

    # Bảng không phụ thuộc phép tính
    for name in ("CALAMVIEC", "PHONGBAN", "NhanVien", "PHUCAP_THUONGPHAT",
                 "LICHSULUONG"):
        df = ep_kieu(name, raw[name])
        kiem_tra_khoa_chinh(name, df)
        kiem_tra_khoa_ngoai(name, df, db)
        db[name] = df

    # BANGCHAMCONG: Cong tự tính
    cc = ep_kieu("BANGCHAMCONG", raw["BANGCHAMCONG"])
    kiem_tra_khoa_chinh("BANGCHAMCONG", cc)
    kiem_tra_khoa_ngoai("BANGCHAMCONG", cc, db)
    db["BANGCHAMCONG"] = cap_nhat_cong(cc, db["CALAMVIEC"])

    # BANGLUONG: tự tính từ chấm công + thưởng/phạt/phụ cấp
    bl = tinh_bang_luong(db["NhanVien"], db["BANGCHAMCONG"],
                         db["PHUCAP_THUONGPHAT"])
    kiem_tra_khoa_chinh("BANGLUONG", bl)
    kiem_tra_khoa_ngoai("BANGLUONG", bl, db)
    db["BANGLUONG"] = bl
    return {name: db[name] for name in THU_TU}


def xuat_csv(db: dict[str, pd.DataFrame]) -> None:
    """Ghi mỗi bảng thành <TENBANG>.csv trong thư mục đang chạy script."""
    for name, df in db.items():
        df.to_csv(f"{name}.csv", index=False,
                  date_format="%Y-%m-%d", encoding="utf-8-sig")


if __name__ == "__main__":
    database = xay_dung_database(du_lieu_mau())
    xuat_csv(database)
    pd.set_option("display.width", 200, "display.max_columns", None)
    for ten, bang in database.items():
        print(f"\n=== {ten} ===")
        print(bang.to_string(index=False))
    print(f"\nĐã xuất {len(database)} file CSV vào thư mục hiện tại.")