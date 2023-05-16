"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # A good place to start is to initialize a new Parser object:
    # parser = Parser(input_file)
    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")
    parser = Parser(input_file)
    symbol_t = SymbolTable()
    code = Code()
    while parser.has_more_commands():
        if parser.command_type() == "L_COMMAND":
            symbol_t.add_entry(parser.symbol(),parser.numtoinsert+1)
        parser.advance()
    parser.currentline = 0
    parser.currentcom = parser.input_lines[parser.currentline]
    n = 16
    while parser.has_more_commands():
        if parser.command_type() =="A_COMMAND":
            symbol = parser.symbol()
            if symbol_t.contains(symbol):
                cur_com = decimaltobin(symbol_t.symbol_table[symbol])
                output_file.write(cur_com+"\n")
            else:
                if symbol.isnumeric():
                    output_file.write(decimaltobin(int(symbol))+"\n")
                else:
                    symbol_t.add_entry(symbol,n)
                    output_file.write(decimaltobin(n)+"\n")
                    n += 1
        elif parser.command_type() =="C_COMMAND":
            shift = check_shift(parser.comp())
            if shift != "":
                output_file.write(shift +"\n")
            else:
                dest = code.dest(parser.dest())
                comp = code.comp(parser.comp())
                jump = code.jump(parser.jump())
                output_file.write("111"+comp+dest+jump+"\n")
        parser.advance()
def decimaltobin(val):
    cur_bin = bin(val).replace("0b","")
    for i in range(16 - len(cur_bin)):
        cur_bin="0"+cur_bin
    return cur_bin

def check_shift(shift):
    if shift == "D>>":
        return "1010010000010000"
    elif shift == "D<<":
        return "1010110000010000"
    elif shift == "A>>":
        return "1010000000010000"
    elif shift == "A<<":
        return "1010100000010000"
    elif shift =="M>>":
        return "1011000000010000"
    elif shift =="M<<":
        return "1011100000010000"
    else:
        return ""

if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
