#-------------------------------------------------- classic --------------------------------------------------#

### Building blocks
XYXY = 'X, tau, Y, tau, X, tau, Y,'
YXYX = 'Y, tau, X, tau, Y, tau, X,'
minusXYXY = '-X, tau, -Y, tau, -X, tau, -Y,'
minusYXYX = '-Y, tau, -X, tau, -Y, tau, -X,'
MREVa = 'tau, X/2, tau, -Y/2, tau*2, Y/2, tau, -X/2, tau,'
MREVb = 'tau, -X/2, tau, -Y/2, tau*2, Y/2, tau, X/2, tau,'
MREVc = 'tau, X/2, tau, Y/2, tau*2, -Y/2, tau, -X/2, tau,'
MREVd = 'tau, -X/2, tau, Y/2, tau*2, -Y/2, tau, X/2, tau,'

### Sequences
RAMSEY = 'tau,'
HAHN = 'tau/2, X, tau/2,'
PIBY2 = 'tau/2, X/2, tau/2,' 
XY16 = 'tau/2,'+XYXY+'tau,'+YXYX+'tau,'+minusXYXY+'tau,'+minusYXYX+'tau/2,'
MREV4 = MREVa
MREV8 = MREVa + MREVb
MREV16 = MREVa + MREVb + MREVc + MREVd

ACPMG2_XSTART = 'tau/2, Y, tau, -Y, tau/2,'
ACPMG4_XSTART = ACPMG2_XSTART*2
ACPMG8_XSTART = ACPMG2_XSTART*4
ACPMG16_XSTART = ACPMG2_XSTART*8

ACPMG2_YSTART = 'tau/2, X, tau, -X, tau/2,'
ACPMG4_YSTART = ACPMG2_YSTART*2
ACPMG8_YSTART = ACPMG2_YSTART*4
ACPMG16_YSTART = ACPMG2_YSTART*8

#--------------------------------------------------- Adam ----------------------------------------------------#

### bad cross family:
bc1fwd = 'tau, X/2, tau, Y, tau, -Y/2, tau, Y, tau, X/2, tau,'
bc1rev = 'tau, -X/2, tau, -Y, tau, Y/2, tau, -Y, tau, -X/2, tau,'

bc2fwd = 'tau, -X/2, tau, Y, tau, -Y/2, tau, Y, tau, -X/2, tau,'
bc2rev = 'tau, X/2, tau, -Y, tau, Y/2, tau, -Y, tau, X/2, tau,'

bc3fwd = 'tau, -Y/2, tau, X, tau, -X/2, tau, X, tau, -Y/2, tau,'
bc3rev = 'tau, Y/2, tau, -X, tau, X/2, tau, -X, tau, Y/2, tau,'

bc4fwd = 'tau, Y/2, tau, X, tau, -X/2, tau, X, tau, Y/2, tau,'
bc4rev = 'tau, -Y/2, tau, -X, tau, X/2, tau, -X, tau, -Y/2, tau,'

### challenger family:
ch1fwd = 'tau, -Y/2, tau, X, tau, X/2, tau, X, tau, -Y/2, tau,'
ch1rev = 'tau, Y/2, tau, -X, tau, -X/2, tau, -X, tau, Y/2, tau,'

ch2fwd = 'tau, X/2, tau, Y, tau, Y/2, tau, Y, tau, X/2, tau,'
ch2rev = 'tau, -X/2, tau, -Y, tau, -Y/2, tau, -Y, tau, -X/2, tau,'

ch3fwd = 'tau, Y/2, tau, X, tau, X/2, tau, X, tau, Y/2, tau,'
ch3rev = 'tau, -Y/2, tau, -X, tau, -X/2, tau, -X, tau, -Y/2, tau,'

ch4fwd = 'tau, -X/2, tau, Y, tau, Y/2, tau, Y, tau, -X/2, tau,'
ch4rev = 'tau, X/2, tau, -Y, tau, -Y/2, tau, -Y, tau, X/2, tau,'

### good cross family:
gc1fwd = 'tau, -X/2, tau, X, tau, Y/2, tau, X, tau, -X/2, tau,'
gc1rev = 'tau, X/2, tau, -X, tau, -Y/2, tau, -X, tau, X/2, tau,'

gc2fwd = 'tau, -X/2, tau, X, tau, -Y/2, tau, X, tau, -X/2, tau,'
gc2rev = 'tau, X/2, tau, -X, tau, Y/2, tau, -X, tau, X/2, tau,'

gc3fwd = 'tau, -Y/2, tau, Y, tau, -X/2, tau, Y, tau, -Y/2, tau,'
gc3rev = 'tau, Y/2, tau, -Y, tau, X/2, tau, -Y, tau, Y/2, tau,'

gc4fwd = 'tau, -Y/2, tau, Y, tau, X/2, tau, Y, tau, -Y/2, tau,'
gc4rev = 'tau, Y/2, tau, -Y, tau, -X/2, tau, -Y, tau, Y/2, tau,'

### Concatenation levels
        
bc1lvl0 = bc1fwd + bc1rev
bc2lvl0 = bc2fwd + bc2rev
bc3lvl0 = bc3fwd + bc3rev
bc4lvl0 = bc4fwd + bc4rev
bc1lvl1 = bc1fwd + bc1fwd + bc1rev + bc1rev
bc2lvl1 = bc2fwd + bc2fwd + bc2rev + bc2rev
bc3lvl1 = bc3fwd + bc3fwd + bc3rev + bc3rev
bc4lvl1 = bc4fwd + bc4fwd + bc4rev + bc4rev
bc1lvl2 = bc1fwd + bc1lvl1 + bc1fwd + bc1lvl1 + bc1rev + bc1lvl1 + bc1rev
bc2lvl2 = bc2fwd + bc2lvl1 + bc2fwd + bc2lvl1 + bc2rev + bc2lvl1 + bc2rev
bc3lvl2 = bc3fwd + bc3lvl1 + bc3fwd + bc3lvl1 + bc3rev + bc3lvl1 + bc3rev
bc4lvl2 = bc4fwd + bc4lvl1 + bc4fwd + bc4lvl1 + bc4rev + bc4lvl1 + bc4rev


ch1lvl0 = ch1fwd + ch1rev
ch2lvl0 = ch2fwd + ch2rev
ch3lvl0 = ch3fwd + ch3rev
ch4lvl0 = ch4fwd + ch4rev
ch1lvl1 = ch1fwd + ch1fwd + ch1rev + ch1rev
ch2lvl1 = ch2fwd + ch2fwd + ch2rev + ch2rev
ch3lvl1 = ch3fwd + ch3fwd + ch3rev + ch3rev
ch4lvl1 = ch4fwd + ch4fwd + ch4rev + ch4rev
ch1lvl2 = ch1fwd + ch1lvl1 + ch1fwd + ch1lvl1 + ch1rev + ch1lvl1 + ch1rev
ch2lvl2 = ch2fwd + ch2lvl1 + ch2fwd + ch2lvl1 + ch2rev + ch2lvl1 + ch2rev
ch3lvl2 = ch3fwd + ch3lvl1 + ch3fwd + ch3lvl1 + ch3rev + ch3lvl1 + ch3rev
ch4lvl2 = ch4fwd + ch4lvl1 + ch4fwd + ch4lvl1 + ch4rev + ch4lvl1 + ch4rev
        
gc1lvl0 = gc1fwd + gc1rev
gc2lvl0 = gc2fwd + gc2rev
gc3lvl0 = gc3fwd + gc3rev
gc4lvl0 = gc4fwd + gc4rev
gc1lvl1 = gc1fwd + gc1fwd + gc1rev + gc1rev
gc2lvl1 = gc2fwd + gc2fwd + gc2rev + gc2rev
gc3lvl1 = gc3fwd + gc3fwd + gc3rev + gc3rev
gc4lvl1 = gc4fwd + gc4fwd + gc4rev + gc4rev
gc1lvl2 = gc1fwd + gc1lvl1 + gc1fwd + gc1lvl1 + gc1rev + gc1lvl1 + gc1rev
gc2lvl2 = gc2fwd + gc2lvl1 + gc2fwd + gc2lvl1 + gc2rev + gc2lvl1 + gc2rev
gc3lvl2 = gc3fwd + gc3lvl1 + gc3fwd + gc3lvl1 + gc3rev + gc3lvl1 + gc3rev
gc4lvl2 = gc4fwd + gc4lvl1 + gc4fwd + gc4lvl1 + gc4rev + gc4lvl1 + gc4rev
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
