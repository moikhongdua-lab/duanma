import pandas as pd
from database.kieu_dl import ep_kieu, parse_time, la_null

GIO_CHUAN = 8.0        # 1 công = 8 giờ
HE_SO_TANG_CA = 1.5    # giờ vượt 8h; KHÔNG nhân HeSoCa

SCHEMA_CHAMCONG = {
    "BANGCHAMCONG": {
        "cols": {"MaCC": "int", "MaNV": "int", "MaCa": "int",
                 "GioVaoThucTe": "time", "GioRaThucTe": "time",
                 "NgayChamCong": "date", "Cong": "float"},
        "pk": ["MaCC"],
        "fk": {"MaNV": ("NHANVIEN", "MaNV"), "MaCa": ("CALAMVIEC", "MaCa")},
        "notnull": ["MaNV", "MaCa", "NgayChamCong"],   # giờ vào/ra được phép trống (quên chấm)
        "unique": [["MaNV", "MaCa", "NgayChamCong"]],
        "derived": ["Cong"],                            # tự tính, không cho nhập tay
    },
}


def _phut(t: str) -> float:
    h, m, s = (int(x) for x in t.split(":"))
    return h * 60 + m + s / 60


def so_gio_lam(vao, ra) -> float | None:
    """Số giờ làm; ca đêm (ra < vao) cộng thêm 24h. Thiếu giờ vào/ra -> None."""
    vao, ra = parse_time(vao), parse_time(ra)
    if vao is None or ra is None:
        return None
    p_vao, p_ra = _phut(vao), _phut(ra)
    if p_ra < p_vao:
        p_ra += 24 * 60
    return (p_ra - p_vao) / 60


def tinh_cong(vao, ra, he_so) -> float | None:
    """giờ <= 8: giờ/8 * HeSoCa;  giờ > 8: 1*HeSoCa + (giờ-8)/8 * 1.5."""
    gio = so_gio_lam(vao, ra)
    if gio is None or la_null(he_so):
        return None
    he_so = float(he_so)
    if gio <= GIO_CHUAN:
        return round(gio / GIO_CHUAN * he_so, 4)
    return round(he_so + (gio - GIO_CHUAN) / GIO_CHUAN * HE_SO_TANG_CA, 4)


def cap_nhat_cong(chamcong: pd.DataFrame, calamviec: pd.DataFrame) -> pd.DataFrame:
    """Tính lại cột Cong cho toàn bộ BANGCHAMCONG."""
    he_so = {int(k): v for k, v in calamviec.set_index("MaCa")["HeSoCa"].items()}
    chamcong = chamcong.copy()
    chamcong["Cong"] = [
        tinh_cong(vao, ra, he_so.get(int(ca)))
        for vao, ra, ca in zip(chamcong["GioVaoThucTe"],
                               chamcong["GioRaThucTe"], chamcong["MaCa"])
    ]
    return ep_kieu("BANGCHAMCONG", chamcong)
