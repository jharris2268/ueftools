from struct import pack, unpack
from .utils import crc
from io import BytesIO


def read_null_terminated_string(stream):
    result = []
    by = stream.read(1)
    while by != b'\0':
        if len(by)!=1:
            raise Exception('null char not found..')
        result.append(by)
        by = stream.read(1)
    
    return b''.join(result)

class DataBlock:
    def __init__(self, name, load_addr, exec_addr, block_nr, is_last, data):
        self.name = name
        self.load_addr = load_addr
        self.exec_addr = exec_addr
        self.block_nr = block_nr
        self.is_last = is_last
        
        self.data = data
        
    
    def pack(self, stream):
        header = name  + '\0' +\
                    pack('<IIHHBI',   self.load_addr, self.exec_addr,
                                        self.block_nr, len(self.data),
                                        0x80 if self.is_last else 0,
                                        0)
        header_crc = crc(header)
        data_crc = crc_(data)
        
        stream.write(b'*')
        stream.write(header)
        stream.write(pack('>H', header_crc))
        stream.write(data)
        stream.write(pack('>H', data_crc))
    
    
    def __repr__(self):
        res = "%s (%d%s)" % (self.name, self.block_nr, ' L' if self.is_last else '')
        if self.data is None:
            return "%s EMPTY" % res
        else:
            return "%s %d bytes" % (res, len(self.data))
    
    @classmethod
    def from_bytes(cls, data):
        if len(data)<21:
            return None
        
        stream = BytesIO(data)
    
        #first byte '*'
        assert stream.read(1)==b'*'
    
        name = read_null_terminated_string(stream)
    
        remaining_header = stream.read(17)
        if not len(remaining_header)==17:
            raise Exception('not enough bytes')
        load_addr,exec_addr,block_nr,data_len,block_flag,c = unpack('<IIHHBI', remaining_header)
        if block_flag not in (0,0x80):
            raise Exception("unexpected block flag %s" % (hex(block_flag),))
        is_last = block_flag == 0x80
        if c!=0:
            raise Exception("unexpected header trailing 4 bytes")
        
        header_crc, = unpack('>H', stream.read(2))
        header = name + b'\0' + remaining_header
        calc_header_crc = crc(header)
        if not header_crc == calc_header_crc:
            print('header crc failed...', header_crc, calc_header_crc, header)
            #raise Exception('header crc check failed')
        
        if data_len == 0:
            return cls(name, load_addr, exec_addr, block_nr, is_last, None)
            
            
        data=stream.read(data_len)
        if not len(data) == data_len:
            raise Exception('not enough bytes')
        
        data_crc, = unpack('>H', stream.read(2))
        if not data_crc == crc(data):
            print('data crc failed', data_crc, crc(data))
            #raise Exception('data crc check failed')
            
            
        if stream.read()!= b'':
            raise Exception("trailing bytes...")
        
        return cls(name, load_addr, exec_addr, block_nr, is_last, data)

def extract_programs(chunks):
    programs = []
    
    for (type, data) in chunks:
        if type == 'data' and len(data)>=21:
            block = DataBlock.from_bytes(data)
            print(block)
            
            if not programs or programs[-1][0] != block.name:
                programs.append([block.name,b'',[]])
                
            if not block.data is None:
                programs[-1][1] += block.data
            programs[-1][2].append(block)
        
    return programs
    
    
