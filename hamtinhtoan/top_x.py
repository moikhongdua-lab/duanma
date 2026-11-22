def in_top_luong(ds):
    x = int(input("Nhập số lượng nhân viên lương cao nhất muốn xem: "))
    if x > 0:
        # Sắp xếp danh sách theo lương giảm dần
        ds_sap_xep = sorted(ds.items(), key=lambda nv: nv[1]["luong"], reverse=True)        
        # Lấy x nhân viên đứng đầu
        top_x = ds_sap_xep[:x]
        print("--- TOP", x, "NHÂN VIÊN LƯƠNG CAO NHẤT ---")
        for ma_nv, thong_tin in top_x:
            print("Mã NV:", ma_nv, ", Tên:", thong_tin["ten"], ", Lương:", thong_tin["luong"])
    else:
        print("Số lượng không hợp lệ!")
in_top_luong(ds)
