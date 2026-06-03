from enum import Enum

#SEP = chr(31)
SEP = '|'

# Sjá parse.py fyrir skýringar á þessum táknum
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

# Sjá parse.py fyrir skýringar á þessum táknum
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
        suffix = 'a' if a else ''
        if self.co != "":
            return f'\\co{suffix}{{{self.co}}}%\n\\{str(self.type)}{{{self.content}}}%\n'
        else:
            return f'\\{str(self.type)}{suffix}{{{self.content}}}%\n'

    def __str__(self):
        return self.to_str()

def to_comma_separated(items):
    string = ""

    if len(items) > 0:
        first = items[0]

        if first.co != "":
            string += f'({first.co}) '

        string += f'{first.content}'

        for item in items[1:]:
            string += ', '

            if item.co != "":
                string += f'({item.co}) '

            string += f'{item.content}'

    return string


class SubEntry:
    def __init__(self):
        self.translations = []
        self.synonyms = []
        self.related_words = []
        self.inserts = []

    def to_str(self, a = False):
        string = ""

        # Þetta er til þess að það sé ekki verið að búa til margar undirfærslur
        done = False

        for i, translation in enumerate(self.translations):
            string += translation.to_str(not done)
            done = True

        for insert in self.inserts:
            string += insert.to_str(False)

        for i, word in enumerate(self.related_words):
            string += word.to_str(not done)
            done = True

        for i, synonym in enumerate(self.synonyms):
            string += synonym.to_str(not done)

        return string

    def __str__(self):
        return self.to_str()

    def to_csv(self):
        # Skilgreining
        string = f'{SEP}'

        # TODO Aldrei meira en eitt Ins?
        if self.inserts != [] and self.inserts[0].type == ItemType.BIGINS:
            string += f'{self.inserts[0].content}'

        string += f'{SEP}'

        # Dæmi
        string += f'{SEP}'

        string += f'{to_comma_separated(self.synonyms)}{SEP}'

        # Heimild
        string += f'{SEP}'

        # Sérsvið
        string += f'{SEP}'

        string += f'{to_comma_separated(self.related_words)}{SEP}'

        # TODO Hvað á að vera hér?
        if len(self.translations) > 0:
            string += f'{self.translations[0].content}{SEP}'

        # Skilgreining, en
        string += f'{SEP}'

        # Skýring, en
        string += f'{SEP}'

        # Dæmi, en
        string += f'{SEP}'

        string += f'{to_comma_separated(self.translations[1:])}{SEP}'

        # Heimild, en
        string += f'{SEP}'

        # Sérsvið, en
        string += f'{SEP}'

        # Vísun/sjá einnig, en
        string += ''

        return string

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

        if self.plural:
            string += '\\pl%\n'

        a = len(self.subentries) > 1

        for subentry in self.subentries:
            string += subentry.to_str(a)

        return string

    def to_csv(self):
        assert(len(self.subentries) == 1)

        return f'{self.word}{SEP}{self.subentries[0].to_csv()}'


class Ast:
    def __init__(self):
        self.entries_by_letter = {}

    def __str__(self):
        string = ""

        for letter, entries in sorted(self.entries_by_letter.items(), key=lambda x: x[0].casefold()):
            string += f'\\ns{{{letter.upper()}}}%\n%\n'

            for entry in entries:
                string += str(entry) + "%\n"

        return string

    def flatten(self):
        list = []

        for _, entries in sorted(self.entries_by_letter.items(), key=lambda x: x[0].casefold()):
            list.extend(entries)

        return list

    def to_csv(self):
        string = f'Hugtak: is{SEP}Skilgreining: is{SEP}Skýring: is{SEP}Dæmi: is{SEP}Samheiti: is{SEP}Heimild: is{SEP}Sérsvið: is{SEP}Vísun/sjá einnig: is{SEP}Hugtak: en{SEP}Skilgreining: en{SEP}Skýring: en{SEP}Dæmi: en{SEP}Samheiti: en{SEP}Heimild: en{SEP}Sérsvið: en{SEP}Vísun/sjá einnig: en\n'

        for entry in self.flatten():
            string += entry.to_csv() + "\n"

        return string