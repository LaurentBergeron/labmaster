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
PI = 'tau/2, X, tau/2,'
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
bclvl0 = bc1fwd + bc1rev
bclvl1 = bc1fwd + bc1fwd + bc1rev + bc1rev
bclvl2 = bc1fwd + bclvl1 + bc1fwd + bclvl1 + bc1rev + bclvl1 + bc1rev

bcfwd_list = [bc1fwd, bc2fwd, bc3fwd, bc4fwd]
chfwd_list = [ch1fwd, ch2fwd, ch3fwd, ch4fwd]
gcfwd_list = [gc1fwd, gc2fwd, gc3fwd, gc4fwd]

bcrev_list = [bc1rev, bc2rev, bc3rev, bc4rev]
chrev_list = [ch1rev, ch2rev, ch3rev, ch4rev]
gcrev_list = [gc1rev, gc2rev, gc3rev, gc4rev]
        
        
bclvl0_list = [fwd+rev for fwd,rev in zip(bcfwd_list, bcrev_list)]
chlvl0_list = [fwd+rev for fwd,rev in zip(chfwd_list, chrev_list)]
gclvl0_list = [fwd+rev for fwd,rev in zip(gcfwd_list, gcrev_list)]

bclvl1_list = [fwd*2+rev*2 for fwd,rev in zip(bcfwd_list, bcrev_list)]
chlvl1_list = [fwd*2+rev*2 for fwd,rev in zip(chfwd_list, chrev_list)]
gclvl1_list = [fwd*2+rev*2 for fwd,rev in zip(gcfwd_list, gcrev_list)]

bclvl2_list = [fwd+lvl1+fwd+lvl1+rev+lvl1+rev for fwd,rev,lvl1 in zip(bcfwd_list, bcrev_list, bclvl1_list)]
chlvl2_list = [fwd+lvl1+fwd+lvl1+rev+lvl1+rev for fwd,rev,lvl1 in zip(chfwd_list, chrev_list, chlvl1_list)]
gclvl2_list = [fwd+lvl1+fwd+lvl1+rev+lvl1+rev for fwd,rev,lvl1 in zip(gcfwd_list, gcrev_list, gclvl1_list)]
