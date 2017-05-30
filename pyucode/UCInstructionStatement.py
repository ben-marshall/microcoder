
"""
A set of classes for representing the operations which occur inside of
instructions.
"""

import logging as log

import ply.lex as lex

class UCInstructionStatement(object):
    """
    Describes a *single* statement within an instruction. A statement
    consists of a single assignment to a variable.

    An EBNF grammar for statements would be:

    ```
    statement ::= <variable> = <expression> \n

    variable  ::= (a-bA-B0-9_)+

    constant  ::= (0-9)*'[h](0-9a-fA-F)+
                | (0-9)*'[d](0-9)+
                | (0-9)*'[b](0-1)+
                | (0-9)*'[o](0-7)+
                | (0-9)+

    expression ::= <term> <infix_op> <term>
                 | <prefix_op> <term>
                 | <term>

    term       ::= <constant>
                 | <variable>
                 | ( <expression> )
                 | { <expression> <concatenation> }
                 | { <constant> { expression } }

    concatenation ::= , <expression> <concatenation>
                    |

    infix_op   ::= + \| - | & ^ * && \|\| << >> <<< >>> > < == >= <=

    prefix_op  ::= - \| &
    ```

    Note that operator precedence is left un-defined. The **only** way to
    express precedence is to use brackets.
    """

    def __init__(self, src=None, lineNo = 0):
        """
        Create a new instruction behaviour statement using a string source.
        """
        assert type(src) == str , \
            "src should be of type str, not %s" % type(src)
        assert type(lineNo) == int , \
            "lineNo should be of type int, not %s" % type(lineNo)

        self.src = src
        self.parse()

    def get_tokens(self):
        """
        Return a string tokenised version of the sourcefor this statement.
        """
        return self.src.split(" ")

    def parse(self):
        """
        Parse the string representation of the statement 
        """
        
