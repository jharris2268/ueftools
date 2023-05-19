#original function from https://github.com/shawty/BBCB_DFS_Catalog/blob/master/dfscat.js
"""
function d_basic(catalogIndex)
{
  var fileItem = catalog[catalogIndex];
  var fileData = getFileData(catalogIndex);
  /* Thanks to https://www.sweharris.org for letting me convert the code in
  *  list.pl part of his MMB_Utils https://github.com/sweharris/MMB_Utils
  *  to javascript and relicense it for use in this code.
  */

  var c = new String;
  var d = new String;
  var e = new String;
  var line = 0;
  var llen = 0;
  var raw = 0;
  var decode = new String;
  var prevchar = new String;
  var listing = new String;
  var lend = 0;
  var lno;
  var n1=0;
  var n2=0;
  var n3=0;
  var low=0;
  var high=0;
  var tokens = new Array();
  var ret=true;
  tokens[128] = 'AND';     tokens[192] = 'LEFT$(';
  tokens[129] = 'DIV';     tokens[193] = 'MID$(';
  tokens[130] = 'EOR';     tokens[194] = 'RIGHT$(';
  tokens[131] = 'MOD';     tokens[195] = 'STR$';
  tokens[132] = 'OR';      tokens[196] = 'STRING$(';
  tokens[133] = 'ERROR';   tokens[197] = 'EOF';
  tokens[134] = 'LINE';    tokens[198] = 'AUTO';
  tokens[135] = 'OFF';     tokens[199] = 'DELETE';
  tokens[136] = 'STEP';    tokens[200] = 'LOAD';
  tokens[137] = 'SPC';     tokens[201] = 'LIST';
  tokens[138] = 'TAB(';    tokens[202] = 'NEW';
  tokens[139] = 'ELSE';    tokens[203] = 'OLD';
  tokens[140] = 'THEN';    tokens[204] = 'RENUMBER';
  tokens[142] = 'OPENIN';  tokens[205] = 'SAVE';
  tokens[143] = 'PTR';     tokens[207] = 'PTR';
  tokens[144] = 'PAGE';    tokens[208] = 'PAGE';
  tokens[145] = 'TIME';    tokens[209] = 'TIME';
  tokens[146] = 'LOMEM';   tokens[210] = 'LOMEM';
  tokens[147] = 'HIMEM';   tokens[211] = 'HIMEM';
  tokens[148] = 'ABS';     tokens[212] = 'SOUND';
  tokens[149] = 'ACS';     tokens[213] = 'BPUT';
  tokens[150] = 'ADVAL';   tokens[214] = 'CALL';
  tokens[151] = 'ASC';     tokens[215] = 'CHAIN';
  tokens[152] = 'ASN';     tokens[216] = 'CLEAR';
  tokens[153] = 'ATN';     tokens[217] = 'CLOSE';
  tokens[154] = 'BGET';    tokens[218] = 'CLG';
  tokens[155] = 'COS';     tokens[219] = 'CLS';
  tokens[156] = 'COUNT';   tokens[220] = 'DATA';
  tokens[157] = 'DEG';     tokens[221] = 'DEF';
  tokens[158] = 'ERL';     tokens[222] = 'DIM';
  tokens[159] = 'ERR';     tokens[223] = 'DRAW';
  tokens[160] = 'EVAL';    tokens[224] = 'END';
  tokens[161] = 'EXP';     tokens[225] = 'ENDPROC';
  tokens[162] = 'EXT';     tokens[226] = 'ENVELOPE';
  tokens[163] = 'FALSE';   tokens[227] = 'FOR';
  tokens[164] = 'FN';      tokens[228] = 'GOSUB';
  tokens[165] = 'GET';     tokens[229] = 'GOTO';
  tokens[166] = 'INKEY';   tokens[230] = 'GCOL';
  tokens[167] = 'INSTR(';  tokens[231] = 'IF';
  tokens[168] = 'INT';     tokens[232] = 'INPUT';
  tokens[169] = 'LEN';     tokens[233] = 'LET';
  tokens[170] = 'LN';      tokens[234] = 'LOCAL';
  tokens[171] = 'LOG';     tokens[235] = 'MODE';
  tokens[172] = 'NOT';     tokens[236] = 'MOVE';
  tokens[173] = 'OPENUP';  tokens[237] = 'NEXT';
  tokens[174] = 'OPENOUT'; tokens[238] = 'ON';
  tokens[175] = 'PI';      tokens[239] = 'VDU';
  tokens[176] = 'POINT(';  tokens[240] = 'PLOT';
  tokens[177] = 'POS';     tokens[241] = 'PRINT';
  tokens[178] = 'RAD';     tokens[242] = 'PROC';
  tokens[179] = 'RND';     tokens[243] = 'READ';
  tokens[180] = 'SGN';     tokens[244] = 'REM';
  tokens[181] = 'SIN';     tokens[245] = 'REPEAT';
  tokens[182] = 'SQR';     tokens[246] = 'REPORT';
  tokens[183] = 'TAN';     tokens[247] = 'RESTORE';
  tokens[184] = 'TO';      tokens[248] = 'RETURN';
  tokens[185] = 'TRUE';    tokens[249] = 'RUN';
  tokens[186] = 'USR';     tokens[250] = 'STOP';
  tokens[187] = 'VAL';     tokens[251] = 'COLOUR';
  tokens[188] = 'VPOS';    tokens[252] = 'TRACE';
  tokens[189] = 'CHR$';    tokens[253] = 'UNTIL';
  tokens[190] = 'GET$';    tokens[254] = 'WIDTH';
  tokens[191] = 'INKEY$';  tokens[255] = 'OSCLI';


  var i = 0;
  while ( i < fileItem.fileLength ) {
    if ( fileData[i] != 13 ) {
      listing+="Bad Program (expected ^M at start of line).";
      ret=false;
      break;
    }
    i++;
    // Line number high
    if ( fileData[i] == 255 ) {
      break;
    }
    if ( fileItem.fileLength < i+2 ) {
      listing+="Bad Program (Line finishes before metadata).";
      ret=false;
      break;
    }
    line = fileData[i]*256;
    i++;
    // Line number low
    line = line + fileData[i];
    i++;
    // Line length
    llen = fileData[i]-4;
    if ( llen < 0 ) {
      listing+="Bad Program (Line length too short)";
      ret=false;
      break;
    }
    raw=0;  // Set to 1 if in quotes
    decode="";
    prevchar="";
    lend=i+llen;
    if (lend > fileItem.fileLength ) {
      listing+="Bad Program (Line truncated)";
      ret=false;
      break;
    }
    // Read rest of line
    while ( i++ < lend ) {
      if (raw == 1) {
        d = String.fromCharCode(fileData[i]);
      } else {
        if (fileData[i] == parseInt("8D",16)) {
          // Line token
          i++;
          n1=fileData[i];
          i++;
          n2=fileData[i];
          i++;
          n3=fileData[i];
          // This comes from page 41 of "The BASIC ROM User Guide"
          n1=(n1*4)&255;
          low=(n1 & 192) ^ n2;
          n1=(n1*4)&255;
          high=n1 ^ n3;
          lno=high*256+low;
          d=lno;
        } else {
          if ( fileData[i] in tokens ) {
            d=tokens[fileData[i]];
          } else {
            d=String.fromCharCode(fileData[i]);
          }
        }
      }
      if (String.fromCharCode(fileData[i]) == '"' ) { raw=1-raw; }
      if ( d == '<' ) {
        decode += "&lt;";
      } else {
        decode += d;
      }
    }
    listing+=String("     "+line).slice(-6)+decode+"\n";
  }
  $('#contentsbas').html(listing);
  return ret;
}
"""

tokens = {
128: 'AND',129: 'DIV',130: 'EOR',131: 'MOD',132: 'OR',133: 'ERROR',134: 'LINE',135: 'OFF',
136: 'STEP',137: 'SPC',138: 'TAB(',139: 'ELSE',140: 'THEN',142: 'OPENIN',143: 'PTR',
144: 'PAGE',145: 'TIME',146: 'LOMEM',147: 'HIMEM',148: 'ABS',149: 'ACS',150: 'ADVAL',151: 'ASC',
152: 'ASN',153: 'ATN',154: 'BGET',155: 'COS',156: 'COUNT',157: 'DEG',158: 'ERL',159: 'ERR',
160: 'EVAL',161: 'EXP',162: 'EXT',163: 'FALSE',164: 'FN',165: 'GET',166: 'INKEY',167: 'INSTR(',
168: 'INT',169: 'LEN',170: 'LN',171: 'LOG',172: 'NOT',173: 'OPENUP',174: 'OPENOUT',175: 'PI',
176: 'POINT(',177: 'POS',178: 'RAD',179: 'RND',180: 'SGN',181: 'SIN',182: 'SQR',183: 'TAN',
184: 'TO',185: 'TRUE',186: 'USR',187: 'VAL',188: 'VPOS',189: 'CHR$',190: 'GET$',191: 'INKEY$',
192: 'LEFT$(',193: 'MID$(',194: 'RIGHT$(',195: 'STR$',196: 'STRING$(',197: 'EOF',198: 'AUTO',199: 'DELETE',
200: 'LOAD',201: 'LIST',202: 'NEW',203: 'OLD',204: 'RENUMBER',205: 'SAVE',207: 'PTR',
208: 'PAGE',209: 'TIME',210: 'LOMEM',211: 'HIMEM',212: 'SOUND',213: 'BPUT',214: 'CALL',215: 'CHAIN',
216: 'CLEAR',217: 'CLOSE',218: 'CLG',219: 'CLS',220: 'DATA',221: 'DEF',222: 'DIM',223: 'DRAW',
224: 'END',225: 'ENDPROC',226: 'ENVELOPE',227: 'FOR',228: 'GOSUB',229: 'GOTO',230: 'GCOL',231: 'IF',
232: 'INPUT',233: 'LET',234: 'LOCAL',235: 'MODE',236: 'MOVE',237: 'NEXT',238: 'ON',239: 'VDU',
240: 'PLOT',241: 'PRINT',242: 'PROC',243: 'READ',244: 'REM',245: 'REPEAT',246: 'REPORT',247: 'RESTORE',
248: 'RETURN',249: 'RUN',250: 'STOP',251: 'COLOUR',252: 'TRACE',253: 'UNTIL',254: 'WIDTH',255: 'OSCLI',
}


from io import BytesIO
def binary_to_basic(fileData):
    
    reader = BytesIO(fileData)
    
    
    listing = []
    
    while True:
        line_pos = reader.tell()
        
        line_start, line_high = reader.read(2)
        
        
        if line_start != 13:
            raise Exception("expected ^M at %d, %x at %d", line_pos, line_start)
        
        
        if line_high == 255:
            #at end
            break
        
        line_low, line_length = reader.read(2)
                
        line_number = line_high * 256 + line_low
        
        line_data = reader.read(line_length-4)
        
        listing.append((line_number, decode_line(line_data)))
    
    return listing
    
def decode_line(data):
    
    res = []
    in_quotes=False
    i=0
    while i < len(data):
        c = data[i]
        if in_quotes:
            res.append(chr(c))
            
            if c==34: #double quote
                in_quotes=not in_quotes
            i+=1
        elif c == 0x8d:
            #line number
            x=data[i+1]
            y=data[i+2]
            z=data[i+3]
            
            x=(x*4)&255
            low=(x & 192) ^ y
            x=(x*4)&255
            high=x ^ z
            
            res.append(str(low + high*256))
            i+=4
        elif c in tokens:
            
            res.append(tokens[c])
            i+=1
        else:
            res.append(chr(c))
            if c==34: #double quote
                in_quotes=not in_quotes
            i+=1
        
    
    return ''.join(res)
    
    
        
        
    

def binary_to_basic_simple(fileData):
    i = 0
    listing = []
    while i < len(fileData):
        if fileData[i] != 13:
            raise Exception("Bad Program (expected ^M at start of line). {i=%d}" % i)
        
        i+=1
        #Line number high
        if fileData[i] == 255:
            break
        
        if len(fileData) < i+2:
            raise Exception("Bad Program (Line finishes before metadata). {i=%d}" % i)
        
        line = fileData[i]*256;
        i+=1
        #Line number low
        line = line + fileData[i];
        i+=1
        #Line length
        
        llen = fileData[i]-3; #different from above (infix/postfix increment confusion...)
        if llen < 0:
            raise Exception("Bad Program (Line length too short) {i=%d}" % i)
            
        
        raw = False # Set to True if in quotes
        decode=[]
        prevchar=""
        lend=i+llen
        
        if (lend > len(fileData)):
            raise Exception("Bad Program (Line truncated) {i=%d}" % i)
            
        # Read rest of line
        i+=1
        while i < lend:
            d = None
            if raw:
                d = chr(fileData[i])
            else:
                if fileData[i] == 0x8d:
                    #line token
                    i += 1
                    n1 = fileData[i]
                    i += 1
                    n2 = fileData[i]
                    i += 1
                    n3 = fileData[i]
                    
                    n1=(n1*4)&255
                    low=(n1 & 192) ^ n2
                    n1=(n1*4)&255
                    high=n1 ^ n3
                    lno=high*256+low
                    d=str(lno)
                else:
                    if fileData[i] in tokens:
                        d = tokens[fileData[i]]
                    else:
                        d = chr(fileData[i])
            
                
            if fileData[i] == ord('"'):
                raw = not raw
            
            decode.append(d)
            i += 1
        #print(line, "".join(decode), i)
        listing.append((line, "".join(decode)))
    
    return listing
