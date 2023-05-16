"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        self.input_lines = [com for com in self.input_lines if (com and com[0:2] != "//")] #delete comment
        self.input_lines = [com.strip() for com in self.input_lines]
        # self.input_lines = [com.replace(" ", "") for com in self.input_lines]
        self.cleancode()
        self.numoflines = len(self.input_lines)
        self.curline=0
        self.currentcommand = self.input_lines[0]

    def cleancode(self):
        for i in range(len(self.input_lines)): #clear comment
            num = self.input_lines[i].find("//")
            if (num != -1):
                self.input_lines[i] = self.input_lines[i][0:num]
        for i in range (len(self.input_lines)): #clear tabs in the begin
            j=0
            while(self.input_lines[j] ==' '):
                j+=1
            self.input_lines[i] = self.input_lines[i][j:]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return bool(self.numoflines - self.curline)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        self.curline += 1
        if self.has_more_commands():
            self.currentcommand = self.input_lines[self.curline]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        arr=self.currentcommand.split()
        com = arr[0]
        if com == "push":
            return "C_PUSH"
        elif com == "pop":
            return "C_POP"
        elif com == "labal":
            return "C_LABEL"
        elif com == "goto":
            return "C_GOTO"
        elif com == "if":
            return "C_IF"
        elif com == "function":
            return "C_FUNCTION"
        elif com == "return":
            return "C_RETURN"
        elif com == "call":
            return "C_CALL"
        else:
            return "C_ARITHMETIC"


    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        arr = self.currentcommand.split()
        if len(arr) == 1:
            return arr[0]
        else:
            return arr[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        arr = self.currentcommand.split()
        return int(arr[2])
