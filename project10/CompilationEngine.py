"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


# todo - complete tabs in the end

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    op = {'+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '='}
    unary_op = {'^', '#', '-', '~'}
    statements = {"let", "if", "do", "while", "return"}
    keyword_constant = {"true", "false", "that", "this"}

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.tokens = input_stream.get_tokens()
        self.output = output_stream
        self.cur_ind = 0
        self.cur_tabs = 0
        self.compile_class()

        # check what meant by start with compile_class

    def has_more(self):
        return self.cur_ind < len(self.tokens) - 1

    def advance(self):
        if self.cur_ind < len(self.tokens) - 1:
            self.cur_ind += 1

    def is_op(self):
        op = self.tokens[self.cur_ind].split()
        return op[1] in CompilationEngine.op

    def is_statement(self):
        token = self.tokens[self.cur_ind].split()
        if token[1] in CompilationEngine.statements:
            return token[1]
        return None

    def check(self, token):
        tok = self.tokens[self.cur_ind].split()
        return token == tok[1]

    def write_major_tag_open(self, tag):
        # complete tabs
        for i in range(self.cur_tabs):
            self.output.write("  ")
        self.output.write(f"<{tag}>\n")
        self.cur_tabs += 1

    def write_major_tag_close(self, tag):
        # complete tabs
        self.cur_tabs -= 1
        for i in range(self.cur_tabs):
            self.output.write("  ")
        self.output.write(f"</{tag}>\n")

    def add_to_file(self):
        for i in range(self.cur_tabs):
            self.output.write("  ")
        self.output.write(self.tokens[self.cur_ind] + "\n")
        self.advance()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.write_major_tag_open("class")
        self.add_to_file()  # add class
        self.add_to_file()  # add classname
        self.add_to_file()  # add {
        while self.check("static") or self.check("field"):
            self.compile_class_var_dec()
        while self.check("constructor") or self.check("function") or self.check("method"):
            self.compile_subroutine()
        self.add_to_file()  # add }
        self.write_major_tag_close("class")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.write_major_tag_open("classVarDec")
        self.add_to_file()  # add static|field
        self.add_to_file()  # add type
        self.add_to_file()  # add var_name
        while self.check(','):
            self.add_to_file()  # add ,
            self.add_to_file()  # add var_name
        self.add_to_file()  # add ;
        self.write_major_tag_close("classVarDec")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        self.write_major_tag_open("subroutineDec")
        self.add_to_file()  # add func type
        self.add_to_file()  # add type
        self.add_to_file()  # add subroutine_name
        self.add_to_file()  # add (
        self.compile_parameter_list()
        self.add_to_file()  # add )
        self.compile_subroutine_body()  # check
        self.write_major_tag_close("subroutineDec")

    def check_var_dec(self) -> bool:
        token = self.tokens[self.cur_ind].split()
        return token[1] == "var"

    def compile_subroutine_body(self) -> None:

        self.write_major_tag_open("subroutineBody")
        self.add_to_file()  # add {
        while self.check_var_dec():
            self.compile_var_dec()
        self.compile_statements()
        self.add_to_file()  # add }
        self.write_major_tag_close("subroutineBody")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        self.write_major_tag_open("parameterList")
        if not self.check(")"):
            self.add_to_file()  # add type
            self.add_to_file()  # add var name
            while self.check(","):
                self.add_to_file()  # add ,
                self.add_to_file()  # add type
                self.add_to_file()  # add var name
        self.write_major_tag_close("parameterList")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.write_major_tag_open("varDec")
        self.add_to_file()  # add var
        self.add_to_file()  # add type
        self.add_to_file()  # add var name
        while self.check(","):
            self.add_to_file()  # add ,
            self.add_to_file()  # var name
        self.add_to_file()  # add ;
        self.write_major_tag_close("varDec")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.write_major_tag_open("statements")
        statement = self.is_statement()
        while statement:
            if statement == "if":
                self.compile_if()
            elif statement == "do":
                self.compile_do()
            elif statement == "while":
                self.compile_while()
            elif statement == "let":
                self.compile_let()
            else:
                self.compile_return()
            statement = self.is_statement()
        self.write_major_tag_close("statements")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.write_major_tag_open("doStatement")
        self.add_to_file()  # add do
        self.compile_subroutine_call()
        self.add_to_file()  # add ;
        self.write_major_tag_close("doStatement")

    def compile_subroutine_call(self) -> None:
        self.add_to_file()  # add
        token = self.tokens[self.cur_ind].split()
        if token[1] == "(":
            self.add_to_file()  # add (
            self.compile_expression_list()
            self.add_to_file()  # add )
        else:
            self.add_to_file()  # add .
            self.add_to_file()  # sub_name
            self.add_to_file()  # add(
            self.compile_expression_list()
            self.add_to_file()  # add )

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.write_major_tag_open("letStatement")
        self.add_to_file()  # add let
        self.add_to_file()  # add varname
        if self.check('['):
            self.add_to_file()  # add [
            self.compile_expression()
            self.add_to_file()  # add ]
        self.add_to_file()  # add =
        self.compile_expression()
        self.add_to_file()  # add ;
        self.write_major_tag_close("letStatement")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.write_major_tag_open("whileStatement")
        self.add_to_file()  # add while
        self.add_to_file()  # add (
        self.compile_expression()
        self.add_to_file()  # add )
        self.add_to_file()  # add {
        self.compile_statements()
        self.add_to_file()  # add }
        self.write_major_tag_close("whileStatement")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.write_major_tag_open("returnStatement")
        self.add_to_file()  # add return
        if not self.check(";"):
            self.compile_expression()
        self.add_to_file()  # add ;
        self.write_major_tag_close("returnStatement")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.write_major_tag_open("ifStatement")
        self.add_to_file()  # add if to the file
        self.add_to_file()  # add (
        self.compile_expression()
        self.add_to_file()  # add )
        self.add_to_file()  # add {
        self.compile_statements()
        self.add_to_file()  # add }
        if self.check("else"):
            self.add_to_file()  # add else
            self.add_to_file()  # {
            self.compile_statements()
            self.add_to_file()  # add }
        self.write_major_tag_close("ifStatement")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.write_major_tag_open("expression")
        self.compile_term()
        while self.is_op():
            self.add_to_file()
            self.compile_term()
        self.write_major_tag_close("expression")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        self.write_major_tag_open("term")
        token = self.tokens[self.cur_ind].split()
        next_token = self.tokens[self.cur_ind + 1].split()
        if token[1] == "(":
            self.add_to_file()  # add (
            self.compile_expression()
            self.add_to_file()  # add )

        elif token[1] in CompilationEngine.unary_op:
            self.add_to_file()  # add unary
            # self.write_major_tag_open("term")
            self.compile_term()

        elif next_token[1] == "[":
            self.add_to_file()  # add var_name
            self.add_to_file()  # add (
            self.compile_expression()
            self.add_to_file()  # add )
        elif next_token[1] == "(":
            self.add_to_file()  # add var_name
            self.add_to_file()  # add (
            self.compile_expression_list()
            self.add_to_file()  # add )
        elif next_token[1] == ".":
            self.add_to_file()  # add class_name or var_name
            self.add_to_file()  # add .
            self.add_to_file()  # add subroutine_name
            self.add_to_file()  # add (
            self.compile_expression_list()
            self.add_to_file()  # add )

        else:
            self.add_to_file()  # add the integer or string or keyword
        self.write_major_tag_close("term")

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        self.write_major_tag_open("expressionList")
        if self.check_term():
            self.compile_expression()
            while self.check(","):
                self.add_to_file()  # add ,
                self.compile_expression()
        self.write_major_tag_close("expressionList")

    def check_term(self) -> bool:
        token = self.tokens[self.cur_ind].split()
        return token[0] == "<identifier>" or token[0] == "<integerConstant>" \
               or token[0] == "<stringConstant>" \
               or token[1] in CompilationEngine.keyword_constant \
               or token[1] in CompilationEngine.unary_op \
               or token[1] == "("
