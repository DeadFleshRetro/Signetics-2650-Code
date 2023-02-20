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
objoff1			equ	$1f04
hc1				equ	$1f0a	; hc = Horizontal Coordinate
hcd1			equ	$1f0b	; hcd = Horizontal Coordinate Duplicate
vc1				equ	$1f0c	; vc = Vertical Coordinate
voff1			equ	$1f0d	; voff = Vertical Offset

object2			equ	$1f10
objoff2			equ	$1f14
hc2				equ	$1f1a
hcd2			equ	$1f1b
vc2				equ	$1f1c
voff2			equ	$1f1d

object3			equ	$1f20
objoff3			equ	$1f24
hc3				equ	$1f2a
hcd3			equ	$1f2b
vc3				equ	$1f2c
voff3			equ	$1f2d

object4			equ	$1f40
objoff4			equ	$1f44
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
joystickcheck	equ	$1f1e	; location for storing the current joystick pot value

;=============================================================================
; PROGRAM CONSTANTS
; -----------------

; It's a good idea to define values like this only once, rather than at every 
; instance where they are used. Then, if the value has to be changed, it only
; has to be found and changed once.

stdpause		equ	130
movepitch		equ	$20
leftlimit		equ 29
rightlimit		equ 149
toplimit		equ	30
bottomlimit		equ 186
gridtop			equ 0
gridbottom		equ 32
loops			equ 2


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
	ppsl	compare			; arithmetic compare

	eorz	r0				; clear register 0
	stra,r0	menupos			; clear the menu position offset
	stra,r0	effects			; initialise the 74LS378
	bsta,un	InitPVI			; gosub > Initialise the video chip
	bsta,un	Define_objects	; gosub > Define the initial size & colours of all objects
    bsta,un Set_grid        ; gosub > Set the initial grid

	lodi,r0	sound			; enable PVI sounds
	stra,r0	effects			;

	lodi,r0	loops			; store 'loops' into the joystick check counter
	stra,r0	joystickcheck

	bsta,un Vsync0          ; make sure VRST hasn't started
endless:
	bsta,un Vsync1          ; wait for VRST to start
	bsta,un	CheckJoystick	; check the joystick & move the menu selector if needed
	bsta,un	InitialObjects	; draw the original objects (1st menu item)
    bsta,un Vsync0			; wait for vertical sync to end
	bsta,un Duplicates		; draw the duplicate ojects (2nd to 9th menu item)
	bsta,un ThrowObjLocations	; throw the remaining object duplicates off screen 
	bsta,un PageNumber		; write the current page number
	bcta,un	endless			; return to the beginning of the endless loop


;===================================================================
; subroutine - Stop all sounds

Stop_sounds:
	eorz	r0				; stop any sounds by
	stra,r0	pitch			; setting pitch to zero
	retc,un					; return from subroutine

;===================================================================
; subroutine - Write all the menu items for the current page

Duplicates:
	lodi,r2	48				; load the overarching shape data pointer into r1 (8 items of 6 rows each)
	lodi,r1	8				; load the menu item pointer into r1 (8 items)
loopWMI_01:
	bsta,un Wait_obj4_complete	; wait until object 4 (previous row) is finished
	lodi,r3 6				; load the individual shape data pointer into r3
loopWMI_02:
	subi,r3 1				; decrement the individual shape data pointer
	loda,r0	obj1frames,r2-	; load shape data and write it to the current object duplicates
	stra,r0	objoff1,r3
	loda,r0	obj2frames,r2	
	stra,r0	objoff2,r3
	loda,r0	obj3frames,r2
	stra,r0	objoff3,r3
	loda,r0	obj4frames,r2
	stra,r0	objoff4,r3
	brnr,r3	loopWMI_02		; repeat until the individual shape data pointer is zero
	brnr,r1 WMI_03			; repeat doing this until menu item pinter is zero
	retc,un
WMI_03:	
	subi,r1	1				; 
	bctr,un loopWMI_01

;===================================================================
; subroutine - Check vertical pot on Joystick 1

CheckJoystick:
	loda,r0	joystickcheck	; check the joystick every 'loops' 'times this routine is called
	subi,r0	1				; decrement the joystick check counter
	brnr,r0	JC_01			; store it and return if it's not yet zero
	bsta,un	Stop_sounds		; stop the sounds
	bsta,un	Joystick_1V		; check the joystick
	loda,r0	loops			; load 'loops' back into the joystick check counter
	stra,r0	joystickcheck

JC_01:
	stra,r0	joystickcheck	; store the joystick check counter back and return
	retc,un


Joystick_1V
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
	lodi,r0	%00000111		; the new top bar should go and draw it
	stra	gridstart,r1
	lodi,r0	%11100000
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
	lodi,r0	%00000111		; the new top bar should go and draw it
	stra	gridstart,r1
	lodi,r0	%11100000
	stra	gridstart,r1+
	subi,r1	5				; more where we're pointing back to the now top bar
	stra,r1	menupos			; write it back to the menu offset
	bsta,un	Play_move_sound	; gosub > Play the movement sound
	retc,un					; return

;===================================================================
; subroutine - Write all the menu items for the current page

PageNumber:
	bsta,un Wait_obj4_complete
	bsta,un Wait_obj4_complete
	lodi,r0	134
	stra,r0	hcd1
	addi,r0	8
	stra,r0	hcd2
	addi,r0	8
	stra,r0	hcd3
	addi,r0	8
	stra,r0	hcd4
	lodi,r3	6				; set the decrement counter to 6 (bytes per object)
loopPN_01:
	loda,r0	pageobj1,r3-			; load each byte from the Data statements, including positions, etc.
	stra,r0	objoff1,r3
	loda,r0	pageobj2,r3
	stra,r0	objoff2,r3
	loda,r0	pageobj3,r3
	stra,r0	objoff3,r3
	loda,r0	pageobj4,r3
	stra,r0	objoff4,r3
	brnr,r3	loopPN_01
	retc,un

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
;	bsta,un	Wait_vert_reset	; goto subroutine "wait for vertical reset"
;	loda,r0	objectstatus	; clear VRLE and collision bits.
	loda,r0	pausecounter 	; load pause value into r1
	bcfr,eq	branchP_01		; if it's not zero, then branch to decrement pause
	retc,un					; return from sub routine

branchP_01:
	subi,r0	1				; decrement r1
	stra,r0	pausecounter	; load r1 back into pause
	bctr,un	loopP_01		; go back to top and wait for next frame

;===================================================================
; subroutine  - colours & sizes of all objects

Define_objects
	lodi,r0	%00100100		; Set initial object colour and size data
	stra,r0	colours12
	lodi,r0	%00100100
	stra,r0	colours34
	lodi,r0	%00000000
	stra,r0	objectsize
	retc,un					; return from sub routine

;===================================================================
; subroutine  - set the initial grid configuration

Set_grid:
	lodi,r3	45              ; set the decrement counter to 45 (to cover all of grid memory)
loopDS_02:
	loda,r0	grid,r3-        ; load the grid data into memory locations from gridstart onwards
	stra,r0	gridstart,r3
	brnr,r3	loopDS_02		; loop back if r3 is non-zero
    retc,un                 ; return from subroutine

;===================================================================
; subroutine  - set the initial object states

InitialObjects:
	lodi,r3	14				; set the decrement counter to 14 (bytes per object)
loopSOL_01:
	loda,r0	one,r3-			; load each byte from the Data statements, including positions, etc.
	stra,r0	object1,r3
	loda,r0	two,r3
	stra,r0	object2,r3
	loda,r0	three,r3
	stra,r0	object3,r3
	loda,r0	four,r3
	stra,r0	object4,r3
	brnr,r3	loopSOL_01
	retc,un					; return from subroutine

;===================================================================
; subroutine  - throw duplicate object locations off screen

ThrowObjLocations:
	lodi,r0	200
	stra,r0	hcd1
	stra,r0	hcd2
	stra,r0	hcd3
	stra,r0	hcd4
	retc,un					; return from subroutine

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
	loda,r0	objectstatus	; load the current object status into register 3
	tmi,r0	$01				; test bit 3 - object 1 completion
	bcfa,eq	Wait_obj4_complete	; wait if object 1 has not completed (if != then loop back)
	retc,un					; return from subroutine

;=============================================================
; All Object and Grid Data

; Object Data
one:
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01000100
	db 	%11001010
	db	%01000010
	db	%01000100
	db	%01001000
	db	%11101110
	db	80		;hc
	db	80		;hcb
	db	23		;vc
	db	9		;voff

two:
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%01001000
	db 	%10101010
	db	%01001010
	db	%00101110
	db	%10100010
	db	%01000010
	db	88		;hc
	db	88		;hcb
	db	23		;vc
	db	9		;voff
three:
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%11100110
	db 	%10001000
	db	%11001100
	db	%00101010
	db	%10101010
	db	%01000100
	db	96		;hc
	db	96		;hcb
	db	23		;vc
	db	9		;voff
four:
	db	%00000000
	db	%00000000
	db	%00000000
	db	%00000000
	db	%11100100
	db 	%00101010
	db	%00100100
	db	%01001010
	db	%01001010
	db	%01000100
	db	104		;hc
	db	104		;hcb
	db	23		;vc
	db	9		;voff

; Grid Data
grid:
	dw	%0000011111100000
	dw	%0000000000000000
	dw	%0000011111100000
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
	db	%01001100
	db 	%10101010
	db	%10001100
	db	%10001010
	db	%10101010
	db	%01101010
;12
	db	%01001000
	db 	%10101000
	db	%10101000
	db	%10101000
	db	%10101000
	db	%01001110
;13
	db	%11001000
	db 	%10101000
	db	%11001000
	db	%10101000
	db	%10101000
	db	%11001110
;14
	db	%01001110
	db 	%11100100
	db	%10100100
	db	%11100100
	db	%10100100
	db	%10101110
;15
	db	%10101110
	db 	%10100010
	db	%10100100
	db	%01001000
	db	%01001000
	db	%01001110
;16
	db	%01001100
	db 	%10101010
	db	%10101100
	db	%10101010
	db	%11101010
	db	%01101010
;17
	db	%11101110
	db 	%01000010
	db	%01000010
	db	%01000010
	db	%01001010
	db	%11100100
;18
	db	%01001100
	db 	%11101010
	db	%10101100
	db	%11101010
	db	%10101010
	db	%10101100

; Object 2
obj2frames
;21
	db	%01001110
	db 	%10101010
	db	%11101010
	db	%10101010
	db	%10101010
	db	%10101010
;22
	db	%10101010
	db 	%10101110
	db	%10101110
	db	%01001110
	db	%01001010
	db	%01001010
;23
	db	%01000100
	db 	%11101010
	db	%10101000
	db	%11101000
	db	%10101010
	db	%10100100
;24
	db	%11000010
	db 	%10100010
	db	%11000100
	db	%10100100
	db	%10101000
	db	%10101000
;25
	db	%01000100
	db 	%10101010
	db	%10101010
	db	%10100110
	db	%10100010
	db	%01001100
;26
	db	%01101110
	db 	%10000100
	db	%01000100
	db	%00100100
	db	%10100100
	db	%01000100
;27
	db	%10101000
	db 	%10101000
	db	%11001000
	db	%10101000
	db	%10101000
	db	%10101110
;28
	db	%01001100
	db 	%10101010
	db	%10001010
	db	%10001010
	db	%10101010
	db	%01001100

; Object 3
obj3frames
;31
	db	%11001100
	db 	%10101010
	db	%10101100
	db	%10101000
	db	%10101000
	db	%11001000
;32
	db	%11001110
	db 	%10100100
	db	%11000100
	db	%10000100
	db	%10000100
	db	%10001110
;33
	db	%10100000
	db 	%10100000
	db	%11000000
	db	%10100000
	db	%10100000
	db	%10100000
;34
	db	%01101110
	db 	%10001000
	db	%01001100
	db	%00101000
	db	%10101000
	db	%01001110
;35
	db	%01000100
	db 	%01001010
	db	%01000010
	db	%01000100
	db	%00000000
	db	%01000100
;36
	db	%10101010
	db 	%10101010
	db	%10101010
	db	%10101010
	db	%10100100
	db	%01000100
;37
	db	%10101110
	db 	%11101010
	db	%11101010
	db	%11101010
	db	%10101010
	db	%10101010
;38
	db	%11101110
	db 	%10001000
	db	%11001100
	db	%10001000
	db	%10001000
	db	%11101000

; Object 4
obj4frames
;41
	db	%11001010
	db 	%10101010
	db	%11000100
	db	%10101010
	db	%10101010
	db	%10101010
;42
	db	%01000110
	db 	%10101000
	db	%10000100
	db	%10000010
	db	%10101010
	db	%01000100
;43
	db	%11101010
	db 	%00101010
	db	%00101100
	db	%00101010
	db	%10101010
	db	%01001010
;44
	db	%01000000
	db 	%10100000
	db	%11100000
	db	%10100000
	db	%10100000
	db	%10100000
;45
	db	%01000100
	db 	%11100100
	db	%01000100
	db	%01000100
	db	%01001110
	db	%01000100
;46
	db	%10101010
	db 	%10101010
	db	%10100100
	db	%11101010
	db	%11101010
	db	%11101010
;47
	db	%01001100
	db 	%10101010
	db	%10101100
	db	%10101000
	db	%10101000
	db	%01001000
;48
	db	%01001010
	db 	%10101010
	db	%10001110
	db	%10001010
	db	%10101010
	db	%01101010

; Page 1
pageobj1
	db	%11000100
	db 	%10101010
	db	%11001000
	db	%10001000
	db	%10001010
	db	%10000110
pageobj2
	db	%00001000
	db 	%00011000
	db	%00001000
	db	%00001000
	db	%00001000
	db	%00011100
pageobj3
	db	%01001110
	db 	%10101000
	db	%10101100
	db	%10101000
	db	%10101000
	db	%01001000
pageobj4
	db	%01110000
	db 	%00010000
	db	%00010000
	db	%00100000
	db	%00100000
	db	%00100000