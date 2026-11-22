def dem(cot_nhom, da_gom, cot_dem):
    tong = {}
    for khoa in da_gom[cot_nhom]:
        for gt in da_gom[cot_dem][khoa]:
            if gt not in tong:
                tong[gt] = 0
            tong[gt] += 1
    return tong
print(dem('luong', da_gom, 'gioitinh'))
