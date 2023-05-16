"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

NONE = "None"
INT_NONE = -1


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_symbols = dict()  # key - name , value - [type,kind,running_index]
        self.method_symbols = dict()
        self.class_ind = {"STATIC": 0, "FIELD": 0}
        self.method_ind = {"ARG": 0, "VAR": 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.method_symbols.clear()
        self.method_ind.update((ind, 0) for ind in self.method_ind)  # reset the index to 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind == "STATIC" or kind == "FIELD":
            running_index = self.class_ind[kind]
            self.class_symbols[name] = [type, kind, running_index]
            self.class_ind[kind] += 1
        else:
            running_index = self.method_ind[kind]
            self.method_symbols[name] = [type, kind, running_index]
            self.method_ind[kind] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind == "STATIC" or kind == "FIELD":
            return self.class_ind[kind]
        else:
            return self.method_ind[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        # Your code goes here!
        value = self.method_symbols.get(name)
        if value is None:
            value = self.class_symbols.get(name)
            if value is None:
                return NONE
        return value[1]  # the type

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # Your code goes here!
        value = self.method_symbols.get(name)
        if value is None:
            value = self.class_symbols.get(name)
            if value is None:
                return NONE
        return value[0]  # the type

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        # Your code goes here!
        value = self.method_symbols.get(name)
        if value is None:
            value = self.class_symbols.get(name)
            if value is None:
                return INT_NONE
        return value[2]  # the running index
