import sys
from enum import Enum
from more_itertools import peekable

class LexError(Exception):
    pass

class ParseError(Exception):
    pass

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

def lex(characters):
    tokens = []

    try:
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

                next(it)

                push_token(tokens, TokenType.STR, string)
                push_token(tokens, TokenType.RBRACE)
            else:
                match next(it):
                    case "\\":
                        push_token(tokens, TokenType.BACK)
                    case "%":
                        lookahead = next(it)

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
                    # TODO
                    case "i":
                        lookahead = next(it)

                        if lookahead == "n" and next(it) == "s" and next(it) == "{":
                            literal_mode = True

                            push_token(tokens, TokenType.INS)
                            push_token(tokens, TokenType.LBRACE)
                        else:
                            raise LexError(lookahead)
                    case "I":
                        lookahead = next(it)

                        if lookahead == "n" and next(it) == "s" and next(it) == "{":
                            literal_mode = True

                            push_token(tokens, TokenType.INS)
                            push_token(tokens, TokenType.LBRACE)
                        else:
                            raise LexError(lookahead)
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
                    case _:
                        raise LexError(next(it))
    except LexError as e:
        # TODO
        sys.exit(f"Villa: {e}")
    except IndexError:
        # TODO
        sys.exit("Villa")

    return tokens

def expect(it, token_type):
    if next(it)["type"] != token_type:
        raise ParseError(token_type)

def zero_or_more(it, token):
    try:
        while it.peek()["type"] == token:
            next(it)
    except StopIteration:
        pass

def parse(tokens):
    it = peekable(tokens)

    entries = []

    try:
        while it.peek(None):
            #print(it.peek(None))

            zero_or_more(it, TokenType.PER)
            expect(it, TokenType.BACK)

            lookahead = next(it)

            #print(lookahead)

            # TODO Para saman sviga og þýðingar/samheiti
            entry = {"word": "", "category": "", "synonyms": [], "translations": [], "related_words": []}

            match lookahead["type"]:
                case TokenType.NS:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.PER:
                    next(it)
                case TokenType.FL:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.TY:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.TYA:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.SH:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.SHA:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.CO:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.COA:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.TV:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.TVA:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.NA:
                    next(it)
                case TokenType.LS:
                    next(it)
                case TokenType.SAG:
                    next(it)
                case TokenType.SKA:
                    next(it)
                case TokenType.SAM:
                    next(it)
                case TokenType.INS:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.AT:
                    next(it)
                case TokenType.BIGINS:
                    expect(it, TokenType.LBRACE)
                    expect(it, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                case TokenType.PL:
                    next(it)
                case TokenType.PREF:
                    next(it)
                case _:
                    raise ParseError(next(it))
    except ParseError as e:
        # TODO
        sys.exit(f"Villa: {e}")

    return entries

if len(sys.argv) < 2:
    sys.exit("Notkun: python parse_tbx.py [skrá]")

path = sys.argv[1]

try:
    file = open(path, encoding="latin-1")

    characters = file.read()

    tokens = lex(characters)

    entries = parse(tokens)

    for entry in entries:
        print(entry)

except OSError:
    sys.exit(f"Villa: {path} fannst ekki")