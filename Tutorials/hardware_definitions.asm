; HARDWARE DEFINITIONS
;   updated 11 Jan 2021
;============================================================

; PROCESSOR CONSTANTS
; -------------------
carrybit		equ $01
compare			equ $02
withcarry		equ $08
registerselect  equ $10
intinhibit		equ $20
stackpointer	equ $07
sense			equ $80
flag			equ $40

; EFFECTS REGISTER
; ----------------
effects			equ $1e80

; BUTTONS
; --------
player1keys147c	equ $1E88 ;player1 keypad, bits: 1,4,7,clear,x,x,x,x
player1keys2580	equ $1E89 ;player1 keypad, bits: 2,5,8,0,x,x,x,x
player1keys369e	equ $1E8A ;player1 keypad, bits: 3,6,9,enter,x,x,x,x
player2keys147c	equ $1E8C ;player2 keypad, bits: 1,4,7,clear,x,x,x,x
player2keys2580	equ $1E8D ;player2 keypad, bits: 2,5,8,0,x,x,x,x
player2keys369e	equ $1E8E ;player2 keypad, bits: 3,6,9,enter,x,x,x,x
keymask123		equ $80     ;top row of keys
keymask456		equ $40
keymask789		equ $20
keymaskc0e		equ $10     ;bottom row of keys
console			equ $1E8B ;start and select buttons on console
consolestart	equ $40
consoleselect	equ $80


; PVI ADDRESSES AND CONSTANTS
; ---------------------------
pvi				equ $1F00

object1			equ $1F00
shape1			equ $1F00
hc1				equ $1F0A ; hc = Horizontal Coordinate
hcd1			equ $1F0B ; hcd = Horizontal Coordinate Duplicate
hcb1			equ $1F0B ; hcb =  ditto  (Signetics datasheet name)
vc1				equ $1F0C ; vc = Vertical Coordinate
voff1			equ $1F0D ; voff = Vertical Offset
vcb1			equ $1F0D ; vcb =  ditto  (Signetics datasheet name)

object2			equ $1F10
shape2			equ $1F10
hc2				equ $1F1A 
hcd2			equ $1F1B 
hcb2			equ $1FCB
vc2				equ $1F1C 
voff2			equ $1F1D 
vcb2			equ $1F1D

object3			equ $1F20
shape3			equ $1F20
hc3				equ $1F2A 
hcd3			equ $1F2B 
hcb3			equ $1F2B 
vc3				equ $1F2C 
voff3			equ $1F2D
vcb3			equ $1F2D

object4			equ $1F40
shape4			equ $1F40
hc4				equ $1F4A 
hcd4			equ $1F4B 
hcb4			equ $1F4B 
vc4				equ $1F4C 
voff4			equ $1F4D  
vcb4			equ $1F4D 

grid			equ $1F80     ; background grid
vbars			equ $1F80     ; vertical bar definitions
hbars			equ $1FA8     ; horizontal bar extensions

objectsize		equ $1FC0

colours12		equ $1FC1     ; colour objects 1,2
colours34		equ $1FC2     ; colour objects 3,4
coloursback		equ $1FC6     ; background grid colour / background grid enable / screen colour
backgnd			equ $1FC6     ;     deprecated

pitch			equ $1FC7

scoreformat		equ $1FC3
score12			equ $1FC8
score34			equ $1FC9

objectstatus	equ $1FCA     ; object-background collision / object complete
obj1complete	equ $08
obj2complete	equ $04
obj3complete	equ $02
obj4complete	equ $01
collisions		equ $1FCB     ; VRLE / inter-object collision
vrle			equ $40
adpot1			equ $1FCC
adpot2			equ $1FCD