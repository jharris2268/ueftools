
from struct import pack, unpack

def read_uef_file(stream):
    header = stream.read(12)
    if not len(header)==12:
        raise Exception("stream not long enough")
    if header[:10] !=  b'UEF File!\x00':
        raise Exception("stream doesn't start with correct header")
    
    vers, = unpack('<H', header[10:12])
    
    while True:
        header = stream.read(6)
        if len(header)==0:
            return
        if len(header)!=6:
            raise Exception("not enough bytes read for header...")
            
        identifier, length = unpack('<HI', header)
        
        data = stream.read(length)
        if len(data)!= length:
            raise Exception("not enough bytes read for data...")
            
        if identifier == 0x100:
            yield ('data', data)
            
        elif identifier == 0x110:
            if len(data)!=2:
                raise Exception("expected carrier tone data to be a 16bit int...")
            
            num_cycles,=unpack('<H', data)
            yield ('carrier', num_cycles)
        elif identifier == 0x114:
            if len(data)!=2:
                raise Exception("expected integer silence data to be a 16bit int...")
            
            num_cycles,=unpack('<H', data)
            yield ('silence', num_cycles * 44100/2400)
        
        elif identifier == 0x116:
            if len(data)!=4:
                raise Exception("expected float silence data to be a 32bit float...")
            
            secs,=unpack('<f', data)
            yield ('silence', secs)
        else:
            print("ignoring %H [%d bytes %s]" % (identifier, length, data))


class WriteUef:
    def __init__(self, stream):
        self.stream = stream
        self.stream.write(b'UEF File!\x00')  # Magic value.
        self.stream.write(b'\x01\x00') 
        
    def write_silence(self, seconds):
        self.stream.write(pack('<HIf', 0x116, 4, seconds))
    
    def write_carrier(self, cycles):
        self.stream.write(pack('<HIH', 0x110, 2, cycles))
        
    def write_data(self, data):
        self.stream.write(pack('<HI', 0x100, len(data)))
        self.stream.write(data)
        
    def __call__(self, what,data):
        if what == 'silence':
            self.write_silence(data)
        elif what == 'carrier':
            self.write_carrier(data)
        elif what == 'data':
            self.write_data(data)
        else:
            raise Exception("unexpected %s [%s]" % (what, data))
    
