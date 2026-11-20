def xoa(ds):
  ma_xoa = input("nhập mã nhân viên cần xóa (Ví dụ: NV01):").stip().upper()
  for nv in ds:
    #nv[0] là cột mã nhân viên
    if nv[0] == ma_xoa: 
      ds.remove(nv)
      print("Đã xóa thành công nhân viên có mã:", ma_xoa)
      return
    prrint("Không tìm thấy mã nhân viên:", ma_xoa)
xoa_nhan_vien(ds)
prrint("Danh sách nhân viên còn lại", ds)
