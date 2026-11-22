
def loc_o(df, cot, dieu_kien):
    ket_qua = {}
    for ten_cot in df:
        ket_qua[ten_cot] = []
    phep_toan, gia_tri = dieu_kien.split()
    gia_tri = int(gia_tri)
    for i in range(len(df[cot])):
        if phep_toan == '>':
            if df[cot][i] > gia_tri:
                for ten_cot in df:
                    ket_qua[ten_cot].append(df[ten_cot][i])
    return ket_qua
print(loc_o(df, 'luong', '> 15'))
