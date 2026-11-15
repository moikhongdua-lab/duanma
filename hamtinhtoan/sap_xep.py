def quick_sort(ds, thu_tu, cot_so=None):
    if len(ds) <= 1:
        return ds
    if thu_tu != 'tangdan' and thu_tu != 'giamdan':
        raise ValueError("thu_tu phải là 'tangdan' hoặc 'giamdan'")
    moc = ds[len(ds) // 2]
    if cot_so is not None:
        moc = moc[cot_so]            
    nhohon = []
    bang = []
    lonhon = []
    for x in ds:
        v = x
        if cot_so is not None:
            v = x[cot_so]
        if v < moc:              
            nhohon.append(x)
        elif v == moc:
            bang.append(x)
        else:
            lonhon.append(x)
    if thu_tu == 'tangdan':
        return quick_sort(nhohon, thu_tu, cot_so) + bang + quick_sort(lonhon, thu_tu, cot_so)
    else:
        return quick_sort(lonhon, thu_tu, cot_so) + bang + quick_sort(nhohon, thu_tu, cot_so)
