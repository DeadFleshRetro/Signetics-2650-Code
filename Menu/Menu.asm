;========================================================================================
; Menu - Attempt to create a paginating textual menu system for, e.g., game selection. 
; 
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
hc1				equ	$1f0a	; hc = Horizontal Coordinate
hcd1			equ	$1f0b	; hcd = Horizontal Coordinate Duplicate
vc1				equ	$1f0c	; vc = Vertical Coordinate
voff1			equ	$1f0d	; voff = Vertical Offset

object2			equ	$1f10
hc2				equ	$1f1a
hcd2			equ	$1f1b
vc2				equ	$1f1c
voff2			equ	$1f1d

object3			equ	$1f20
hc3				equ	$1f2a
hcd3			equ	$1f2b
vc3				equ	$1f2c
voff3			equ	$1f2d

object4			equ	$1f40
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

; RAM

pausecounter	equ	$1f0e   ; RAM location of the pause counter in scratch memory
menupos			equ	$1f0f	; location of current menu position offset (from gridstart) in grid memory
itempointer		equ	$1f1e	; location of menu item pointer for writing shape data 

;=============================================================================
; PROGRAM CONSTANTS
; -----------------

; It's a good idea to define values like this only once, rather than at every 
; instance where they are used. Then, if the value has to be changed, it only
; has to be found and changed once.

stdpause		equ	2
movepitch		equ	$20
leftlimit		equ 29
rightlimit		equ 149
toplimit		equ	30
bottomlimit		equ 186
gridtop			equ 0
gridbottom		equ 32
menuitem		equ 21


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
	stra,r0	menupos			; clear the menu position offset
	stra,r0	effects			; initialise the 74LS378
	bsta,un	InitPVI			; gosub > Initialise the video chip
	bsta,un	Define_objects	; gosub > Define the initial shape and location of all objects
    bsta,un Set_grid        ; gosub > Set the initial grid

	lodi,r0	sound			; enable PVI sounds
	stra,r0	effects			;

endless:

	bsta,un	Stop_sounds		; gosub > stop all sounds
	bsta,un	Wait_vert_reset	; gosub > wait for the vertical reset
	bsta,un WriteMenuItems	; gosub > write all the menu items
	bsta,un	Joystick_1V		; gosub > CHeck joystick 1 and move the menu selector 
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
; subroutine - Write all the menu items for the current page

WriteMenuItems:
	bsta,un	Wait_obj4_complete	; wait for object 4 to finish writing
	lodi,r1	20		; get the item pointer (shape data is read backwards)
loopWMI_01
	lodi,r2 10
loopWMI_02
	subi,r2 1
	loda,r0	obj1frames,r1-
	stra,r0	object1,r2
	loda,r0	obj2frames,r1	
	stra,r0	object2,r2
	loda,r0	obj3frames,r1
	stra,r0	object3,r2
	loda,r0	obj4frames,r1
	stra,r0	object4,r2
	brnr,r2	loopWMI_02
	comi,r1	1
	bctr,gt	loopWMI_01
	retc,un

;===================================================================
; subroutine - Check vertical pot on Joystick 1

Joystick_1V
	bsta,un	Vsync1			; gosub > Vsync1 (wait for the vertical reset to begin)
	ppsu	flag			; set flag to 1 (read vertical pots) ISN'T THIS WRONG??
	loda,r0	joystick1		; load the value of joystick1 into register 0
	comi,r0	$20				; compare the controller value with 32
	bctr,lt joystick_up		; if it's less than 32, then go to joystick_up
	comi,r0	$B8				; compare it to 184 (everything in between we're calling dead-spot)
	bctr,gt	joystick_down	; if it's more than 184, then go to joystick_down
	retc,un					; return from subroutine
	
joystick_up:
	loda,r1	menupos			; load the current vertical coordinate into r3
	comi,r1	gridtop			; are we in the top row? I.e. against the top edge limit
	retc,eq					; if we are, then just return

	addi,r1	4				; erase the current menu selection bottom bar
	lodi,r0 0				
	stra	gridstart,r1	
	stra	gridstart,r1+
	subi,r1	9				; move where we're pointing all the way up to where
	lodi,r0	$FF				; the new top bar should go and draw it
	stra	gridstart,r1
	stra	gridstart,r1+
	subi,r1 1				; move the pointer back to the left top bar
	stra,r1	menupos			; write it back to the menu offset
	bsta,un	Play_move_sound	; gosub > Play the movement sound
	retc,un					; return		

joystick_down:
	loda,r1	menupos			; load the current menu position offset into r3
	comi,r1	gridbottom		; are we at the bottom of the grid?
	retc,eq					; if we are, then just return

	lodi,r0 0				; erase the current menu selection top bar
	stra	gridstart,r1	
	stra	gridstart,r1+
	addi,r1	7				; move where we're pointing to where we want the new bottom bar
	lodi,r0	$FF				; and draw it
	stra	gridstart,r1
	stra	gridstart,r1+
	subi,r1	5				; more where we're pointing back to the now top bar
	stra,r1	menupos			; write it back to the menu offset
	bsta,un	Play_move_sound	; gosub > Play the movement sound
	retc,un					; return


;===================================================================
; subroutine - Play the movement sound

Play_move_sound:
	lodi,r0	movepitch		; play movement tone
	stra,r0	pitch			;
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
	brnr,r3	loopDS_02		; loop back if r3 is non-zero
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
;subroutine - wait for object 4 to finish

Wait_obj4_complete
	loda,r3	objectstatus	; load the current object status into register 3
	tmi,r3	$01				; test bit 3 - object 4 completion
	bcfa,eq	Wait_obj4_complete	; wait if object 4 has not completed (if != then loop back)
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
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100
	db	64		;hc
	db	64		;hcb
	db	16		;vc
	db	255		;voff

two:
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%10101010
	db	%10001010
	db	%10001010
	db	%10101010
	db	%01001100
	db	80		;hc
	db	80		;hcb
	db	16		;vc
	db	255		;voff
three:
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%11101110
	db 	%10001000
	db	%11001100
	db	%10001000
	db	%10001000
	db	%11101000
	db	96		;hc
	db	96		;hcb
	db	16		;vc
	db	255		;voff
four:
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001010
	db 	%10101010
	db	%10001110
	db	%10001010
	db	%10101010
	db	%01101010
	db	112		;hc
	db	112		;hcb
	db	16		;vc
	db	255		;voff

; Grid Data
grid:
	dw	%1111111111111111
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
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	dw	%0000000000000000
	db	%00001001
	db	%00001001
	db	%00001001
	db	%00001001
	db	%00001001

; Object 1
obj1frames
;11
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100
;12
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100

; Object 2
obj2frames
;21
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100
;22
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100

; Object 3
obj3frames
;31
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100
;32
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100

; Object 4
obj4frames
;41
	db	%10000000
	db	%01000000
	db	%00100000
	db	%00010000
	db	%00001000
	db 	%00000100
	db	%00000010
	db	%00000001
	db	%00000010
	db	%00000100
;42
	db	%00010000
	db	%00001000
	db	%00010000
	db	%00001000
	db	%01011100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100