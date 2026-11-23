"""Ép kiểu dữ liệu theo schema.

Quy tắc chính: ô rỗng/null KHÔNG làm mất dòng. Ô đó được lưu là NA
(Int64 / Float64 / string / datetime64 đều chứa được NA) và các ô còn lại của
dòng vẫn được đẩy lên bình thường. Chỉ cột pk và cột "notnull" mới bị chặn khi rỗng.
"""
import math
from datetime import date, datetime, time

import pandas as pd

# kiểu trong schema -> dtype của pandas (loại "nullable" để chứa được NA)
DTYPE = {"int": "Int64", "float": "Float64", "str": "string",
         "date": "datetime64[ns]", "time": "string"}   # time lưu dạng "HH:MM:SS"

_CHUOI_NULL = {"", "nan", "none", "null", "na", "n/a", "nat", "<na>"}
_DINH_DANG_NGAY = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d")


def la_null(v) -> bool:
    if v is None or v is pd.NA or v is pd.NaT:
        return True
    if isinstance(v, str):
        return v.strip().lower() in _CHUOI_NULL
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def parse_time(value) -> str | None:
    """Chuẩn hóa về 'HH:MM:SS'. Nhận 'HH:MM', 'HH:MM:SS', datetime.time, datetime, Timestamp."""
    if la_null(value):
        return None
    if isinstance(value, (time, datetime, pd.Timestamp)):
        return f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}"
    parts = str(value).strip().split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"Giờ không hợp lệ: {value!r}")
    try:
        h, m = int(parts[0]), int(parts[1])
        s = int(parts[2]) if len(parts) == 3 else 0
    except ValueError:
        raise ValueError(f"Giờ không hợp lệ: {value!r}") from None
    if not (0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60):
        raise ValueError(f"Giờ không hợp lệ: {value!r}")
    return f"{h:02d}:{m:02d}:{s:02d}"


def _ep_int(v):
    if isinstance(v, bool):
        raise ValueError(f"không phải số nguyên: {v!r}")
    try:
        f = float(v.strip()) if isinstance(v, str) else float(v)
    except (TypeError, ValueError):
        raise ValueError(f"không phải số nguyên: {v!r}") from None
    if not math.isfinite(f) or not f.is_integer():
        raise ValueError(f"không phải số nguyên: {v!r}")
    return int(f)


def _ep_float(v):
    if isinstance(v, bool):
        raise ValueError(f"không phải số: {v!r}")
    try:
        f = float(v.strip()) if isinstance(v, str) else float(v)
    except (TypeError, ValueError):
        raise ValueError(f"không phải số: {v!r}") from None
    if not math.isfinite(f):
        raise ValueError(f"không phải số: {v!r}")
    return f


def _ep_str(v):
    return str(v).strip()


def _ep_date(v):
    if isinstance(v, (pd.Timestamp, datetime)):
        return pd.Timestamp(v).tz_localize(None).normalize() if getattr(v, "tzinfo", None) else pd.Timestamp(v).normalize()
    if isinstance(v, date):
        return pd.Timestamp(v)
    s = str(v).strip()
    if len(s) > 10 and s[10] in " T":      # '2026-11-22 00:00:00' -> lấy phần ngày
        s = s[:10]
    for dinh_dang in _DINH_DANG_NGAY:
        try:
            return pd.Timestamp(datetime.strptime(s, dinh_dang))
        except ValueError:
            pass
    raise ValueError(f"ngày không hợp lệ: {v!r} (dùng YYYY-MM-DD hoặc DD/MM/YYYY)")


_BO_EP = {"int": _ep_int, "float": _ep_float, "str": _ep_str,
          "date": _ep_date, "time": parse_time}


def _thanh_series(gia_tri: list, kieu: str, index) -> pd.Series:
    if kieu == "date":
        return pd.Series(pd.to_datetime(gia_tri), index=index).astype("datetime64[ns]")
    return pd.Series(gia_tri, index=index, dtype=DTYPE[kieu])


def tao_bang_rong(ten_bang: str) -> pd.DataFrame:
    """Bảng rỗng nhưng đã đúng tên cột và dtype theo schema."""
    from database.schema import SCHEMA
    cols = SCHEMA[ten_bang]["cols"]
    return pd.DataFrame({c: pd.Series(dtype=DTYPE[k]) for c, k in cols.items()})


def ep_kieu(ten_bang: str, df: pd.DataFrame) -> pd.DataFrame:
    """Ép toàn bộ cột về đúng kiểu schema. Gom hết lỗi rồi báo một lần."""
    from database.schema import SCHEMA          # import trễ để tránh vòng lặp import
    cols = SCHEMA[ten_bang]["cols"]
    la = [c for c in df.columns if c not in cols]
    if la:
        raise ValueError(f"{ten_bang}: cột không có trong schema: {la}")

    loi, ket_qua = [], {}
    for cot, kieu in cols.items():
        nguon = df[cot].tolist() if cot in df.columns else [None] * len(df)
        gia_tri = []
        for i, v in zip(df.index, nguon):
            if la_null(v):
                gia_tri.append(None)             # ô rỗng -> NA, dòng vẫn giữ nguyên
                continue
            try:
                gia_tri.append(_BO_EP[kieu](v))
            except ValueError as e:
                loi.append(f"  dòng {i}, cột {cot}: {e}")
                gia_tri.append(None)
        ket_qua[cot] = _thanh_series(gia_tri, kieu, df.index)
    if loi:
        raise ValueError(f"{ten_bang}: lỗi kiểu dữ liệu\n" + "\n".join(loi))
    return pd.DataFrame(ket_qua, index=df.index)
