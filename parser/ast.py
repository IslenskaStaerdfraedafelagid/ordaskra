from enum import Enum

from unidecode import unidecode

from parser.util import first_char

# TODO
# SEP = chr(31)
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
            case ItemType.TY:
                return "ty"
            case ItemType.SH:
                return "sh"
            case ItemType.TV:
                return "tv"
            case ItemType.INS:
                return "ins"
            case ItemType.BIGINS:
                return "Ins"
            case _:
                return ""


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
            case Category.NA:
                return "na"
            case Category.LS:
                return "ls"
            case Category.SAG:
                return "sag"
            case Category.SAM:
                return "sam"
            case Category.AT:
                return "at"
            case Category.PREF:
                return "pref"
            case Category.SKA:
                return "ska"
            case _:
                return ""

    # TODO Setja á form sem Árnastofnun notar
    def to_csv(self):
        match self:
            case Category.NA:
                return "na"
            case Category.LS:
                return "ls"
            case Category.SAG:
                return "sag"
            case Category.SAM:
                return "sam"
            case Category.AT:
                return "at"
            case Category.PREF:
                return "pref"
            case Category.SKA:
                return "ska"
            case _:
                return ""


class Kyn(Enum):
    KK = 0
    KVK = 1
    HK = 2
    NONE = 3

    def __str__(self):
        match self:
            case Kyn.KK:
                return "kk"
            case Kyn.KVK:
                return "kvk"
            case Kyn.HK:
                return "hk"
            case _:
                return ""


class Item:
    def __init__(self):
        self.type = ItemType.NONE
        self.co = ""
        self.content = ""
        self.idx = 0

    def to_str(self, a=False):
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
        self.idx = 0

    def to_str(self, a=False):
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

        # Samheiti: is
        string += f'{SEP}'

        # Heimild
        string += f'{SEP}'

        # Sérsvið
        string += f'{SEP}'

        string += f'{to_comma_separated(self.related_words)}{SEP}'

        # Hugtak: en
        string += f'{to_comma_separated(self.translations)}{SEP}'

        # TODO Ensk tala?
        # Tala: en

        # Skilgreining, en
        string += f'{SEP}'

        # Skýring, en
        string += f'{SEP}'

        # Dæmi, en
        string += f'{SEP}'

        # Samheiti, en
        string += f'{SEP}'

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
        self.kyn = Kyn.NONE

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
        assert (len(self.subentries) == 1)

        tala = 'Fleirtala' if self.plural else 'Eintala'

        item = Item()
        item.content = self.word

        list = [item]
        list.extend(self.subentries[0].synonyms)
        # TODO
        return f'{to_comma_separated(list)}{SEP}{SEP}{self.category.to_csv()}{SEP}{self.kyn}{SEP}{tala}{SEP}{self.subentries[0].to_csv()}'


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

    def lookup(self, word):
        normalized_word = unidecode(word)
        letter = first_char(normalized_word).lower()

        return next((e for e in self.entries_by_letter.get(letter, []) if e.word == word), None)

    def exists(self, word):
        return self.lookup(word)

    def flatten(self):
        list = []

        for _, entries in sorted(self.entries_by_letter.items(), key=lambda x: x[0].casefold()):
            list.extend(entries)

        return list

    def to_csv(self):
        string = f'Hugtök: is{SEP}Val: is{SEP}Orðaflokkur: is{SEP}Kyn{SEP}Tala: is{SEP}Skilgreining: is{SEP}Skýring: is{SEP}Dæmi: is{SEP}Samheiti: is{SEP}Heimild: is{SEP}Sérsvið: is{SEP}Vísun/sjá einnig: is{SEP}Hugtak: en{SEP}Val: en{SEP}Skilgreining: en{SEP}Skýring: en{SEP}Dæmi: en{SEP}Samheiti: en{SEP}Heimild: en{SEP}Sérsvið: en{SEP}Vísun/sjá einnig: en\n'

        for entry in self.flatten():
            string += entry.to_csv() + "\n"

        return string

    def add_entry(self, entry):
        # Þetta er til þess að fjarlægjastafmerki þannig að orð eins og étale flokkist undir "e"
        word = unidecode(entry.word)
        # # Gerum ekki greinarmun á stórum og litlum staf, miðum við lítinn staf
        letter = first_char(word).lower()

        if not self.entries_by_letter.get(letter, []):
            self.entries_by_letter[letter] = [entry]
        else:
            self.entries_by_letter[letter].append(entry)

    def sort(self):
        for k, entries in sorted(self.entries_by_letter.items(), key=lambda x: x[0].casefold()):
            self.entries_by_letter[k] = list(sorted(entries, key=lambda x: x.word.casefold()))
