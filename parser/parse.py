import sys
from more_itertools import peekable
from .lex import TokenType
from .ast import *
from unidecode import unidecode

class ParseError(Exception):
    pass

def expect(it, token_type):
    lookahead = next(it)
    if lookahead["type"] != token_type:
        raise ParseError(lookahead["type"])

def assert_type(token, token_type):
    if token["type"] != token_type:
        raise ParseError(token["type"])

def zero_or_more(it, token):
    try:
        while it.peek()["type"] == token:
            next(it)
    except StopIteration:
        pass

entry = Entry()
subentry = SubEntry()
item = Item()

def first_char(string):
    i = 0

    while not string[i].isalpha():
        i += 1

    return string[i]

def parse(tokens):
    global entry
    global subentry
    global item

    it = peekable(tokens)

    ast = Ast()

    try:
        while it.peek(None):
            zero_or_more(it, TokenType.PER)
            expect(it, TokenType.BACK)

            lookahead = next(it)

            match lookahead["type"]:
                case TokenType.NS:
                    expect(it, TokenType.LBRACE)
                    string = next(it)
                    assert_type(string, TokenType.STR)
                    expect(it, TokenType.RBRACE)

                    letter = first_char(string["content"]).lower()

                    ast.entries_by_letter[letter] = []
                case TokenType.PER:
                    next(it)
                case TokenType.FL:
                    entry.subentries.append(subentry)
                    subentry = SubEntry()

                    # TODO
                    if entry.word != "":
                        word = unidecode(entry.word)
                        letter = first_char(word).lower()

                        ast.entries_by_letter[letter].append(entry)

                    entry = Entry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)
                    entry.word = string["content"]

                    expect(it, TokenType.RBRACE)
                case TokenType.TY:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.TY

                    subentry.translations.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.TYA:
                    entry.subentries.append(subentry)
                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.TY

                    subentry.translations.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.SH:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.SH

                    subentry.synonyms.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.SHA:
                    entry.subentries.append(subentry)
                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.SH

                    subentry.synonyms.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.CO:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.co = string["content"]

                    expect(it, TokenType.RBRACE)
                case TokenType.COA:
                    entry.subentries.append(subentry)
                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.co = string["content"]

                    expect(it, TokenType.RBRACE)
                case TokenType.TV:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.TV

                    subentry.related_words.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.TVA:
                    entry.subentries.append(subentry)
                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.TV

                    subentry.related_words.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.NA:
                    next(it)

                    entry.category = Category.NA
                case TokenType.LS:
                    next(it)

                    entry.category = Category.LS
                case TokenType.SAG:
                    next(it)

                    entry.category = Category.SAG
                case TokenType.SKA:
                    next(it)

                    entry.category = Category.SKA
                case TokenType.SAM:
                    next(it)

                    entry.category = Category.SAM
                case TokenType.INS:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.INS

                    subentry.inserts.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.AT:
                    next(it)

                    entry.category = Category.AT
                case TokenType.BIGINS:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.BIGINS

                    subentry.inserts.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.PL:
                    next(it)

                    entry.plural = True
                case TokenType.PREF:
                    next(it)

                    entry.category = Category.PREF
                case _:
                    raise ParseError(lookahead)
    except ParseError as e:
        # TODO
        sys.exit(f"Villa: {e}")

    #ast.entries_by_letter[0].pop(0)

    # TODO
    #for entry in entries:
    #    entry.subentries.pop(0)

    return ast