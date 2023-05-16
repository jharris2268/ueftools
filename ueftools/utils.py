def crc(bytes):
    crc = 0
    for c in bytes:
        crc = ((c ^ (crc >> 8)) << 8) | (crc & 0x00FF)
        for _ in range(8):
            if crc & 0x8000:
                crc = crc ^ 0x0810
                t = 1
            else:
                t = 0
            crc = (crc * 2 + t) & 0xFFFF
    return crc
