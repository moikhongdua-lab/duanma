import pandas as pd
from datetime import time, datetime
from database.kieu_dl import ep_kieu # chỉnh lại đường dẫn import cho khớp dự án của bạn

GIO_CHUAN = 8.0  

SCHEMA_CHAMCONG = {
    "BANGCHAMCONG": {
        "cols": {"MaCC": "int", "MaNV": "int", "MaCa": "int",
                 "GioVaoThucTe": "time", "GioRaThucTe": "time",
                 "NgayChamCong": "date", "Cong": "float"},  # Cong: tự tính
        "pk": ["MaCC"],
        "fk": {"MaNV": ("NHANVIEN", "MaNV"), "MaCa": ("CALAMVIEC", "MaCa")},
        "unique": [["MaNV", "MaCa", "NgayChamCong"]],
    },
}


def _parse_time(value) -> str | None:
    """Chuẩn hóa về 'HH:MM:SS'. Nhận str ('08:30' hoặc '08:30:15'), datetime.time, datetime, Timestamp."""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (time, datetime, pd.Timestamp)):
        return f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}"
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


def so_gio_lam(vao, ra) -> float:
    """Số giờ làm; ca đêm (ra < vao) tự cộng thêm 24h."""
    vao, ra = _parse_time(vao), _parse_time(ra)
    if vao is None or ra is None:
        return 0.0
    phut_vao, phut_ra = _to_minutes(vao), _to_minutes(ra)
    if phut_ra < phut_vao:
        phut_ra += 24 * 60
    return (phut_ra - phut_vao) / 60


def tinh_cong(vao, ra, he_so: float, gio_chuan: float = GIO_CHUAN) -> float:
    """Công = (giờ làm / giờ chuẩn, tối đa 1) x hệ số ca."""
    return round(min(so_gio_lam(vao, ra) / gio_chuan, 1.0) * he_so, 2)


def kiem_tra_trung(df: pd.DataFrame) -> None:
    dup = df.duplicated(["MaNV", "MaCa", "NgayChamCong"], keep=False)
    if dup.any():
        raise ValueError(f"Chấm công trùng:\n{df[dup]}")


def cap_nhat_cong(chamcong: pd.DataFrame, calamviec: pd.DataFrame) -> pd.DataFrame:
    """Tính lại cột Cong cho toàn bộ BANGCHAMCONG (đã nhân hệ số ca)."""
    he_so = calamviec.set_index("MaCa")["HeSoCa"]
    thieu = set(chamcong["MaCa"]) - set(he_so.index)
    if thieu:
        raise ValueError(f"MaCa không tồn tại trong CALAMVIEC: {sorted(thieu)}")
    kiem_tra_trung(chamcong)
    chamcong = chamcong.copy()
    chamcong["Cong"] = [
        tinh_cong(v, r, he_so.loc[ca])
        for v, r, ca in zip(chamcong["GioVaoThucTe"],
                            chamcong["GioRaThucTe"], chamcong["MaCa"])
    ]
    return ep_kieu("BANGCHAMCONG", chamcong)