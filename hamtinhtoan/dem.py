def dem(cot_nhom, da_gom, cot_dem):
    tong = {}
    for muc_luong in da_gom[cot_nhom]:
        for gioi_tinh in da_gom[cot_dem][muc_luong]:
            if gioi_tinh not in tong:
                tong[gioi_tinh] = 0
            tong[gioi_tinh] += 1
    return tong

