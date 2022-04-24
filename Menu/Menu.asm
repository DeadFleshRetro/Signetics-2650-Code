;========================================================================================
; Menu - Attempt to create a paginating textual menu system for, e.g., game selection. 
; 
;
;========================================================================================

; PROCESSOR CONSTANTS
; -------------------

carrybit		equ	$01		; bit positions of these flags in PSU & PSL
compare			equ	$02
withcarry		equ	$08
registerselect	equ	$10
intinhibit		equ	$20
stackpointer	equ	$07
sense			equ	$80
flag			equ	$40

sound			equ	%11000100

; PVI CONSTANTS
; -------------

effects			equ	$1e80	; location of the 74LS378

object1			equ	$1f00	; mem locations of object/shape 1
shape1			equ	$1f00	; 
hc1				equ	$1f0a	; hc = Horizontal Coordinate
hcd1			equ	$1f0b	; hcd = Horizontal Coordinate Duplicate
vc1				equ	$1f0c	; vc = Vertical Coordinate
voff1			equ	$1f0d	; voff = Vertical Offset

object2			equ	$1f10
shape2			equ	$1f10
hc2				equ	$1f1a
hcd2			equ	$1f1b
vc2				equ	$1f1c
voff2			equ	$1f1d

object3			equ	$1f20
shape3			equ	$1f20
hc3				equ	$1f2a
hcd3			equ	$1f2b
vc3				equ	$1f2c
voff3			equ	$1f2d

object4			equ	$1f40
shape4			equ	$1f40
hc4				equ	$1f4a
hcd4			equ	$1f4b
vc4				equ	$1f4c
voff4			equ	$1f4d

objectsize		equ	$1fc0	; location of object size variable

colours12		equ	$1fc1	; location of object 1 & 2 colours
colours34		equ	$1fc2	; location of object 3 & 4 colours
backgnd			equ	$1fc6	; location of background colour

pitch			equ	$1fc7

scoreformat		equ	$1fc3	; location of score format
score12			equ	$1fc8	; locations of score values
score34			equ	$1fc9

objectstatus	equ	$1fca	; location of object completion flags (and bg collisions)
obj1complete	equ	$08		; bit position of object 1 completion flag
obj2complete	equ	$04		; bit position of object 2 completion flag

gridstart		equ $1F80	; location of background grid

joystick1		equ	$1fcc	; location of joystick 1 value
joystick2		equ $1fcd	; location of joystick 2 value

pausecounter	equ	$1f0e   ; location of the pause counter in scratch memory

;=============================================================================
; PROGRAM CONSTANTS
; -----------------

; It's a good idea to define values like this only once, rather than at every 
; instance where they are used. Then, if the value has to be changed, it only
; has to be found and changed once.

stdpause		equ	2
movepitch		equ	$10
leftlimit		equ 29
rightlimit		equ 149
toplimit		equ	30
bottomlimit		equ 186
obj1animframes	equ 40
gridpos			equ gridstart

;=============================================================================
; PROGRAM START
; -----------------

	org	0
reset_vector:				; the microprocessor starts here when the reset button is pressed
	bcta,un	reset			; gosub > reset
interrupt_vector:			; interrupts shouldn't happen, but we set this just in case
	retc,un					; return without doing anything
reset:	
							; initialise program status word, just to be sure!
	ppsu	intinhibit		; inhibit interrupts
	cpsu	stackpointer	; stack pointer=%000
	cpsl	registerselect	; register bank 0
	cpsl	withcarry 		; without carry
	cpsl	compare			; arithmetic compare

	eorz	r0				; clear register 0
	stra,r0	effects			; initialise the 74LS378
	bsta,un	InitPVI			; gosub > Initialise the video chip
	bsta,un	Define_objects	; gosub > Define the initial shape and location of all objects
    bsta,un Set_grid        ; gosub > Set the initial grid

	lodi,r0	sound			; enable PVI sounds
	stra,r0	effects			;

endless:

	bsta,un	Wait_vert_reset	; gosub > wait for vertical reset
	bsta,un	Joystick_1V		; gosub > check the vertical pot of joystick 1
	lodi,r0	stdpause
	bsta,un	Pause			; gosub > pause
	bctr,un	endless			; return to the beginning of the endless loop


;===================================================================
; subroutine - Stop all sounds

Stop_sounds:
	eorz	r0				; stop any sounds by
	stra,r0	pitch			; setting pitch to zero
	retc,un					; return from subroutine

;===================================================================
; subroutine - Check vertical pot on Joystick 1

Joystick_1V
	bsta,un	Vsync1			; gosub > Vsync1 (wait for the vertical reset to begin)
	cpsu	flag			; clear flag to 1 (read vertical pots)
	loda,r0	joystick1		; load the value of joystick1 into register 0
	comi,r0	$20				; compare the controller value with 32
	bctr,lt	joystick_up		; if it's less than 32, then go to joystick_up
	comi,r0	$B8				; compare it to 184 (everything in between we're calling dead-spot)
	bctr,gt	joystick_down	; if it's more than 184, then go to joystick_down
	retc,un					; return from subroutine
	
joystick_up:
	loda,r3	vc1				; load the current vertical coordinate into r3
	comi,r3	toplimit		; are we in the top row? I.e. against the top edge limit
	retc,lt					; if we are, then just return


	loda,r2	gridoffset		; we're not, so load the gridoffset into r2
	subi,r2	4				; take 4 off it to reflect the byte of grid definition we're moving to
	loda,r1	gridmask		; load the current grid mask into r1
	bsta,un	Can_I_move		; gosub > Can I move, i.e. check if there's a dot to move to?
	brnr,r0	move_up			; if there is a dot, move the object up
	retc,un					; return from subroutine
	
move_up:
;	bsta,un	Play_move_sound	; gosub > Play the movement sound
	subi,r3	20				; subtract 20 from the vertical coordinate
	stra,r3	vc1				; write back all three values
	stra,r2	gridoffset		;
	stra,r1	gridmask		;
	retc,un					; return from subroutine

joystick_down:
	loda,r3	vc1				; load the current vertical coordinate into r3
	comi,r3 bottomlimit		; are we in the bottom row? I.e. against the bottom edge limit
	retc,gt					; if we are, then just return
	loda,r2	gridoffset		; we're not, so load the gridoffset into r2
	addi,r2	4				; add 4 to it to reflect the byte of grid definition we're moving to
	loda,r1	gridmask		; load the current gridmask into r1
	bsta,un	Can_I_move		; gosub > Can I move, i.e. check if there's a dot to move to?
	brnr,r0	move_down		; if there is a dot, move the object down
	retc,un

move_down:
	bsta,un	Play_move_sound	; gosub > Play the movement sound
	addi,r3 20				; add 20 to the vertical coordinate
	stra,r3	vc1				; write back all three values
	stra,r2	gridoffset		;
	stra,r1	gridmask		;
	retc,un					; return from subroutine


;===================================================================
; subroutine - initialise PVI

InitPVI:
	eorz	r0				; clear register 0
	lodi,r3	$CA				; set register 3 to one beyond the last address of writable PVI memory.
loopIP_01:					; loop to set every location between the beginning of PVI mem (object1)
	stra,r0	object1,r3-		; and the end of writable PVI memory to zero (contents of r0).
	brnr,r3	loopIP_01		;

	lodi,r0 	$02			; set the score format to single number at top
	stra,r0 	scoreformat	; write the score format
	lodi,r0 	$aa        	; set the first 2 score digits to larger than 9 (do not display)
	stra,r0 	score12		; write the first 2 score digits
	lodi,r0 	$aa			; set the second 2 score digits to larger than 9 (do not display)
	stra,r0 	score34		; write the second 2 score digits

	lodi,r0 	%01101001	; set the screen colour to blue, background enabled, grid to yellow 01101001
	stra,r0 	backgnd		; write the screen colour
	retc,un					; return from subroutine

;===================================================================
; subroutine - pause the number of cycles in r0

Pause:
	stra,r0	pausecounter
loopP_01:
	bsta,un	Wait_vert_reset	; goto subroutine "wait for vertical reset"
	loda,r0	objectstatus	; clear VRLE and collision bits.
	loda,r0	pausecounter 	; load pause value into r1
	bcfr,eq	branchP_01		; if it's not zero, then branch to decrement pause
	retc,un					; return from sub routine

branchP_01:
	subi,r0	1				; decrement r1
	stra,r0	pausecounter	; load r1 back into pause
	bctr,un	loopP_01		; go back to top and wait for next frame

;===================================================================
; subroutine  -  define shapes, positions, colours & sizes of all objects

Define_objects
; Load Objects into PVI
	lodi,r3	14              ; set the decrement counter to 14 (bytes per object)
loopDS_01:
	loda,r0	one,r3-         ; load each byte from the Data statements, including positions, etc.
	stra,r0	object1,r3
	loda,r0	two,r3
	stra,r0	object2,r3
	loda,r0	three,r3
	stra,r0	object3,r3
	loda,r0	four,r3
	stra,r0	object4,r3
	brnr,r3	loopDS_01

; Set initial object colour and size data
	lodi,r0	%00100100
	stra,r0	colours12
	lodi,r0	%00100100
	stra,r0	colours34
	lodi,r0	%01010101
	stra,r0	objectsize
	retc,un					; return from sub routine

;===================================================================
; subroutine  -  set the initial grid configuration

Set_grid:
	lodi,r3	45              ; set the decrement counter to 45 (to cover all of grid memory)
loopDS_02:
	loda,r0	grid,r3-        ; load the grid data into memory locations from gridstart onwards
	stra,r0	gridstart,r3
	brnr,r3	loopDS_02
    retc,un                 ; return from subroutine

;=================================================================
; subroutine - wait for vertical reset to clear
Vsync0:
loopVS0_01:
	tpsu	sense			; test the Sense bit in PSU (set condition codes to %10 when Sense = 0)
	bctr,a1	loopVS0_01		; loop until Sense bit is clear (a1 = all 1s)
	retc,un					; return from subroutine

;=================================================================
; subroutine - wait for vertical reset to set
Vsync1:
loopVS1_01:
	tpsu	sense			; test the Sense bit in PSU (set condition codes to %00 when Sense = 1)
	bctr,s0	loopVS1_01		; loop until Sense bit is set (s0 = some 0s)
	retc,un					; return from subroutine


;============================================================
; subroutine - wait for start of vertical reset period
Wait_vert_reset:
	cpsl	compare			; set COM bit to arithmetic compare   
							; (the Sense input, VRST, is read on bit 7 of PSU, which is also the sign bit
							; so we can use arithmetic compare to test this bit)

loopWVR_01:					; wait here while Sense line is HIGH (in case we arrive here in the middle of a vertical reset)
	spsu					; get PSU
	bctr,lt	loopWVR_01		; loop if it's negative (Sense bit is positive)

loopWVR_02					; wait here while Sense line is LOW (now just waiting for VRST to go HIGH)
	spsu					; get PSU
	bcfr,lt loopWVR_02		; loop if it's positive

	ppsl	compare			; set COM back to logical compare
	retc,un					; return from subroutine

;=============================================================
;subroutine - wait for object 1 to finish

Wait_obj1_complete
	loda,r3	objectstatus	; load the current object status into register 3
	tmi,r3	$08				; test bit 3 - object 1 completion
	bcfa,eq	Wait_obj1_complete	; wait if object 1 has not completed (if != then loop back)
	retc,un					; return from subroutine
	
;=============================================================
;subroutine - wait for object to finish
;  enter with r1=mask for bit to be tested:
;	obj1=$08, obj2=$04, obj3=$02, obj4=$01

Wait_obj:
	loda,r0 objectstatus	; load the current object status into register 0
	andz	r1				; AND the r0 against the input mask in r1
	bctr,eq	Wait_obj		; While the condition codes are showing true, loop back
	retc,un					; return from subroutine

;=============================================================
; All Object and Grid Data

; Object Data
one:
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100
	db	%00000000
	db	%00000000
	db	36		;hc
	db	36		;hcb
	db	20		;vc
	db	255		;voff

two:
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%10101010
	db	%10001010
	db	%10001010
	db	%10101010
	db	%01001100
	db	%00000000
	db	%00000000
	db	52		;hc
	db	52		;hcb
	db	20		;vc
	db	255		;voff
three:
	db	%00000000
	db	%00000000
	db	%11101110
	db 	%10001000
	db	%11001100
	db	%10001000
	db	%10001000
	db	%11101000
	db	%00000000
	db	%00000000
	db	68		;hc
	db	68		;hcb
	db	20		;vc
	db	255		;voff
four:
	db	%00000000
	db	%00000000
	db	%01001010
	db 	%10101010
	db	%10001110
	db	%10001010
	db	%10101010
	db	%01101010
	db	%00000000
	db	%00000000
	db	84		;hc
	db	84		;hcb
	db	20		;vc
	db	255		;voff


; Grid Data
grid:
	dw	%0111111111111111
	dw	%0000000000000000
	dw	%1111111111111111
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%1111111111111111
	dw	%0000000000000000
	dw	%1111111111111111
	dw	%0000000000000000
	db	%00001001
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000