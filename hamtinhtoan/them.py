
def them(df, dong_moi):
    i = 0
    for ten_cot in df:
        df[ten_cot].append(dong_moi[i])
        i += 1
    return df
print(them(df, ('NV11', 'Khoa', 12, 'Nam')))
