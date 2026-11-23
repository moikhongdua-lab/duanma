import pandas as pd
from database.kieu_dl import la_null


def _doc_bang(bang):
    """Bảng (DataFrame hoặc dict các list) -> ({cột: list giá trị}, {cột: dtype})."""
    du_lieu = {c: list(bang[c]) for c in bang}
    kieu = {c: bang[c].dtype for c in bang} if isinstance(bang, pd.DataFrame) else {}
    return du_lieu, kieu


def ghep_bang(bang1, bang2, cot, kieu_ghep="inner"):
    """Nối 2 bảng theo cột `cot` (cùng tên ở cả hai bảng), giống JOIN trong SQL.

    kieu_ghep = "inner": chỉ giữ dòng khớp ở cả hai bảng
                "left" : giữ mọi dòng của bang1, không khớp thì phần bang2 để trống
    - Khóa trống (null) không bao giờ khớp với nhau (như SQL).
    - Cột trùng tên (ngoài `cot`) của bang2 được đổi thành <tên>_2.
    - Trả về DataFrame, giữ nguyên kiểu dữ liệu của bảng gốc.
    """
    if kieu_ghep not in ("inner", "left"):
        raise ValueError("kieu_ghep chỉ nhận 'inner' hoặc 'left'")
    b1, kieu1 = _doc_bang(bang1)
    b2, kieu2 = _doc_bang(bang2)
    if cot not in b1 or cot not in b2:
        raise KeyError(f"Cột {cot!r} phải có ở cả hai bảng")

    # tên cột của bang2 sau khi đổi (tránh đè lên cột của bang1)
    ten_moi = {}
    for c in b2:
        if c != cot:
            ten_moi[c] = c if c not in b1 else c + "_2"

    ket_qua = {c: [] for c in b1}
    ket_qua.update({ten_moi[c]: [] for c in ten_moi})

    # lập chỉ mục bang2 theo khóa: tìm nhanh, không phải duyệt lồng nhau
    chi_muc = {}
    for j, v in enumerate(b2[cot]):
        if not la_null(v):
            chi_muc.setdefault(v, []).append(j)

    for i, v in enumerate(b1[cot]):
        khop = [] if la_null(v) else chi_muc.get(v, [])
        if not khop and kieu_ghep == "left":
            khop = [None]                      # giữ dòng bang1, phần bang2 để trống
        for j in khop:
            for c in b1:
                ket_qua[c].append(b1[c][i])
            for c in ten_moi:
                ket_qua[ten_moi[c]].append(None if j is None else b2[c][j])

    dtype = dict(kieu1)
    dtype.update({ten_moi[c]: k for c, k in kieu2.items() if c in ten_moi})
    return pd.DataFrame({c: pd.Series(gt, dtype=dtype.get(c)) for c, gt in ket_qua.items()})
