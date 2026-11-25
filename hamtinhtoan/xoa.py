def xoa(df):
    print("1. Xóa một dòng (theo Mã NV)")
    print("2. Xóa một cột (theo tên cột)")
    print("3. Xóa một ô (làm rỗng ô)")
    chon = input("Chọn kiểu xóa (1, 2 hoặc 3): ").strip()

    if chon == "1":
        ma_xoa = input("Nhập mã nhân viên cần xóa: ").strip().upper()
        if ma_xoa in df["ma_nv"].values:
            df = df[df["ma_nv"] != ma_xoa]
            print("Đã xóa dòng có mã:", ma_xoa)
        else:
            print("Không tìm thấy mã:", ma_xoa)

    elif chon == "2":
        ten_cot = input("Nhập tên cột cần xóa: ").strip()
        if ten_cot in df.columns:
            df = df.drop(columns=[ten_cot])
            print("Đã xóa cột:", ten_cot)
        else:
            print("Không tìm thấy cột:", ten_cot)

    elif chon == "3":
        ma_nv = input("Nhập mã nhân viên: ").strip().upper()
        ten_cot = input("Nhập tên cột cần xóa dữ liệu: ").strip()
        if ma_nv in df["ma_nv"].values and ten_cot in df.columns:
            df.loc[df["ma_nv"] == ma_nv, ten_cot] = None
            print("Đã xóa dữ liệu tại ô:", ma_nv, "-", ten_cot)
        else:
            print("Không tìm thấy mã nhân viên hoặc tên cột!")

    else:
        print("Lựa chọn không hợp lệ!")

    return df
