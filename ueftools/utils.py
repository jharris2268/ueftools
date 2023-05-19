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

def call_basictool(data, *opts):
    cmd = ['/home/james/bbcmicro/basictool/basictool', '-2']
    cmd.extend(opts)
    cmd.append('-')
    p = Popen(cmd, stdin = PIPE, stdout=PIPE, stderr = PIPE)
    
    res, err = p.communicate(input=data)
    
    if err:
        raise Exception(err.decode('ascii'))
        
    return res
    

import re
linenum_cmd = re.compile("^\s*(\d+)\s*(.*)$")
    
def remove_linenumbers(basic_text, incr = 10):
    result = {}
    for l in basic_text.split("\n"):
        if not l.strip():
            continue #ignore blank lines
        p = linenum_cmd.match(l)
        if not p:
            raise Exception("line %s not matching '<LINENUM> <TEXT>'" % l)
        
        lineno_s, txt = p.groups()
        lineno = int(lineno_s)
        if (lineno % incr) != 0:
            raise Exception("lineno %d doesn't match increment %d [%s]" % (lineno, incr, l))
        
        result[lineno//incr] = txt
        
    return result
    
def add_linenumbers(basic_text, incr=10):
    result = []
    max_line_num = basic_text.count("\n") * incr
    num_chars = len(str(max_line_num))
    
    line_number_format = "%% %dd %%s" % num_chars
    
    for i,l in enumerate(basic_text.split("\n")):
        result.append(line_number_format % ((i+1)*incr, l))
    
    return "\n".join(result)

