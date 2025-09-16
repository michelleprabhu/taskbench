def read_md_or_txt_bytes(b: bytes) -> str:
    return b.decode("utf-8", errors="ignore")
