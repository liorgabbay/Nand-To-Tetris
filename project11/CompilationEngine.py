"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:

    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """
    op = {'+': "ADD", '-': "SUB", '*': "MULT", '/': "DIVIDE", '&amp;': "AND", '|': "OR", '&lt;': "LT", '&gt;': "GT",
          '=': "EQ"}
    unary_op = {'#': "SHIFTRIGHT", '^': "SHIFTLEFT", '-': "NEG", '~': "NOT"}
    statements = {"let", "if", "do", "while", "return"}
    keyword_constant = {"true", "false", "that", "this"}
    kind = {"VAR": "LOCAL", "ARG": "ARGUMENT", "FIELD": "THIS", "STATIC": "STATIC"}

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
        self.writer = VMWriter(output_stream)
        self.cur_ind = 0
        self.symbol_table = SymbolTable()
        self.label_counter = 0
        self.class_name = ""
        self.class_field_ind = 0
        self.function_name = ""
        self.function_arg = 0
        self.function_kind = ""
        self.expression_ind = 0
        self.function_type = ""
        self.local_id = 0
        self.compile_class()

    ################################ helper for 11 ####################################

    def advance(self):
        if self.cur_ind < len(self.tokens) - 1:
            self.cur_ind += 1

    def make_unique_label(self, label):
        return_label = self.class_name + "." + label + "#" + str(self.label_counter)
        self.label_counter += 1
        return return_label

    def check(self, token):
        tok = self.tokens[self.cur_ind].split()
        return token == tok[1]

    def get_next(self):
        return self.tokens[self.cur_ind + 1].split()[1]

    def eat_identifier(self) -> str:
        identifier = self.tokens[self.cur_ind].split()[1]
        self.advance()
        return identifier

    def eat_symbol(self) -> str:
        symbol = self.tokens[self.cur_ind].split()
        symbol = symbol[1]
        self.advance()
        return symbol

    def eat_keyword(self) -> str:
        keyword = self.tokens[self.cur_ind].split()
        keyword = keyword[1]
        self.advance()
        return keyword

    def eat_var(self) -> str:
        var = self.tokens[self.cur_ind].split()
        if var[0] == "<stringConstant>":
            var = self.tokens[self.cur_ind][17:-18]
        else:
            var = var[1]
        self.advance()
        return var

    def handle_arr(self, var_kind, var_index):
        self.eat_symbol()  # add [
        self.writer.write_push(CompilationEngine.kind[var_kind], var_index)  # push arr
        self.compile_expression()  # compile expression with in []
        self.writer.write_arithmetic("ADD")  # compile add
        self.eat_symbol()  # add ]

    def check_term(self) -> bool:
        token = self.tokens[self.cur_ind].split()
        return token[0] == "<identifier>" or token[0] == "<integerConstant>" \
               or token[0] == "<stringConstant>" \
               or token[1] in CompilationEngine.keyword_constant \
               or token[1] in CompilationEngine.unary_op \
               or token[1] == "("

    def check_var_dec(self) -> bool:
        token = self.tokens[self.cur_ind].split()
        return token[1] == "var"

    def compile_constructor(self) -> None:
        self.writer.write_push("CONSTANT", self.class_field_ind)  # save place for the class var
        self.writer.write_call("Memory.alloc", 1)
        self.writer.write_pop("POINTER", 0)

    def is_statement(self):
        token = self.tokens[self.cur_ind].split()
        if token[1] in CompilationEngine.statements:
            return token[1]
        return None

    def is_op(self):
        op = self.tokens[self.cur_ind].split()
        return op[1] in CompilationEngine.op

    def get_into_field(self):
        self.writer.write_push("ARGUMENT", 0)
        self.writer.write_pop("POINTER", 0)

    def handle_string(self, word):
        self.writer.write_push("CONSTANT", len(word))
        self.writer.write_call("String.new", 1)
        for let in word:
            self.writer.write_push("CONSTANT", ord(let))
            self.writer.write_call("String.appendChar", 2)

    #####################################################################################

    # DONE
    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.eat_identifier()  # add class
        self.class_name = self.eat_identifier()  # save classname
        self.eat_symbol()  # add {
        while self.check("static") or self.check("field"):
            self.compile_class_var_dec()
        while self.check("constructor") or self.check("function") or self.check("method"):
            self.compile_subroutine()
        self.eat_symbol()  # add }

    # DONE
    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""

        var_kind = self.eat_identifier().upper()  # add static|field and change it to upper case
        var_type = self.eat_identifier()
        var_name = self.eat_var()
        if var_kind == "FIELD":
            self.class_field_ind += 1
        self.symbol_table.define(var_name, var_type, var_kind)
        while self.check(','):
            self.eat_symbol()  # add ,
            var_name = self.eat_var()  # save var name
            if var_kind == "FIELD":
                self.class_field_ind += 1
            self.symbol_table.define(var_name, var_type, var_kind)
        self.eat_symbol()  # add ;

    # DONE
    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        func_kind = self.eat_identifier()  # save func_kind
        self.function_kind = func_kind
        self.function_type = self.eat_identifier()  # save func_type
        self.function_name = self.eat_identifier()  # save_func_name
        self.symbol_table.start_subroutine()
        self.eat_symbol()  # add (
        self.compile_parameter_list()
        self.eat_symbol()  # add )
        self.function_arg = 0
        self.compile_subroutine_body()

    # DONE
    def compile_subroutine_body(self) -> None:
        self.eat_symbol()  # add {
        while self.check_var_dec():
            self.compile_var_dec()
        self.writer.write_function(self.class_name + "." + self.function_name, self.local_id)
        self.local_id = 0
        if self.function_kind == "constructor":
            self.compile_constructor()
        if self.function_kind == "method":
            self.get_into_field()
        self.compile_statements()
        self.eat_symbol()  # add }

    # DONE
    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        # Your code goes here!
        if self.function_kind == "method":
            self.symbol_table.define("this", self.class_name, "ARG")
        if not self.check(")"):
            arg_type = self.eat_identifier()  # save var type
            arg_name = self.eat_var()  # save var_name
            self.symbol_table.define(arg_name, arg_type, "ARG")
            self.function_arg += 1
            while self.check(","):
                self.eat_symbol()  # add ,
                arg_type = self.eat_identifier()  # save var type
                arg_name = self.eat_var()  # save var_name
                self.symbol_table.define(arg_name, arg_type, "ARG")
                self.function_arg += 1

    # DONE
    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.eat_identifier()  # add var
        var_type = self.eat_identifier()  # save var type
        var_name = self.eat_var()  # save var_name
        self.symbol_table.define(var_name, var_type, "VAR")
        self.local_id += 1
        while self.check(","):
            self.eat_symbol()  # add ,
            var_name = self.eat_var()  # save var_name
            self.symbol_table.define(var_name, var_type, "VAR")
            self.local_id += 1
        self.eat_symbol()  # add ;

    # DONE
    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
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
                if self.function_kind == "constructor":
                    self.writer.write_push("POINTER", 0)
                self.compile_return()
            statement = self.is_statement()

    # DONE
    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!

        self.eat_identifier()  # add do
        self.compile_expression()
        self.writer.write_pop("TEMP", 0)
        self.eat_symbol()  # add ;

    # DONE
    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.eat_identifier()  # add let
        var_name = self.eat_var()  # add varname
        var_kind = self.symbol_table.kind_of(var_name)
        var_index = self.symbol_table.index_of(var_name)

        if self.check('['):
            self.handle_arr(var_kind, var_index)
            self.eat_symbol()  # add =
            self.compile_expression()  # compile expression 2
            self.writer.write_pop("TEMP", 0)
            self.writer.write_pop("POINTER", 1)
            self.writer.write_push("TEMP", 0)
            self.writer.write_pop("THAT", 0)
            self.eat_symbol()  # add;
        else:
            self.eat_symbol()  # add =
            self.compile_expression()
            # print(self.function_kind, var_name)
            self.writer.write_pop(CompilationEngine.kind[var_kind], var_index)
            self.eat_symbol()  # add;

    # DONE
    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.eat_keyword()  # add while
        start_while = self.make_unique_label("START_WHILE")
        end_while = self.make_unique_label("END_WHILE")
        self.writer.write_label(start_while)
        self.eat_symbol()  # add (
        self.compile_expression()
        self.writer.write_arithmetic("NOT")
        self.eat_symbol()  # add )
        self.writer.write_if(end_while)
        self.eat_symbol()  # add {
        self.compile_statements()
        self.eat_symbol()  # add }
        self.writer.write_goto(start_while)
        self.writer.write_label(end_while)

    # DONE
    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.eat_keyword()  # add return
        if not self.check(";"):
            self.compile_expression()
        else:
            self.writer.write_push("CONSTANT", 0)
        self.writer.write_return()
        self.eat_symbol()  # add ;

    # DONE
    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.eat_keyword()  # add if
        self.eat_symbol()  # add (
        self.compile_expression()
        self.writer.write_arithmetic("NOT")
        self.eat_symbol()  # add )
        if_label = self.make_unique_label("IF")
        self.writer.write_if(if_label)
        self.eat_symbol()  # add {
        self.compile_statements()
        self.eat_symbol()  # add }
        if self.check("else"):
            else_label = self.make_unique_label("ELSE")
            self.writer.write_goto(else_label)
            self.eat_symbol()  # add else
            self.writer.write_label(if_label)
            self.eat_symbol()  # {
            self.compile_statements()
            self.eat_symbol()  # add }
            self.writer.write_label(else_label)

        else:
            self.writer.write_label(if_label)

    # DONE
    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        self.compile_term()
        while self.is_op():
            op = self.eat_symbol()
            self.compile_term()
            if op not in ["*", "/"]:
                self.writer.write_arithmetic(CompilationEngine.op[op])
            else:
                if op == "*":
                    self.writer.write_call("Math.multiply", 2)
                else:
                    self.writer.write_call("Math.divide", 2)

    # DONE
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
        expression_ind = 0
        token = self.tokens[self.cur_ind].split()
        next_token = self.tokens[self.cur_ind + 1].split()
        if token[1] == "(":
            self.eat_symbol()  # add (
            self.compile_expression()
            self.eat_symbol()  # add )

        elif token[1] in CompilationEngine.unary_op:
            unary_op = self.eat_symbol()  # add unary
            self.compile_term()
            self.writer.write_arithmetic(CompilationEngine.unary_op[unary_op])

        elif next_token[1] == "[":
            arr_name = self.eat_identifier()
            arr_kind = self.symbol_table.kind_of(arr_name)
            arr_index = self.symbol_table.index_of(arr_name)
            self.handle_arr(arr_kind, arr_index)
            self.writer.write_pop("POINTER", 1)
            self.writer.write_push("THAT", 0)

        elif next_token[1] == "(":
            func = self.eat_identifier()
            self.eat_symbol()  # add (
            self.writer.write_push("POINTER", 0)
            self.compile_expression_list()
            self.eat_symbol()  # add )
            expression_ind = self.expression_ind
            self.expression_ind = 0
            self.writer.write_call(self.class_name + "." + func, expression_ind + 1)


        # continue from here
        elif next_token[1] == ".":
            var = self.eat_identifier()
            self.eat_symbol()  # add "."
            subroutine_name = self.eat_identifier()  # save the function name
            self.eat_symbol()  # eat (
            if var + "." + subroutine_name == self.class_name + ".new":  # call to the constructor
                self.compile_expression_list()
                expression_ind = self.expression_ind
                self.expression_ind = 0
                self.writer.write_call(f"{self.class_name}.new", expression_ind)

            else:
                var_kind = self.symbol_table.kind_of(var)
                var_type = self.symbol_table.type_of(var)
                if var_kind != "None":
                    subroutine_name = var_type + "." + subroutine_name
                    var_index = self.symbol_table.index_of(var)
                    self.writer.write_push(CompilationEngine.kind[var_kind], var_index)
                    expression_ind += 1
                else:
                    subroutine_name = var + "." + subroutine_name
                self.compile_expression_list()
                expression_ind += self.expression_ind
                self.expression_ind = 0
                self.writer.write_call(subroutine_name, expression_ind)
            self.eat_symbol()  # eat )

        # need to take care if is not a number like var or something else
        else:
            if token[0] == "<stringConstant>":
                var = self.eat_var()
                self.handle_string(var)
                return
            var = self.eat_var()
            if var.isdecimal():
                self.writer.write_push("constant", int(var))
            else:
                var_kind = self.symbol_table.kind_of(var)
                if var_kind == "None":
                    if var == "true":
                        self.writer.write_push("constant", 1)
                        self.writer.write_arithmetic("NEG")
                    if var == "false" or var == "null":
                        self.writer.write_push("constant", 0)
                else:
                    var_index = self.symbol_table.index_of(var)
                    self.writer.write_push(CompilationEngine.kind[var_kind], var_index)

    # DONE
    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        expression_ind = 0
        if self.check_term():
            expression_ind += 1
            self.compile_expression()
            while self.check(","):
                self.eat_symbol()  # add ,
                expression_ind += 1
                self.compile_expression()
        self.expression_ind = expression_ind
