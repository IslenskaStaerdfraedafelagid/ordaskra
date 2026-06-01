from enum import Enum

class ItemType(Enum):
    TY = 0
    SH = 1
    TV = 2
    INS = 3
    BIGINS = 4
    NONE = 5

    def __str__(self):
        match self:
            case ItemType.TY: return "ty"
            case ItemType.SH: return "sh"
            case ItemType.TV: return "tv"
            case ItemType.INS: return "ins"
            case ItemType.BIGINS: return "Ins"
            case _: return ""

class Category(Enum):
    NA = 0
    LS = 1
    SAG = 2
    SAM = 3
    AT = 4
    PREF = 5
    SKA = 6
    NONE = 7

    def __str__(self):
        match self:
            case Category.NA: return "na"
            case Category.LS: return "ls"
            case Category.SAG: return "sag"
            case Category.SAM: return "sam"
            case Category.AT: return "at"
            case Category.PREF: return "pref"
            case Category.SKA: return "ska"
            case _: return ""

class Item:
    def __init__(self):
        self.type = ItemType.NONE
        self.co = ""
        self.content = ""

    def to_str(self, a = False):
        string = ""

        if self.co != "":
            string += '\\co'

            if a:
                string += 'a'

            string += f'{{{self.co}}}%\n'

        string += f'\\{str(self.type)}{{{self.content}}}%\n'

        return string

    def __str__(self):
        return self.to_str()

class SubEntry:
    def __init__(self):
        self.translations = []
        self.synonyms = []
        self.related_words = []
        self.inserts = []

    def to_str(self, a = False):
        string = ""

        for translation in self.translations:
            string += translation.to_str(a)

        for insert in self.inserts:
            string += insert.to_str(a)

        for word in self.related_words:
            string += word.to_str(a)

        for synonym in self.synonyms:
            string += synonym.to_str(a)


        return string

    def __str__(self):
        return self.to_str()

class Entry:
    def __init__(self):
        self.word = ""
        self.category = Category.NONE
        self.subentries = []
        self.plural = False

    def __str__(self):
        string = f'\\fl{{{self.word}}}%\n'

        if self.category != Category.NONE:
            string += f'\\{str(self.category)}%\n'

        a = len(self.subentries) > 1

        for subentry in self.subentries:
            string += subentry.to_str(a)

        return string

class Ast:
    def __init__(self):
        self.entries_by_letter = {}

    def __str__(self):
        string = ""

        for char, entries in self.entries_by_letter.items():
            string += f'\\ns{{{char.upper()}}}%\n'

            for entry in entries:
                string += str(entry) + "%\n"

        return string