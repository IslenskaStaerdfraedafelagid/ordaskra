import sys

from more_itertools import peekable

from .ast import *
from .lex import TokenType


class ParseError(Exception):
    pass


###############################################################
#### Frekar hefðbundinn þáttari fyrir sniðið á orðaskránni ####
###############################################################

# Tryggir það að tákn sé af viðbúnu tagi
def assert_type(token, token_type):
    if token["type"] != token_type:
        raise ParseError(token["type"])


# Hunsar næsta tákn og tryggir að tagið á því sé rétt
def expect(it, token_type):
    lookahead = next(it)
    assert_type(lookahead, token_type)


# Hunsar núll eða fleiri tákn af sama tagi
def zero_or_more(it, token):
    try:
        while it.peek()["type"] == token:
            next(it)
    except StopIteration:
        pass


def extract_references(string):
    new_string = string

    if string[-1].isdigit():
        i = string.rfind('~')

        if i != -1:
            new_string = new_string.replace('~', ' ')

        i = new_string.rfind(' ')

        return string[:i], int(string[i + 1:])
    else:
        return string, 0


# Þetta eru global breytur sem eru notaðar til að smíða færslur yfir margar ítranir í innri lykkju parse()
entry = Entry()
subentry = SubEntry()
item = Item()
entry_idx = 0


def maybe_add_subentry(subentry):
    global entry_idx

    # TODO Ljót lausn
    if subentry.translations != [] or subentry.synonyms != [] or subentry.related_words != []:
        entry_idx += 1

    if subentry.translations != []:
        subentry.idx = entry_idx
        entry.subentries.append(subentry)

# Þáttarinn
def parse(tokens):
    global entry
    global subentry
    global item
    global entry_idx

    it = peekable(tokens)

    ast = Ast()

    try:
        while it.peek(None):
            # Okkur er alveg sama um prósentumerki milli skipana þannig við hendum þeim bara út
            zero_or_more(it, TokenType.PER)
            # Síðan búumst við við því að sjá \ til þess að byrja nýja skipun
            expect(it, TokenType.BACK)

            lookahead = next(it)

            match lookahead["type"]:
                # NS skipunin býr til nýjan flokk orða sem byrja á sama staf
                case TokenType.NS:
                    expect(it, TokenType.LBRACE)
                    string = next(it)
                    assert_type(string, TokenType.STR)
                    expect(it, TokenType.RBRACE)
                # FL skipunin býr til nýja færslu í orðaskránni, held að það standi fyrir Foreign Language
                case TokenType.FL:
                    # Bætum við "undirfærslunni" í seinustu færslu á undan áður en við búum til nýja
                    maybe_add_subentry(subentry)

                    # Hreinsum núverandi undirfærslu
                    subentry = SubEntry()

                    # TODO Fyrra skilyrðið er hakk til þess að koma í veg fyrir að tómu færslunni sem við byrjuðum með
                    # sé bætt inn í
                    if entry.word != "" and entry.subentries != []:
                        ast.add_entry(entry)

                    # Hreinsa núverandi færslu
                    entry = Entry()
                    entry_idx = 0

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)
                    entry.word = string["content"]

                    expect(it, TokenType.RBRACE)
                # TY skipunin býr til nýja þýðingu
                case TokenType.TY:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content, item.idx = extract_references(string["content"])
                    item.type = ItemType.TY

                    subentry.translations.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # TYA skipunin býr til nýjan þýðingaflokk
                case TokenType.TYA:
                    maybe_add_subentry(subentry)

                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content, item.idx = extract_references(string["content"])
                    item.type = ItemType.TY

                    subentry.translations.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # SH skipunin byr til samheiti
                case TokenType.SH:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content, item.idx = extract_references(string["content"])
                    item.type = ItemType.SH

                    subentry.synonyms.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # o.s.frv.
                case TokenType.SHA:
                    maybe_add_subentry(subentry)

                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content, item.idx = extract_references(string["content"])
                    item.type = ItemType.SH

                    subentry.synonyms.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # CO skipunin býr til skýringu innan sviga
                case TokenType.CO:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.co = string["content"]

                    expect(it, TokenType.RBRACE)
                case TokenType.COA:
                    maybe_add_subentry(subentry)

                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.co = string["content"]

                    expect(it, TokenType.RBRACE)
                # TV skipunin býr til skylt orð
                case TokenType.TV:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content, item.idx = extract_references(string["content"])
                    item.type = ItemType.TV

                    subentry.related_words.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.TVA:
                    maybe_add_subentry(subentry)

                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content, item.idx = extract_references(string["content"])
                    item.type = ItemType.TV

                    subentry.related_words.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # NA skipunin býr til nafnorð
                case TokenType.NA:
                    next(it)

                    entry.category = Category.NA
                # LS skipunin býr til lýsingarorð
                case TokenType.LS:
                    next(it)

                    entry.category = Category.LS
                # SAG skipunin býr til sagnorð
                case TokenType.SAG:
                    next(it)

                    entry.category = Category.SAG
                # SKA skipunin býr til skammstöfun
                case TokenType.SKA:
                    next(it)

                    entry.category = Category.SKA
                # SAM skipunin býr til samtengingu
                case TokenType.SAM:
                    next(it)

                    entry.category = Category.SAM
                # INS skipunin setur inn skýringu inn í hornklofum
                case TokenType.INS:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content, item.idx = extract_references(string["content"])
                    item.type = ItemType.INS

                    subentry.inserts.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # AT skipunin býr til atviksorð
                case TokenType.AT:
                    next(it)

                    entry.category = Category.AT
                # INS skipunin (með stóru I-i) býr til skýringu á nýrri línu
                case TokenType.BIGINS:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content, item.idx = extract_references(string["content"])
                    item.type = ItemType.BIGINS

                    subentry.inserts.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # PL skipunin býr til fleirtöluorð
                case TokenType.PL:
                    next(it)

                    entry.plural = True
                # PREF skipunin býr til forskeyti
                case TokenType.PREF:
                    next(it)

                    entry.category = Category.PREF
                case _:
                    raise ParseError(lookahead)
    except ParseError as e:
        # TODO Betri villuboð
        sys.exit(f"Parser villa: {e}")

    return ast
