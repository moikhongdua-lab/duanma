def sua(df, cot_khoa, gia_tri_khoa, cot_sua, gia_tri_moi):
    for i in range(len(df[cot_khoa])):
        if df[cot_khoa][i] == gia_tri_khoa:
            df[cot_sua][i] = gia_tri_moi
    return df