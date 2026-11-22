def ep_kieu(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Ép DataFrame về đúng kiểu dữ liệu theo SCHEMA."""
    spec = SCHEMA[name]["cols"]
    df = df.reindex(columns=list(spec))          # đúng thứ tự & đủ cột
    for col, kind in spec.items():
        if kind == "int":
            df[col] = pd.to_numeric(df[col]).astype("Int64")
        elif kind == "float":
            df[col] = pd.to_numeric(df[col]).astype("Float64")
        elif kind == "date":
            df[col] = pd.to_datetime(df[col]).dt.normalize()
        elif kind == "time":
            df[col] = df[col].map(_parse_time).astype("string")
        else:
            df[col] = df[col].astype("string")
            limit = VARCHAR_LEN.get((name, col))
            if limit and (df[col].str.len() > limit).any():
                raise ValueError(f"{name}.{col} vượt quá varchar({limit})")
    return df
