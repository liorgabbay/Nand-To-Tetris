"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        self.input_lines = [com for com in self.input_lines if (com and com[0:2]!="//")]
        self.input_lines = [com.strip() for com in self.input_lines]
        self.input_lines =[com.replace(" ","") for com in self.input_lines]
        self.cleancode()
        self.currentline = 0
        self.currentcom = self.input_lines[self.currentline]
        self.numlines = 0
        self.numtoinsert = 0
        for i in range(len(self.input_lines)):
            if self.input_lines[i][0] != '(':
                self.numlines += 1

    def cleancode(self):
        for i in range(len(self.input_lines)):
            num = self.input_lines[i].find("//")
            if(num != -1):
                self.input_lines[i] = self.input_lines[i][0:num]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """

        return bool(len(self.input_lines) - self.currentline)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """

        self.currentline += 1
        if self.has_more_commands():
            self.currentcom = self.input_lines[self.currentline]
            if self.command_type() != "L_COMMAND":
                self.numtoinsert += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        # Your code goes here!
        if self.currentcom[0] == '@':
            return "A_COMMAND"
        elif self.currentcom[0] == '(':
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # Your code goes here!
        command = self.command_type()
        if command == "A_COMMAND":
            return self.currentcom[1:]
        if command == "L_COMMAND":
            return self.currentcom[1:-1] #check if ok

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        for i in range(len(self.input_lines[self.currentline])):
            if self.currentcom[i] == '=':
                return self.currentcom[:i]
        return "null"


    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        command = self.currentcom
        eqal = command.find('=')
        semicolom = command.find(';')
        if eqal == -1 and semicolom == -1 :
            return command
        elif eqal != -1 and semicolom == -1 :
            return command[eqal+1:]
        elif eqal == -1 and semicolom != -1:
            return command[:semicolom]
        else:
            return command[eqal+1:semicolom]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        # Your code goes here!
        command = self.currentcom
        semicolom = command.find(';')
        if semicolom == -1:
            return "null"
        return command[semicolom+1:]
