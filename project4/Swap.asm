// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.
@R14
D=M
@maxaddress 
M=D
@minaddress
M=D
A=M
D=M
@max
M=D
@min
M=D
@i
M=0
(LOOP)
//CHACK IF WE ENTER THE END OF THE LOOP
	@R15
	D=M
	@i
	D=D-M
	@POS
	D;JLE
//CHACK IF THE CURRENT VAL IS CUR MAX
	@R14
	D=M
	@i
	A=D+M
	D=M
	@max
	D=D-M
	@CHANGEMAX
	D;JGT
	(CONTINUE1)
//CHACK IF THE CURRENT VAL IS CUR MIN
	@R14
	D=M
	@i
	A=D+M
	D=M
	@min
	D=D-M
	@CHANGEMIN
	D;JLT
	(CONTINUE2)
	@i
	M=M+1
	@LOOP
	0;JMP

	(CHANGEMAX)
		@R14
		D=M
		@i
		A=D+M
		D=A
		@maxaddress
		M=D
		A=M
		D=M
		@max
		M=D
		@CONTINUE1
		0;JMP

	(CHANGEMIN)
		@R14
		D=M
		@i
		A=D+M
		D=A
		@minaddress
		M=D
		A=M
		D=M
		@min
		M=D
		@CONTINUE2
		0;JMP

	(POS)
		@min
		D=M
		@tmp
		M=D
		@max
		D=M
		@minaddress
		A=M
		M=D
		@tmp
		D=M
		@maxaddress
		A=M
		M=D
		(END)
			@END
			0;JMP












	










