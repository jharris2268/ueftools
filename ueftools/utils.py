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


from subprocess import Popen, PIPE

def call_basictool(data, format_option=False):
    cmd = ['/home/james/bbcmicro/basictool/basictool', '-2']
    if format_option:
        cmd.append('-f')
    cmd.append('-')
    p = Popen(cmd, stdin = PIPE, stdout=PIPE, stderr = PIPE)
    
    res, err = p.communicate(input=data)
    
    if err:
        raise Exception(err.decode('ascii'))
        
    return res.decode('ascii')
    
    
    
