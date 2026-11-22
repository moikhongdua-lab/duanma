
def dem(cot_nhom, da_gom, cot_dem):
    ket_qua = {}
    for khoa in da_gom[cot_nhom]:
        if khoa not in ket_qua:
            ket_qua[khoa] = {}
        for gt in da_gom[cot_dem][khoa]:
            if gt not in ket_qua[khoa]:
                ket_qua[khoa][gt] = 0
            ket_qua[khoa][gt] += 1
    tong = {}
    for khoa in ket_qua:
        for gt in ket_qua[khoa]:
            if gt not in tong:
                tong[gt] = 0
            tong[gt] += ket_qua[khoa][gt]
    return tong
print(dem('luong', da_gom, 'gioitinh'))
