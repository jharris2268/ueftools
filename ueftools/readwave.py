import scipy
import numpy as np

kk = {(-1, -1): 'A', (-1, 1): 'B', (1, 1): 'C', (1, -1): 'D'}

def calc_moving_average(arr, n=3):
    ret=np.cumsum(arr)
    return (ret[n:]-ret[:-n])/n
    


def read_wave_file(filename, ignore_first=None, ignore_last=None):
    samplerate, arr = scipy.io.wavfile.read(filename)
    if len(arr.shape)>1:
        arr=arr[:,0]
    if ignore_first is not None or ignore_last is not None:
        ii = int(samplerate * (ignore_first or 0))
        jj = int(samplerate * (ignore_last or 0))
        arr = arr[ii:-jj]
        
    if samplerate != 44100:
        raise Exception("sample rate must be 44100")
    
    
    signs_dirs_iter = iter_signs_dirs(arr)
    
    parts = find_cycle_parts(signs_dirs_iter)
    
    cycles = merge_cycle_parts(parts)
    
    for chunk in to_bytes(cycles):
        yield chunk
    
    
def iter_signs_dirs(arr, n=3):
    
    moving_avg = calc_moving_average(arr,n) if n else arr
    
    nsamp = moving_avg.shape[0]
    signs = np.sign(moving_avg)
    dirs = np.sign(np.gradient(moving_avg))
    
    return zip(range(nsamp), signs, dirs)
    
def find_cycle_parts(signs_dirs_iter):
        
    
    #reps = []
    
    ii, curr = 0, None
    
    for i, a, b in signs_dirs_iter:
        if a==0 or b==0 or kk[a,b] == curr:
            continue
        
        else:
            if not curr is None:
                
                yield (ii, i, i-ii, curr)
            ii = i
            curr = kk[a,b]
    
    yield (ii, i, i-ii, curr)
    


def merge_cycle_parts(itr):
    idx = 0 
    while True:
        try:
            A = next(itr)
            while A[3] != 'A':
                print('skip', A)
                A = next(itr)
            B = next(itr)
            while B[3] != 'B':
                print('skip', B)
                B = next(itr)
            C = next(itr)
            while C[3] != 'C':
                print('skip', C)
                C = next(itr)
            D = next(itr)
            while D[3] != 'D':
                print('skip', D)
                D = next(itr)
            
            
            ln = D[1]-A[0]
            
            if ln > 200:
                print('silence?', A[0],D[1], ln)
                yield (idx, 'S', A[0],D[1])
            
            elif ln < 14:
                print('too short??', A[0],D[1], ln)
                raise Exception("??")
                
            elif ln < 22:
                yield (idx, 'H',A[0],D[1])
            elif ln < 34:
                print('in between??', A[0],D[1], ln)
                raise Exception("??")
            elif ln < 39:
                yield (idx, 'L',A[0],D[1])
            else:
                print('too long??', A[0],D[1], ln)
                raise Exception("??")
            
            idx += 1
        except StopIteration:
            break
    
    

def find_low(cycles):
    count=0
    while True:
        try:
            count += 1
            item = next(cycles)
            if item[1] != 'H':
                return item, count
        except StopIteration:
            return None, count
    

def read_byte(cycles, first):
    if first[1] != 'L':
        raise Exception("uexpected high bit at %d [%s]" % (idx, parts[idx]))
    #idx += 1
    ans = 0
    for i in (1,2,4,8,16,32,64,128):
        curr_item = next(cycles)
        if curr_item[1] == 'L':
            pass
        elif curr_item[1] == 'H':
            next_item = next(cycles)
            if next_item[1] == 'H':
                ans += i #set bit
                
            else:
                raise Exception("single high bit at %s // %s" % (curr_item, next_item))
    
    first_stop = next(cycles)
    second_stop = next(cycles)
    if first_stop[1] != 'H' or second_stop[1] != 'H':
        raise Exception("wrong stop bit [%s %s]" % (first_stop,second_stop))
    
    return ans

def to_bytes(cycles):
    idx,key,start,end = next(cycles)
    while True:
        try:
            
            if key == 'L':
                data = []
                while key == 'L':
                    by = read_byte(cycles, (idx, key,start,end))
                    data.append(by)
                    idx,key,start,end = next(cycles)
                     
                yield ('data', bytes(data))
            elif key == 'H':
                item,count = find_low(cycles)
                yield ('carrier', count)
                if item is None:
                    return
                else:
                    (idx,key,start,end) = item
                
            
            elif key == 'S':
                
                yield ('silence', (end-start)/44100.0 )
                (idx,key,start,end) = next(cycles)
            
            else:
                raise Exception("?? %d [%s %d %d]" % (idx, key, start, end))
        except StopIteration:
            return
        
