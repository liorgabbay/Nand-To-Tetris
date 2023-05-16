"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import re
import typing
import os


# check what to do with "
# check if i deal with string const right
# check if i need to move it to a file
# check file name
# check uses of the function we made in the API


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters,
    and comments, which are ignored. There are three possible comment formats:
    /* comment until closing */ , /** API comment until closing */ , and
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' |
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate
    file. A compilation unit is a single class. A class is a sequence of tokens
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type)
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement |
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className |
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    ## globals ##

    keyword_element = {'class': "CLASS", 'constructor': "CONSTRUCTOR", 'function': "FUNCTION", 'method': "METHOD",
                       'field': "FIELD",
                       'static': "STATIC", 'var': "VAR", 'int': "INT", 'char': "CHAR", 'boolean': "BOOLEAN",
                       'void': "VOID",
                       'true': "TRUE",
                       'false': "FALSE", 'null': "NULL", 'this': "THIS", 'let': "LET", 'do': "DO", 'if': "IF",
                       'else': "ELSE",
                       'while': "WHILE", 'return': "RETURN"}

    symbol_element = {'{': '{', '}': '}', '(': '(', ')': ')', '[': '[', ']': ']', '.': '.', ',': ',', ';': ';',
                      '+': '+',
                      '-': '-', '*': '*', '/': '/', '&': '&amp;', '|': '|', '<': '&lt;', '>': '&gt;', '=': '=',
                      '~': '~',
                      '^': '^', '#': '#'}

    digit_limit = {"max": 32767, "min": 0}
    to_write = "<#> * </#>"
    name_symbol = "symbol"
    name_keyword = "keyword"
    name_int = "integerConstant"
    name_string = "stringConstant"
    name_identifier = "identifier"

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()
        self.input = input_stream
        self.input_lines = input_stream.read().splitlines()
        self.input_lines = [self._remove_inline_comment(line) for line in
                            self.input_lines]
        self.remove_block()
        self.input_lines = [com.strip() for com in self.input_lines]  # delete space at the begin and the end
        self.input_lines = [com for com in self.input_lines if com != ""]

        self.cur_line = self.input_lines[0]
        self.cur_ind_line = 0
        self.cur_ind_let = 0
        self.cur_token = ""
        self.find_cur_token()



    def remove_block(self):
        arr = []
        in_comment = False
        in_string = False

        for string in self.input_lines:
            modified_string = ""
            words = re.split(r'(?<!\s) ', string)

            for word in words:

                if "/*" in word and not in_string:
                    in_comment = True
                    if not in_string and len(word) != 2:
                        index = word.index("/*")
                        modified_string += " " + word[:index]
                    continue

                if "*/" in word and not in_string:
                    in_comment = False
                    if not in_string and len(word) != 2:
                        index = word.index("*/")
                        modified_string += " " + word[index + 2:]
                    continue

                if "\"" in word and not in_comment:
                    in_string = not in_string
                    if word.count("\"") % 2 == 0:
                        in_string = not in_string

                if not in_comment or in_string:
                    modified_string += " " + word

            arr.append(modified_string)

        self.input_lines = arr

    def _remove_inline_comment(self, line):
        in_quotes = False

        result = ""

        for i in range(len(line)):
            if line[i] == '"':
                in_quotes = not in_quotes
                result += line[i]

            elif i <= len(line) - 2 and line[i] == '/' and \
                    line[i + 1] == '/' and not in_quotes:
                return result

            else:
                result += line[i]

        return result

    def get_tokens(self) -> list:
        tokens = list()
        while self.has_more_tokens():
            token = JackTokenizer.to_write.replace('#', self.type())
            if self.token_type() == "STRING_CONST":
                token = token.replace('*', self.string_val())
            elif self.token_type() == "SYMBOL":
                token = token.replace('*', self.symbol())
            else:
                token = token.replace('*', self.cur_token)
            tokens.append(token)
            self.advance()
        return tokens

    def type(self):

        if self.cur_token in JackTokenizer.symbol_element:
            return JackTokenizer.name_symbol
        if self.cur_token in JackTokenizer.keyword_element:
            return JackTokenizer.name_keyword
        if self.cur_token.isdecimal() and JackTokenizer.digit_limit["max"] >= int(self.cur_token) >= \
                JackTokenizer.digit_limit["min"]:
            return JackTokenizer.name_int
        if self.cur_token[0] == '"' and self.cur_token[-1] == '"' and len(
                self.cur_token) > 2 and self.cur_token != "\n":
            return JackTokenizer.name_string
        if not self.cur_token[0].isdigit():
            return JackTokenizer.name_identifier

    def find_cur_token(self):
        token = ""
        if self.cur_line[self.cur_ind_let] in JackTokenizer.symbol_element:
            self.cur_token = self.cur_line[self.cur_ind_let]
            self.cur_ind_let += 1
            return
        ###### check if I handle it wall ######
        if self.cur_line[self.cur_ind_let] == '"':
            token += self.cur_line[self.cur_ind_let]
            self.cur_ind_let += 1
            while self.cur_line[self.cur_ind_let] != '"':
                token += self.cur_line[self.cur_ind_let]
                self.cur_ind_let += 1
            token += self.cur_line[self.cur_ind_let]
            self.cur_ind_let += 1
            self.cur_token = token
            return
        ########################################
        for i in range(self.cur_ind_let, len(self.cur_line)):
            if not self.cur_line[i].isspace() and self.cur_line[i] not in JackTokenizer.symbol_element:
                token += self.cur_line[i]
            else:
                self.cur_token = token
                self.cur_ind_let = i
                return
        self.cur_token = token
        self.cur_ind_let = len(self.cur_line)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.cur_ind_line < len(self.input_lines) or self.cur_ind_let < len(self.cur_line)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        if self.cur_ind_let == len(self.cur_line):
            self.cur_ind_line += 1
            self.cur_ind_let = 0
        if self.cur_ind_line < len(self.input_lines):
            self.cur_line = self.input_lines[self.cur_ind_line]
        if self.has_more_tokens():
            while self.cur_line[self.cur_ind_let].isspace():
                self.cur_ind_let += 1
            self.find_cur_token()

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_token in JackTokenizer.symbol_element:
            return "SYMBOL"
        if self.cur_token in JackTokenizer.keyword_element:
            return "KEYWORD"
        if self.cur_token.isdecimal() and JackTokenizer.digit_limit["max"] >= int(self.cur_token) >= \
                JackTokenizer.digit_limit["min"]:
            return "INT_CONST"
        if self.cur_token[0] == '"' and self.cur_token[-1] == '"' and len(
                self.cur_token) > 2 and self.cur_token != "\n":
            return "STRING_CONST"
        if not self.cur_token[0].isdigit():
            return "IDENTIFIER"

        # todo - check if no ok

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return JackTokenizer.keyword_element[self.cur_token]

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return JackTokenizer.symbol_element[self.cur_token]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.cur_token[1:-1]
