"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


# todo - check code , make small function for one target
# todo chack - file name , check staticvar - from 0 or from 1 ?

class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.file_name = ""  # var for the file name
        self.output = output_stream  # output file
        self.labelcount = 1  # var for labels
        self.return_count = 1
        self.current_function = ""

    def boot(self):
        self.output.write("@256\n")
        self.output.write("D=A\n")
        self.output.write("@SP\n")
        self.output.write("M=D\n")
        self.write_call("Sys.init", 0)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.file_name = filename  # set the file name

    def spplus(self):
        "apply sp++"
        self.output.write("@SP\n")
        self.output.write("M=M+1\n")

    def spminus(self):
        "apply sp--"
        self.output.write("@SP\n")
        self.output.write("M=M-1\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        # Your code goes here!
        if command == "add" or command == "sub":  # if the arithmatic function is sub or add
            self.add_or_sub(command)

        if command == "neg":
            self.neg()

        if command == "lt" or command == "gt" or command == "eq":  # if the arithmatic function is lt or gt or eq
            self.comp_operators(command)

        if command == "and" or command == "or":  # if the aritmatic func is and or or
            self.and_or_operators(command)

        if command == "not":  # if the arithmatic function is not
            self.not_operator()

    def add_or_sub(self, command) -> None:
        self.output.write("//" + command + "\n")  # comment
        self.spminus()
        self.output.write("A=M\n")
        self.output.write("D=M\n")  # save arg1
        self.spminus()
        self.output.write("A=M\n")

        if command == "add":
            self.output.write("D=D+M\n")  # compute arg1+arg2
        else:
            self.output.write("D=M-D\n")  # compute arg2-arg1

        self.output.write("@SP\n")
        self.output.write("A=M\n")  # get into the value
        self.output.write("M=D\n")  # save the result
        self.spplus()

    def neg(self) -> None:
        self.output.write("//neg\n")
        self.spminus()
        self.output.write("A=M\n")  # get into the value
        self.output.write("M=-M\n")  # change m to -m
        self.spplus()

    def check_sign(self):
        positive_arg1 = self.file_name + "." + self.current_function + "positivefirst" + str(self.labelcount)
        negative_arg1 = self.file_name + "." + self.current_function + "negativefirst" + str(self.labelcount)
        positive_arg2 = self.file_name + "." + self.current_function + "positivesec" + str(self.labelcount)
        negative_arg2 = self.file_name + "." + self.current_function + "negativesec" + str(self.labelcount)
        signequal = self.file_name + "." + self.current_function + "signequal" + str(self.labelcount)
        sign_pos = self.file_name + "." + self.current_function + "signpos" + str(self.labelcount)
        sign_neg = self.file_name + "." + self.current_function + "signneg" + str(self.labelcount)
        checkarg2 = self.file_name + "." + self.current_function + "chacksec" + str(self.labelcount)
        checksign = self.file_name + "." + self.current_function + "chacksign" + str(self.labelcount)
        sign = "R14"
        self.output.write("@" + sign + "\n")  # val for checking the signs
        self.output.write("M=0\n")
        self.output.write("@SP\n")
        self.output.write("A=M-1\n")
        self.output.write("D=M\n")  # get the first val
        self.output.write("@" + positive_arg1 + "\n")  # checking if positive
        self.output.write("D;JGT\n")
        self.output.write("@" + signequal + "\n")
        self.output.write("D;JEQ\n")
        self.output.write("@" + negative_arg1 + "\n")  # checking if negative
        self.output.write("0;JMP\n")

        # positive arg1
        self.output.write("(" + positive_arg1 + ")\n")
        self.output.write("@" + sign + "\n")
        self.output.write("M=M-1\n")  # if arg1 is positive sign--
        self.output.write("@" + checkarg2 + "\n")
        self.output.write("0;JMP\n")

        # negative_arg1
        self.output.write("(" + negative_arg1 + ")\n")
        self.output.write("@" + sign + "\n")
        self.output.write("M=M+1\n")  # if arg1 is negative sign++
        self.output.write("@" + checkarg2 + "\n")
        self.output.write("0;JMP\n")

        self.output.write("(" + checkarg2 + ")\n")
        self.output.write("@2\n")
        self.output.write("D=A\n")
        self.output.write("@SP\n")
        self.output.write("A=M-D\n")
        self.output.write("D=M\n")  # get arg 2
        self.output.write("@" + positive_arg2 + "\n")
        self.output.write("D;JGT\n")
        self.output.write("@" + signequal + "\n")
        self.output.write("D;JEQ\n")
        self.output.write("@" + negative_arg2 + "\n")
        self.output.write("D;JLT\n")

        # positive arg2
        self.output.write("(" + positive_arg2 + ")\n")
        self.output.write("@" + sign + "\n")
        self.output.write("M=M+1\n")  # if arg2 is positive sign++
        self.output.write("@" + checksign + "\n")
        self.output.write("0;JMP\n")

        # negative_arg2
        self.output.write("(" + negative_arg2 + ")\n")
        self.output.write("@" + sign + "\n")
        self.output.write("M=M-1\n")
        self.output.write("@" + checksign + "\n")
        self.output.write("0;JMP\n")

        self.output.write("(" + checksign + ")\n")
        self.output.write("@" + sign + "\n")
        self.output.write("D=M\n")
        self.output.write("@" + sign_pos + "\n")
        self.output.write("D;JGT\n")
        self.output.write("@" + sign_neg + "\n")
        self.output.write("D;JLT\n")
        self.output.write("@" + signequal + "\n")
        self.output.write("D;JEQ\n")

    def comp_operators(self, command) -> None:
        signequal = self.file_name + "." + self.current_function + "signequal" + str(self.labelcount)
        sign_pos = self.file_name + "." + self.current_function + "signpos" + str(self.labelcount)
        sign_neg = self.file_name + "." + self.current_function + "signneg" + str(self.labelcount)
        ratio = self.file_name + "." + self.current_function + "ratio" + str(self.labelcount)
        endcomp = self.file_name + "." + self.current_function + "end_comp" + str(self.labelcount)
        self.output.write("//" + command + "\n")
        self.check_sign()
        self.output.write("(" + signequal + ")\n")
        self.spminus()
        self.output.write("A=M\n")
        self.output.write("D=M\n")  # save arg1
        self.spminus()
        self.output.write("A=M\n")
        self.output.write("D=M-D\n")  # compute the diff between arg1 and arg2
        self.output.write("@" + ratio + "\n")  # compute label for if the res is ok.
        if command == "eq":
            self.output.write("D;JEQ\n")  # check if D=0
        elif command == "lt":
            self.output.write("D;JLT\n")  # check if D<0
        else:
            self.output.write("D;JGT\n")  # check if D>0

        self.di_sp()  # get into the adrress in sp
        self.output.write("M=0\n")  # put false, if the res is false
        self.spplus()
        self.output.write("@" + endcomp + "\n")  # jump to end
        self.output.write("0;JMP\n")
        self.output.write("(" + ratio + ")\n")  # start the label if res is ok
        self.di_sp()  # get into sp
        self.output.write("M=-1\n")  # put true
        self.spplus()
        self.output.write("@" + endcomp + "\n")  # jump to end
        self.output.write("0;JMP\n")
        self.output.write("(" + sign_pos + ")\n")
        self.spminus()
        self.output.write("A=M-1\n")
        if command == "eq":
            self.output.write("M=0\n")
        elif command == "lt":
            self.output.write("M=0\n")
        else:
            self.output.write("M=-1\n")
        self.output.write("@" + endcomp + "\n")  # jump to end
        self.output.write("0;JMP\n")
        self.output.write("(" + sign_neg + ")\n")
        self.spminus()
        self.output.write("A=M-1\n")
        if command == "eq":
            self.output.write("M=0\n")
        elif command == "lt":
            self.output.write("M=-1\n")
        else:
            self.output.write("M=0\n")
        self.output.write("@" + endcomp + "\n")  # jump to end
        self.output.write("0;JMP\n")
        self.output.write("(" + endcomp + ")\n")
        self.labelcount += 1  # increse label_count by 1

    def and_or_operators(self, command):
        self.output.write("//" + command + "\n")
        self.spminus()
        self.output.write("A=M\n")
        self.output.write("D=M\n")  # save arg1
        self.spminus()
        self.output.write("A=M\n")  # get arg2
        if command == "and":
            self.output.write("D=D&M\n")  # compute arg1 & arg2
        else:
            self.output.write("D=D|M\n")  # compute arg1 || arg2
        self.di_sp()  # get into sp
        self.output.write("M=D\n")  # put the result
        self.spplus()

    def not_operator(self):
        self.output.write("//not\n")  # label for me
        self.spminus()
        self.output.write("A=M\n")
        self.output.write("M=!M\n")  # change m to -m
        self.spplus()

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        if command == "C_PUSH":
            self.push_func(segment, index)

        if command == "C_POP":
            self.pop_func(segment, index)

    def push_func(self, segment: str, index: int) -> None:
        self.output.write("//push " + segment + "," + str(index) + "\n")  # comment for me

        if segment == "constant":  # if we push constant
            self.output.write("@" + str(index) + "\n")
            self.output.write("D=A\n")  # get the val to get in
            self.di_sp()  # get into sp
            self.output.write("M=D\n")  # change the value
            self.spplus()

        elif segment == "static":
            self.output.write("@" + self.file_name + "." + str(index) + "\n")  # get into the static var
            self.output.write("D=M\n")  # save the static var
            self.di_sp()  # get into sp
            self.output.write("M=D\n")  # save the static in the top of sp
            self.spplus()

        elif segment == "pointer":  # *SP=THIS/THAT, SP++
            if index == 0:
                self.output.write("@THIS\n")
            else:
                self.output.write("@THAT\n")
            self.output.write("D=M\n")
            self.di_sp()
            self.output.write("M=D\n")
            self.spplus()

        else:  # if segment == "local" || "argument" ||"this" ||"that" || "temp"
            self.push_segment(segment, index)

    def pop_func(self, segment: str, index: int):
        self.output.write("//pop" + segment + "," + str(index) + "\n")
        if segment == "static":
            self.spminus()
            self.output.write("A=M\n")
            self.output.write("D=M\n")
            self.output.write("@" + self.file_name + "." + str(index) + "\n")
            self.output.write("M=D\n")
        elif segment == "pointer":  # SP--,THIS\THAT = *SP
            self.spminus()
            self.output.write("A=M\n")
            self.output.write("D=M\n")
            if index == 0:
                self.output.write("@THIS\n")
            else:
                self.output.write("@THAT\n")
            self.output.write("M=D\n")
        else:  # if segment == "local" || "argument" ||"this" ||"that" || "temp"
            self.pop_segment(segment, index)

    def di_sp(self):
        self.output.write("@SP\n")
        self.output.write("A=M\n")

    def push_segment(self, segment: str, index: int) -> None:
        self.p_segment_plus_i(segment, index)
        self.output.write("A=M\n")  # get into the addr
        self.output.write("D=M\n")  # save the var
        self.di_sp()  # get into sp
        self.output.write("M=D\n")  # put the var
        self.spplus()
        self.labelcount += 1  # increase the labelcount cause we used it

    def pop_segment(self, segment: str, index: int) -> None:
        self.p_segment_plus_i(segment, index)  # get the place
        self.spminus()
        self.output.write("A=M\n")
        self.output.write("D=M\n")  # save sp val
        self.output.write("@R14\n")  # get the address from R14
        self.output.write("A=M\n")
        self.output.write("M=D\n")  # save the var in the segment
        self.labelcount += 1

    def p_segment_plus_i(self, segment: str, index: int) -> None:
        self.output.write("@" + str(index) + "\n")
        self.output.write("D=A\n")  # get the index
        if segment == "local":
            self.output.write("@LCL\n")
            self.output.write("D=D+M\n")  # get the place
        elif segment == "argument":
            self.output.write("@ARG\n")
            self.output.write("D=D+M\n")  # get the place
        elif segment == "this":
            self.output.write("@THIS\n")
            self.output.write("D=D+M\n")  # get the place
        elif segment == "that":
            self.output.write("@THAT\n")
            self.output.write("D=D+M\n")  # get the place
        else:
            self.output.write("@5\n")
            self.output.write("D=D+A\n")  # get the place
        self.output.write("@R14\n")  # save the place in R14
        self.output.write("M=D\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command.
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """

        label_name = self.current_function + "$" + label
        # label_name = self.current_function + "$" + label
        # label_name = label
        self.output.write("//label\n")
        self.output.write("(" + label_name + ")\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """

        label_name = self.current_function + "$" + label
        # label_name = self.current_function + "$" + label
        # label_name = label
        self.output.write("//goto\n")
        self.output.write("@" + label_name + "\n")
        self.output.write("0;JMP\n")  # if not 0 jmp

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command.

        Args:
            label (str): the label to go to.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        label_name = self.current_function + "$" + label
        # label_name = self.current_function + "$" + label
        # label_name = label
        self.output.write("//if-goto\n")
        self.output.write("@SP\n")
        self.output.write("M=M-1\n")  # get to the top val in the sp
        self.output.write("A=M\n")
        self.output.write("D=M\n")  # get the top val in sp
        self.output.write("@" + label_name + "\n")
        self.output.write("D;JNE\n")  # if not 0 jmp #todo - check if need exactly -1 or not 0 is ok?

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command.
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.output.write("//function\n")
        self.current_function = function_name  #### check
        self.output.write("(" + function_name + ")\n")  # (function_name)
        for i in range(n_vars):  # push 0 n time to constant
            self.push_func("constant", 0)

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command.
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        self.output.write("//call_function\n")
        # push return address
        returnaddress = f"{function_name}$ret.{self.return_count}"
        self.output.write(f"@{returnaddress}\n")
        self.output.write("D=A\n")
        self.di_sp()
        self.output.write("M=D\n")
        self.spplus()
        # push LCL
        self.push_for_call("LCL")
        # push ARG
        self.push_for_call("ARG")
        # push THIS
        self.push_for_call("THIS")
        # push THAT
        self.push_for_call("THAT")
        # ARG = SP -5-nArgs
        self.output.write("@SP\n")
        self.output.write("D=M\n")
        self.output.write("@" + str(n_args) + "\n")
        self.output.write("D=D-A\n")
        self.output.write("@5\n")
        self.output.write("D=D-A\n")
        self.output.write("@ARG\n")
        self.output.write("M=D\n")
        # LCL = SP
        self.output.write("@SP\n")
        self.output.write("D=M\n")
        self.output.write("@LCL\n")
        self.output.write("M=D\n")
        # goto - functionName
        # self.write_goto(function_name)
        self.output.write("@" + function_name + "\n")
        self.output.write("0;JMP\n")
        # (returnAddress)
        # self.write_label(returnaddress)
        self.output.write("(" + returnaddress + ")\n")
        self.return_count += 1  # check
        self.labelcount += 1

    def push_for_call(self, segment: str) -> None:
        self.output.write("@" + segment + "\n")
        self.output.write("D=M\n")
        self.di_sp()
        self.output.write("M=D\n")
        self.spplus()

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""
        # This is irrelevant for project 7,
        # you will implement this in project 8!
        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        labelcount = self.labelcount
        # endframe = self.file_name + ".endFrame" + str(labelcount)
        # retaddr = self.file_name + ".retAddr" + str(labelcount)
        endframe = "R13"
        retaddr = "R15"
        self.output.write("//write_return\n")
        self.output.write("@LCL\n")
        self.output.write("D=M\n")
        self.output.write("@" + endframe + "\n")
        self.output.write("M=D\n")
        self.output.write("@5\n")
        self.output.write("D=D-A\n")
        self.output.write("A=D\n")
        self.output.write("D=M\n")
        self.output.write("@" + retaddr + "\n")
        self.output.write("M=D\n")
        self.pop_func("argument", 0)
        self.output.write("@ARG\n")
        self.output.write("D=M+1\n")
        self.output.write("@SP\n")
        self.output.write("M=D\n")
        self.restore_segment("THAT", 1, labelcount)
        self.restore_segment("THIS", 2, labelcount)
        self.restore_segment("ARG", 3, labelcount)
        self.restore_segment("LCL", 4, labelcount)
        self.output.write("@" + retaddr + "\n")
        self.output.write("A=M\n")
        self.output.write("0;JMP\n")
        # self.current_function = ""  #### check
        self.labelcount += 1

    def restore_segment(self, segment: str, index: int, label_count: int) -> None:
        # endframe = self.file_name + ".endFrame" + str(label_count)
        endframe = "R13"
        self.output.write("@" + endframe + "\n")
        self.output.write("D=M\n")
        self.output.write("@" + str(index) + "\n")
        self.output.write("D=D-A\n")
        self.output.write("A=D\n")
        self.output.write("D=M\n")
        self.output.write("@" + segment + "\n")
        self.output.write("M=D\n")
