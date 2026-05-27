import sys
from enum import Enum

class LexError(Exception):
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
    NONE = 25

def lex(characters):
    tokens = []

    try:
        token = {"type": TokenType.NONE, "content": ""}

        i = 0
        line = 1

        literal_mode = False

        while i < len(characters):
            if literal_mode:
                token["type"] = TokenType.STR
                string = ""

                while characters[i+1] != "%":
                    string += (characters[i])
                    i += 1

                i += 1

                token["content"] = string
                tokens.append(token)
                print(token)

                token["type"] = TokenType.RBRACE
                token["content"] = ""
                tokens.append(token)

                token["type"] = TokenType.NONE
                literal_mode = False
                continue

            match characters[i]:
                case "\\":
                    token["type"] = TokenType.BACK
                case "%":
                    i += 1
                    line += 1

                    while characters[i] != "\n":
                        i += 1

                    token["type"] = TokenType.PER
                case "{":
                    token["type"] = TokenType.LBRACE

                    literal_mode = True
                case "}":
                    token["type"] = TokenType.RBRACE
                case "n":
                    i += 1

                    match characters[i]:
                        case "s":
                            token["type"] = TokenType.NS
                        case "a":
                            token["type"] = TokenType.NA
                        case _:
                            raise LexError(characters[i])
                case "f":
                    i += 1

                    if characters[i] != "l":
                        raise LexError(characters[i])
                    else:
                        token["type"] = TokenType.FL
                case "s":
                    i += 1

                    match characters[i]:
                        case "h":
                            if characters[i+1] == "a":
                                i += 1

                                token["type"] = TokenType.SHA
                            else:
                                token["type"] = TokenType.SH
                        case "k":
                            i += 1

                            if characters[i] != "a":
                                raise LexError(characters[i])
                            else:
                                token["type"] = TokenType.SKA
                        case "a":
                            i += 1

                            match characters[i]:
                                case "g":
                                    token["type"] = TokenType.SAG
                                case "m":
                                    token["type"] = TokenType.SAM
                                case _:
                                    raise LexError(characters[i])
                        case _:
                            raise LexError(characters[i])
                case "t":
                    i += 1

                    match characters[i]:
                        case "y":
                            if characters[i+1] == "a":
                                i += 1

                                token["type"] = TokenType.TYA
                            else:
                                token["type"] = TokenType.TY
                        case "v":
                            if characters[i + 1] == "a":
                                i += 1

                                token["type"] = TokenType.TVA
                            else:
                                token["type"] = TokenType.TV
                case "c":
                    i += 1

                    if characters[i] != "o":
                        raise LexError(characters[i])
                    else:
                        if characters[i + 1] == "a":
                            i += 1

                            token["type"] = TokenType.COA
                        else:
                            token["type"] = TokenType.CO
                case "l":
                    i += 1

                    if characters[i] != "s":
                        raise LexError(characters[i])
                    else:
                        token["type"] = TokenType.LS
                # TODO
                case "i":
                    i += 1

                    if characters[i] == "n" and characters[i+1] == "s" and characters[i+2] == "{":
                        i += 2

                        token["type"] = TokenType.INS
                        tokens.append(token)

                        token["type"] = TokenType.LBRACE
                        tokens.append(token)

                        literal_mode = True
                    else:
                        raise LexError(characters[i])
                case "I":
                    i += 1

                    if characters[i] == "n" and characters[i+1] == "s" and characters[i+2] == "{":
                        i += 2

                        token["type"] = TokenType.BIGINS
                        tokens.append(token)

                        token["type"] = TokenType.LBRACE
                        tokens.append(token)

                        literal_mode = True
                    else:
                        raise LexError(characters[i])
                case "a":
                    i += 1

                    if characters[i] != "t":
                        raise LexError(characters[i])
                    else:
                        token["type"] = TokenType.AT
                case "p":
                    i += 1

                    match characters[i]:
                        case "l":
                            token["type"] = TokenType.PL
                        case "r":
                            i += 1

                            if characters[i] == "e" and characters[i+1] == "f":
                                i += 1

                                token["type"] = TokenType.PREF
                            else:
                                raise LexError(characters[i])
                case "\n":
                    line += 1

                    token["type"] = TokenType.PER
                case _:
                    raise LexError(characters[i])

            tokens.append(token)
            print(token)

            token = {"type": TokenType.NONE, "content": ""}
            i += 1
    except LexError as e:
        sys.exit(f"Villa: {e}")
    except IndexError:
        sys.exit("Villa")

    return tokens

def parse(tokens):
    i = 0

    while i < len(tokens):
        # TODO Para saman sviga og þýðingar/samheiti
        entry = {"word": "", "category": "", "synonyms": [], "translations": [], "related_words": []}

        i += 1

    return []

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