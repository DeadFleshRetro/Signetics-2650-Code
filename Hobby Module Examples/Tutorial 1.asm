; Hobby Module Tutorial Programme #1

begin:
	org	0
	bcta,un		prog
	retc,un

prog:
	lodi,r0		06	; Load value 06 into r0
	lodi,r1		02	; Load value 02 into r1
	addz		r1	; Add the value in r1 to r0
	strz		r2	; Store value in r0 in r2
	halt