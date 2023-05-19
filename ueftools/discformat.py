

#400 or 800 sectors of 256 bytes (100kb / 200kb)

# Sector 0:
# Bytes 0x00 - 0x07: first 8 chars volume name (pad space)
#       0x08 - 0x0e: last file name (7 chars, pad space or null)
#              0x0f: last file directory (1 char)
#       0x10 - 0x17: 2nd last file name ...
#              0x08: 2nd last directory ...
# ...
#       0xf8 - 0xfe: 31st last...
#              0xff: 31st last...

# Sector 1
# Bytes 0x00 - 0x03: last 4 chars volume name (pad space)
#              0x04: cycle number, BCD (bits 0-3 high decimal, 4-7 low decimal) [Increments when catalogue rewritten]
#              0x05: number of files, low five bits [max 31]
#              0x06: bit 4 & 5: boot behaviour
#                          Bit 5 	Bit 4 	Action
#                          0        0 	    No action
#                          0 	    1 	    *LOAD $.!BOOT
#                          1        0 	    *RUN $.!BOOT
#                          1        1 	    *EXEC $.!BOOT
#                    bit 0 & 1: high bits of 10 bit sector number
#              0x07: low 8 bits of sector number


def bcd_to_int(by):
    high = int((by >> 4))
    low = int(by & 15)
    assert 0<=high<=9 and 0<=low<=9
    return high*10 + low
    
def int_to_bcd(val):
    assert 0 <= val <= 99
    high = (val//10)
    low = (val % 10)
    return (high << 4) | low
    

boot_mode_strings = ['NONE','LOAD','RUN','EXEC']

def get_disc_info(sector0, sector1):
    vol_name_head = sector0[:8]
    vol_name_tail = sector1[:4]
    
    vol_name = (vol_name_head + vol_name_tail).rstrip(b' ').decode('ascii')
    
    cycle_num = bcd_to_int(sector1[4])
    num_files = sector1[5] // 8
    
           
    
    boot_mode = (sector1[6] & 0b00110000) >> 4
    
    sector_count = (sector1[6] & 0b00000011) << 8 | sector1[7]
    
    return (vol_name, cycle_num, num_files, boot_mode, sector_count)    
    
def get_file_info(sector0, sector1, idx):
    part0 = sector0[8 + 8*idx:16 + 8*idx]
    part1 = sector1[8 + 8*idx:16 + 8*idx]
    
    file_name = part0[0:7].rstrip(b' ').decode('ascii')
    directory = chr(part0[7] & 0x7f)
    locked = bool(part0[7]&0x80)
    
    load_addr = part1[0] | (part1[1] << 8) | ( ((part1[6]&0b00001100) << 14) )
    exec_addr = part1[2] | (part1[3] << 8) | ( ((part1[6]&0b11000000) << 10) )
    file_len  = part1[4] | (part1[5] << 8) | ( ((part1[6]&0b00110000) << 12) )
    
    start_sec = part1[7] | ( ((part1[6]&0b00000011) << 8) )
    
    return (file_name, directory, locked, load_addr, exec_addr, file_len, start_sec)
    
    

class File:
    def __init__(self):
        self.index = 0
        
        self.file_name = b''
        self.directory = b''
        self.locked = False
        self.load_addr = 0
        self.exec_addr = 0
        self.file_length = 0
        self.start_sector = 0
        
        self.last_sector = 0
        self.data = b''

    def __repr__(self):
        return "[%2d] % 7s %s [%s] %05x %05x %05X %03x (%d bytes)" % (\
            self.index, self.file_name, self.directory,
            'L' if self.locked else ' ', self.load_addr, self.exec_addr,
            self.file_length, self.start_sector, len(self.data))

    @classmethod
    def from_sectors(cls, idx, sectors):
        file = cls()
        file.index = idx
        
        file.file_name, file.directory,\
            file.locked, file.load_addr,\
            file.exec_addr, file.file_length,\
            file.start_sector = get_file_info(sectors[0], sectors[1], idx)
        
        
         
        file.last_sector = file.start_sector + file.file_length//256 + (1 if (file.file_length % 256)!=0 else 0)
        file.data = b''.join(sectors[file.start_sector:file.last_sector])[:file.file_length]
        
        return file
    
    def pack_sector_zero_part(self):
        result = list(("%-7.7s" % (self.file_name,)).encode('ascii'))
        result.append(ord(self.directory) | (0x80 if self.locked else 0))
        assert len(result) == 8
        return result
    
    def pack_sector_one_part(self):
        result = [0, 0, 0, 0, 0, 0, 0, 0]
        
        result[0] = self.load_addr & 0xff
        result[1] = (self.load_addr & 0xff00) >> 8
        result[6] |= (self.load_addr & 0xff0000) >> 14 #bits 2 and 3
        
        result[2] = self.exec_addr & 0xff
        result[3] = (self.exec_addr & 0xff00) >> 8
        result[6] |= (self.exec_addr & 0xff0000) >> 10 #bits 6 and 7
        
        result[4] = self.file_length & 0xff
        result[5] = (self.file_length & 0xff00) >> 8
        result[6] |= (self.file_length & 0xff0000) >> 12 #bits 4 and 5
        
        result[7] = self.start_sector & 0xff
        result[6] |= (self.start_sector & 0xff00) >> 8 #bits 0 and 1
        
        return result
    
    def set_data_sectors(self, sectors):
        assert len(self.data) == self.file_length
        
        num_sectors = self.last_sector-self.start_sector
        assert num_sectors == len(self.data)//256+ (1 if (len(self.data) % 256)!=0 else 0)
        
        for i in range(num_sectors):
            sectors[self.start_sector + i] = self.data[256*i : 256*i + 256]
        
    
def pad_sector(data):
    if data is None:
        return bytes(256)
    if len(data)>256:
        raise Exception("too long!")
    return data + bytes(256-len(data))

class Disc:
    def __init__(self):
        self.volume_name = b''
        self.cycle_number = 0
        self.num_files = 0
        self.boot_mode = 0
        self.sector_count = 400
        
        self.last_sector = 0
        self.changed = False
        self.files = []

    def __repr__(self):
        return "Disc [% 12s], {cycle: %02d}, %2d files, %s %3d sectors" % (\
            self.volume_name, self.cycle_number, self.num_files,
            boot_mode_strings[self.boot_mode], self.sector_count)

    @classmethod
    def from_bytes(cls, data):
        
        sectors = [data[i:i+256] for i in range(0, len(data), 256)]
        
        disc = cls()
        
        disc.volume_name, disc.cycle_number,\
            disc.num_files, disc.boot_mode,\
            disc.sector_count = get_disc_info(sectors[0], sectors[1])
        
        for i in range(disc.num_files):
            ff = File.from_sectors(i, sectors)
            disc.files.append(ff)
        
        disc.last_sector = 2 if not disc.files else max(f.last_sector for f in disc.files)
        return disc
            
    def add_file(self, file_name, data, directory=None, load_addr=None, exec_addr=None):
        assert len(self.files) < 31
        
        file = File()
        
        directory = directory or '$'
        try:
            load_addr = load_addr or self.files[0].load_addr
            exec_addr = exec_addr or self.files[0].exec_addr
        except:
            raise Exception("can't set default load_addr / exec_addr")
        
        file.index=0
        file.file_name = file_name
        file.directory = directory
        file.locked=False
        file.load_addr = load_addr
        file.exec_addr = exec_addr
        file.file_length = len(data)
        file.start_sector = self.last_sector
        self.last_sector = file.start_sector + len(data)//256 + 1
        file.last_sector = self.last_sector
        file.data = data
        
        
        self.changed = True
        
        for f in self.files:
            f.index += 1
        self.files.insert(0, file)
    
    
    def pack_sector_zero(self):
        result = list(("%-8.8s" % (self.volume_name,)).encode('ascii'))
        assert len(result)==8
        for f in self.files:
            
            result.extend(f.pack_sector_zero_part())
            
            
        assert len(result)==8 + 8*len(self.files)
        
        return bytes(result)
        
    def pack_sector_one(self):
        result = list(("%-4.4s" % (self.volume_name[8:12],)).encode('ascii'))
        
        result.append(int_to_bcd(self.cycle_number))
        result.append(len(self.files)*8)
        
        #             bits 5 and 6                     bits 0 and 1
        byte6 = ((self.boot_mode&3) << 4) | ( (self.sector_count & 1023) >> 8 )
        result.append(byte6)
        result.append(self.sector_count & 255)
        assert len(result)==8
        
        for f in self.files:
            result.extend(f.pack_sector_one_part())
            
        assert len(result)==8 + 8*len(self.files)
        
        return bytes(result)
        
        
    def pack_all(self):
        
        if self.changed:
            self.cycle_number = (self.cycle_number + 1) % 100
            self.changed=False
            
        
        sectors = [None for i in range(self.sector_count)]
        
        sectors[0] = self.pack_sector_zero()
        sectors[1] = self.pack_sector_one()
        
        for f in self.files:
            f.set_data_sectors(sectors)
                    
        last_used = max(i for i in range(len(sectors)) if not sectors[i] is None)
        return b''.join(pad_sector(s) for s in sectors[:last_used+1])
        
def get_data(fileobj):
    if isinstance(fileobj, str):
        fileobj = open(fileobj, 'rb')
    
    return fileobj if isinstance(fileobj, bytes) else fileobj.read()

def read_disc_single(fileobj):
    data = get_data(fileobj)   
    return Disc.from_bytes(data)
    
def read_disc_double(fileobj):
    data = get_data(fileobj)   
    
    track_len = 10*256
    side0 = b''.join(data[x:x+track_len] for x in range(0, len(data), 2*track_len))
    side1 = b''.join(data[x:x+track_len] for x in range(track_len, len(data), 2*track_len))
    
    return Disc.from_bytes(side0), Disc.from_bytes(side1)
    
    
        
