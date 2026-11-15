def tong(cot, da_gom, cot_nhom=None):
    if cot_nhom is None:
        ket_qua = 0
        for so in da_gom[cot]:
            ket_qua = ket_qua + so
        return ket_qua
    if type(cot_nhom) == str:
        cot_nhom = [cot_nhom]
    ds = da_gom[cot]
    ket_qua = {}
    for i in range(len(ds)):
        khoa = []
        for gia_tri in cot_nhom:
            khoa.append(da_gom[gia_tri][i])
        khoa = tuple(khoa)
        if len(khoa) == 1:
            khoa = khoa[0]
        if khoa not in ket_qua:
            ket_qua[khoa] = 0
        ket_qua[khoa] = ket_qua[khoa] + ds[i]
    return ket_qua
