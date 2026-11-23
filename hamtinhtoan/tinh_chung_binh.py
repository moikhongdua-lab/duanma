def avg(cot, da_gom, cot_nhom=None):
    ds = da_gom[cot]
    # Truong hop khong phan nhom
    if cot_nhom is None:
        if len(ds) == 0:
            return 0
        tong_gia_tri = 0
        for so in ds:
            tong_gia_tri = tong_gia_tri + so
        return tong_gia_tri / len(ds)
    # Neu cot_nhom la chuoi thi chuyen thanh danh sach
    if type(cot_nhom) == str:
        cot_nhom = [cot_nhom]
    tong_nhom = {}
    dem_nhom = {}
    for i in range(len(ds)):
        khoa = []
        for gia_tri in cot_nhom:
            khoa.append(da_gom[gia_tri][i])
        khoa = tuple(khoa)
        if len(khoa) == 1:
            khoa = khoa[0]
        if khoa not in tong_nhom:
            tong_nhom[khoa] = 0
            dem_nhom[khoa] = 0
        tong_nhom[khoa] = tong_nhom[khoa] + ds[i]
        dem_nhom[khoa] = dem_nhom[khoa] + 1
    ket_qua = {}
    for khoa in tong_nhom:
        ket_qua[khoa] = tong_nhom[khoa] / dem_nhom[khoa]
    return ket_qua