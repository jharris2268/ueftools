#import scipy
import wave
import numpy as np

SAMPLE_RATE = 44100

LOW_SAMPLES = round(44100 / 1200)
HIGH_SAMPLES = round(44100 / 2400)

LOW_TONE = np.int16(28000 * np.sin(np.linspace(0, 2*np.pi, LOW_SAMPLES)[:-1]))
HIGH_TONE = np.int16(28000 * np.sin(np.linspace(0, 2*np.pi, HIGH_SAMPLES)[:-1]))

def write_byte(stream, by):
    write_bit(stream, False)
    write_bit(stream, by & 1)
    write_bit(stream, by & 2)
    write_bit(stream, by & 4)
    write_bit(stream, by & 8)
    write_bit(stream, by & 16)
    write_bit(stream, by & 32)
    write_bit(stream, by & 64)
    write_bit(stream, by & 128)
    write_bit(stream, True)
    

def write_bit(stream, bit):
    if bit:
        stream.writeframes(HIGH_TONE)
        stream.writeframes(HIGH_TONE)
    else:
        stream.writeframes(LOW_TONE)

def write_wave_file(out_filename, uef_chunks):
    
    out_obj = wave.open(out_filename, 'wb')
    out_obj.setframerate(SAMPLE_RATE)
    out_obj.setsampwidth(2)
    out_obj.setnchannels(1)
    
    for type, data in uef_chunks:
        if type == 'silence':
            num_frames = data * SAMPLE_RATE
            out_obj.writeframes([0 for i in range(numframes)])
        elif type == 'carrier':
            for _ in range(data):
                out_obj.writeframes(HIGH_TONE)
        elif type == 'data':
            for by in data:
                write_byte(out_obj,by)
            
    out_obj.close()
            
        
