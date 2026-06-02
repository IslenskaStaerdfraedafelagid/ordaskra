import sys
from enum import Enum
from more_itertools import peekable

class LexError(Exception):
    pass

# Sjá parse.py fyrir skýringar á þessum táknum
class TokenType(Enum):
    NS = 0
    PER = 1
    FL = 2
    TY = 3
    TYA = 4
    SH = 5
    SHA = 6
    CO = 7
    COA = 8
    TV = 9
    TVA = 10
    NA = 11
    LS = 12
    SAG = 13
    SKA = 14
    STR = 15
    BACK = 16
    LBRACE = 17
    RBRACE = 18
    SAM = 19
    INS = 20
    AT = 21
    BIGINS = 22
    PL = 23
    PREF = 24

EOF = "\0"

def push_token(tokens, type, string = ""):
    tokens.append({"type": type, "content": string})

# Breyir TeX kóða með dollaramerkjum í afturábak skástrik og sviga, $...$ -> \(...\)
def replace_dollars(string):
    i = string.find("$")
    new_string = ""

    if i != -1:
        new_string += string[:i]

        while i != -1:
            j = string.find("$", i)
            k = string.find("$", j + 1)

            if j != -1 and k != -1:
                new_string += string[i+1:j] + "\\(" + string[j+1:k] + "\\)"
                i = k + 1
            else:
                new_string += string[i:]
                i = -1
    else:
        new_string = string

    return new_string

# Þáttar orðaskránna í tákn sem er auðveldara að vinna með, bara einföld stöðuvél
def lex(characters):
    tokens = []

    try:
        # Notað til þess að lesa beint inn strengi í sér tákn
        literal_mode = False

        it = peekable(characters)

        while it.peek(EOF) != EOF:
            if literal_mode:
                literal_mode = False

                string = ""

                lookahead = next(it)

                while lookahead != "%":
                    string += lookahead
                    lookahead = next(it)

                if string[-1] != "}":
                    raise LexError(string[-1])

                # Hunsa dollaramerkið
                next(it)

                string = replace_dollars(string[:-1])

                push_token(tokens, TokenType.STR, string)
                push_token(tokens, TokenType.RBRACE)
            else:
                match next(it):
                    case "\\":
                        push_token(tokens, TokenType.BACK)
                    case "%":
                        lookahead = next(it)

                        # Hunsar komment
                        while lookahead != "\n":
                            lookahead = next(it)

                        push_token(tokens, TokenType.PER)
                    case "{":
                        literal_mode = True

                        push_token(tokens, TokenType.LBRACE)
                    case "}":
                        push_token(tokens, TokenType.RBRACE)
                    case "n":
                        lookahead = next(it)

                        match lookahead:
                            case "s":
                                push_token(tokens, TokenType.NS)
                            case "a":
                                push_token(tokens, TokenType.NA)
                            case _:
                                raise LexError(lookahead)
                    case "f":
                        lookahead = next(it)

                        if lookahead != "l":
                            raise LexError(lookahead)
                        else:
                            push_token(tokens, TokenType.FL)
                    case "s":
                        match next(it):
                            case "h":
                                if it.peek() == "a":
                                    next(it)

                                    push_token(tokens, TokenType.SHA)
                                else:
                                    push_token(tokens, TokenType.SH)
                            case "k":
                                lookahead = next(it)

                                if lookahead != "a":
                                    raise LexError(lookahead)
                                else:
                                    push_token(tokens, TokenType.SKA)
                            case "a":
                                lookahead = next(it)

                                match lookahead:
                                    case "g":
                                        push_token(tokens, TokenType.SAG)
                                    case "m":
                                        push_token(tokens, TokenType.SAM)
                                    case _:
                                        raise LexError(lookahead)
                            case _:
                                raise LexError(next(it))
                    case "t":
                        match next(it):
                            case "y":
                                if it.peek() == "a":
                                    next(it)

                                    push_token(tokens, TokenType.TYA)
                                else:
                                    push_token(tokens, TokenType.TY)
                            case "v":
                                if it.peek() == "a":
                                    next(it)

                                    push_token(tokens, TokenType.TVA)
                                else:
                                    push_token(tokens, TokenType.TV)
                    case "c":
                        lookahead = next(it)

                        if lookahead != "o":
                            raise LexError(lookahead)
                        else:
                            if it.peek() == "a":
                                next(it)

                                push_token(tokens, TokenType.COA)
                            else:
                                push_token(tokens, TokenType.CO)
                    case "l":
                        lookahead = next(it)

                        if lookahead != "s":
                            raise LexError(lookahead)
                        else:
                            push_token(tokens, TokenType.LS)
                    case "a":
                        lookahead = next(it)

                        if lookahead != "t":
                            raise LexError(lookahead)
                        else:
                            push_token(tokens, TokenType.AT)
                    case "p":
                        lookahead = next(it)

                        match lookahead:
                            case "l":
                                push_token(tokens, TokenType.PL)
                            case "r":
                                lookahead = next(it)

                                if lookahead == "e" and it.peek() == "f":
                                    next(it)

                                    push_token(tokens, TokenType.PREF)
                                else:
                                    raise LexError(lookahead)
                    case "\n":
                        push_token(tokens, TokenType.PER)
                    case c:
                        # Þetta er til þess að komast hjá því að endurtaka kóða í tveim greinum
                        if c == 'i' or c == 'I':
                            lookahead = next(it)
                            token_type = TokenType.INS if c == 'i' else TokenType.BIGINS

                            if lookahead == "n" and next(it) == "s" and next(it) == "{":
                                literal_mode = True

                                push_token(tokens, token_type)
                                push_token(tokens, TokenType.LBRACE)
                            else:
                                raise LexError(lookahead)
                        else:
                            raise LexError(next(it))
    except LexError as e:
        # TODO Betri villuboð
        sys.exit(f"Lexer villa: {e}")
    except IndexError:
        # TODO Betri villuboð
        sys.exit("Villa")

    return tokens