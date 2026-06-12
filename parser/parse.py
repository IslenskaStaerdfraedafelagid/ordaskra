import sys
from more_itertools import peekable
from .lex import TokenType
from .ast import *
from unidecode import unidecode

from .util import first_char


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

def maybe_add_subentry(ast, subentry):
    if subentry.translations != [] and not any(ast.exists(w.content) for w in subentry.synonyms):
        entry.subentries.append(subentry)

# Þetta eru global breytur sem eru notaðar til að smíða færslur yfir margar ítranir í innri lykkju parse()
entry = Entry()
subentry = SubEntry()
item = Item()

# Þáttarinn
def parse(tokens):
    global entry
    global subentry
    global item

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

                    # Gerum ekki greinarmun á stórum og litlum staf, miðum við lítinn staf
                    letter = first_char(string["content"]).lower()

                    ast.entries_by_letter[letter] = []
                # FL skipunin býr til nýja færslu í orðaskránni, held að það standi fyrir Foreign Language
                case TokenType.FL:
                    # Bætum við "undirfærslunni" í seinustu færslu á undan áður en við búum til nýja
                    maybe_add_subentry(ast, subentry)

                    # Hreinsum núverandi undirfærslu
                    subentry = SubEntry()

                    # TODO Fyrra skilyrðið er hakk til þess að koma í veg fyrir að tómu færslunni sem við byrjuðum með
                    # sé bætt inn í
                    if entry.word != "" and entry.subentries != []:
                        # Þetta er til þess að fjarlægja stafmerki þannig að orð eins og étale flokkist undir "e"
                        word = unidecode(entry.word)
                        letter = first_char(word).lower()

                        ast.entries_by_letter[letter].append(entry)

                    # Hreinsa núverandi færslu
                    entry = Entry()

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

                    item.content = string["content"]
                    item.type = ItemType.TY

                    subentry.translations.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # TYA skipunin býr til nýjan þýðingaflokk
                case TokenType.TYA:
                    maybe_add_subentry(ast, subentry)

                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.TY

                    subentry.translations.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # SH skipunin byr til samheiti
                case TokenType.SH:
                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
                    item.type = ItemType.SH

                    subentry.synonyms.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                # o.s.frv.
                case TokenType.SHA:
                    maybe_add_subentry(ast, subentry)

                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
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
                    maybe_add_subentry(ast, subentry)

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

                    item.content = string["content"]
                    item.type = ItemType.TV

                    subentry.related_words.append(item)

                    item = Item()

                    expect(it, TokenType.RBRACE)
                case TokenType.TVA:
                    maybe_add_subentry(ast, subentry)

                    subentry = SubEntry()

                    expect(it, TokenType.LBRACE)

                    string = next(it)
                    assert_type(string, TokenType.STR)

                    item.content = string["content"]
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

                    item.content = string["content"]
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

                    item.content = string["content"]
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