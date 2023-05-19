from .uef import read_uef_file, WriteUef

from .readwave import read_wave_file
from .writewave import write_wave_file

from .datablock import DataBlock, extract_programs, encode_programs

from .utils import call_basictool, remove_linenumbers, add_linenumbers
from .discformat import Disc, read_disc_single, read_disc_double

import sys, os


def wave_to_uef():
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    
    chunks = list(read_wave_file(infilename, 2.0, 2.0))
    
    writer = WriteUef(open(outfilename, 'wb'))
    for a,b in chunks:
        writer(a,b)
    return 0

def uef_to_wave():
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    
    instream = open(infilename, 'rb')
    chunks = list(read_uef_file(instream))
    
    write_wave_file(outfilename, chunks)
    return 0
    
def uef_to_basic():
    infilename = sys.argv[1]
    outlocation = None
    if len(sys.argv)>2:
        outlocation = sys.argv[2]
    
    instream = open(infilename, 'rb')
    chunks = list(read_uef_file(instream))
    
    progs = extract_programs(chunks)
    
    for name, prog, _ in progs:
        prog_text = call_basictool(prog).decode('ascii')
        if prog_text.startswith('Bad Pro'):
            print("%s not basic?? [%s]" % (name, repr(prog[:50])))
        else:
            if outlocation is None:
                print("%s:\n%s" % (name.decode('ascii'), prog_text))
            else:
                open(os.path.join(outlocation, "%s.bas" % (name.decode('ascii'),)),'w').write(prog_text)
    return 0

def basic_to_uef():
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    
    if not infilename.endswith('.bas'):
        raise Exception("expected infilename to have '.bas' extension")
    
    prog_name = os.path.split(infilename)[1][:-4].upper().encode('ascii')
    
    in_text = open(infilename, 'r').read().encode('ascii')
    binary = call_basictool(in_text, '-t')
    
    chunks = encode_programs([(prog_name, binary)])
    
    writer = WriteUef(open(outfilename, 'wb'))
    for a,b in chunks:
        writer(a,b)
    return 0

def call_remove_linenumbers():
    infilename = sys.argv[1]
    outfilename = None
    if len(sys.argv)>2:
        outfilename = sys.argv[2]
    
    if outfilename and os.path.exists(outfilename):
        raise Exception("%s exists" % (outfilename,))
    
    intext = open(infilename, 'r').read()
    
    lines = remove_linenumbers(intext)
    lines_joined = "\n".join(lines.get(i) or '' for i in range(min(lines),max(lines)+1))
    if outfilename is None:
        print(lines_joined)
    else:
        open(outfilename,'w').write(lines_joined)

def call_add_linenumbers():
    infilename = sys.argv[1]
    outfilename = None
    if len(sys.argv)>2:
        outfilename = sys.argv[2]
    
    if outfilename and os.path.exists(outfilename):
        raise Exception("%s exists" % (outfilename,))
    
    intext = open(infilename, 'r').read()
    
    result = add_linenumbers(intext)
    
    if outfilename is None:
        print(result)
    else:
        open(outfilename,'w').write(result)
    
    
