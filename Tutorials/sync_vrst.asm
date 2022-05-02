; HARDWARE DEFINITIONS
;   updated 11 Jan 2021
;============================================================

; PROCESSOR CONSTANTS
; -------------------
carrybit        equ $01
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

; Tutorial SyncVRST
;=============================================================================
        org     0
reset_vector:                   ; the microprocessor starts here when the reset button is pressed
        bcta,un reset
        org     3
interrupt_vector:               ; interrupts shouldn't happen, but we set this just in case
        retc,un
reset:  
        lodi,r0 $20	        ; initialise program status word, just to be sure!
        lpsu                    ; inhibit interrupts, stack pointer=0
        lpsl                    ; register bank 0, without carry, arithmetic compare

        eorz    r0
        stra,r0 effects         ;initialise the 74LS378
        stra,r0 objectsize      ;all objects size 0
        bsta,un DefineObjects   ;define all objects 
   
        lodi,r0 $AA
        stra,r0 score12
        stra,r0 score34

        eorz    r0
        stra,r0 effects         ; !invert = 0 

        lodi,r0 0               ;  X / 000              /   0     / 000
        stra,r0 backgnd         ;    / black background / disabled / yellow screen

        lodi,r0 %00011101       ; XX  /  011        /   101
        stra,r0 colours12       ;     / obj1 red / obj2 green
        lodi,r0 %00110000       ; XX  /  110        /   000
        stra,r0 colours34       ;     / obj 3 blue / 4 white
endless:
        bsta,un Vsync0          ; make sure VRST hasn't started
        bsta,un Vsync1          ; wait for VRST to start

        loda,r0 vc1		; increment vertical position of object 1
        addi,r0 1
        stra,r0 vc1

        loda,r0 hc1		; decrement horizontal position of object 1
        subi,r0 1
        stra,r0 hc1

        bctr,un endless

;===================================================================
; subroutine  -  define shapes and position of all objects
                       
DefineObjects:
        lodi,r3 $0E
        lodi,r0 $FF
loopDS:                         
        stra,r0 shape1,r3-      ; create rectangular shapes
        stra,r0 shape2,r3
        stra,r0 shape3,r3
        stra,r0 shape4,r3
        brnr,r3 loopDS

        retc,un

;=================================================================
; subroutine - wait for VRST to clear
Vsync0:                       
        tpsu    sense
        bctr,eq Vsync0          ; wait for Sense bit to clear
        retc,un
;=================================================================
; subroutine - wait for VRST to set
Vsync1:         
        tpsu    sense           ; wait for Sense bit to be set
        bctr,lt Vsync1
        retc,un
;=================================================================
