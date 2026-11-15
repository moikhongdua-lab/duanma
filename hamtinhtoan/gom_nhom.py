def gom_nhom(df, cot):
    if type(cot) == str:
        cot = [cot]
    for c in cot:
        if c not in df:
            raise KeyError("Không tìm thấy cột: " + str(c))
    nhom = {}
    for dong in range(len(df[cot[0]])):
        ds = []
        for ten_cot in cot:
            ds.append(df[ten_cot][dong])
        khoa = tuple(ds)
        if khoa not in nhom:
            nhom[khoa] = []
        nhom[khoa].append(dong)
    thu_tu_moi = []
    for khoa in nhom:
        for i in nhom[khoa]:
            thu_tu_moi.append(i)
    ket_qua = {}
    for tencot in df:
        cot_moi = []
        for i in thu_tu_moi:
            cot_moi.append(df[tencot][i])
        ket_qua[tencot] = cot_moi
    return ket_qua        
