from .ast import *
import pandas as pd
from reynir import Greynir

#bin_ordalisti = pd.read_csv("SHsnid.csv", delimiter=";", header=None).set_index(0)[2].to_dict()
g = Greynir()

def analyze_gender(word):
    noun = None
    kyn = Kyn.NONE
    plural = False

    parsed = g.parse_single(word)

    if parsed is not None and parsed.terminals is not None:
        nouns = list(filter(lambda t: t.category == "no", parsed.terminals))
        if nouns != []:
            noun = nouns[0]

    # TODO Samsett orð
    if noun is not None:
        variants = noun.variants

        # TODO Ná í fleirtölu hérna í leiðinni?
        plural = variants[0] == "ft"

        match variants[1]:
            case "kk":
                kyn = Kyn.KK
            case "kvk":
                kyn = Kyn.KVK
            case "hk":
                kyn = Kyn.HK
            case _:
                # TODO Fletta upp í orðalista BÍN ef Greynir virkar ekki?
                pass

    if word.find("kk.") != -1:
        idx = word.find("(")

        return Kyn.KK, word[:idx-1], plural
    elif word.find("kvk.") != -1:
        idx = word.find("(")

        return Kyn.KVK, word[:idx-1], plural
    elif word.find("hk.") != -1:
        idx = word.find("(")

        return Kyn.HK, word[:idx-1], plural
    else:
        return kyn, word, plural

def invert(ast):
    reversed = Ast()

    for entry in ast.flatten():
        for subentry in entry.subentries:
            if len(subentry.translations) > 0:
                # Veljum fyrstu íslensku þýðinguna sem íðorðið sem fyrstu nálgun
                íðorð = subentry.translations[0]
                letter = íðorð.content[0]

                # Setjum enska orðið tengt færslunni sem fyrstu þýðingu
                new_word = Item()
                new_word.content = entry.word
                new_word.type = ItemType.TY

                new_subentry = SubEntry()
                new_subentry.translations.append(new_word)
                # Bætum síðan við restina af upprunalegu samheitunum sem auka þýðingum
                new_subentry.translations.extend(subentry.synonyms)

                # Allt nema fyrsta íslenska orðið verða þá að samheitum
                new_subentry.synonyms = subentry.translations[1:]
                # Skýringarnar fara beint í gegn
                new_subentry.inserts = subentry.inserts
                # TODO Ekki viss hvort að skyldu orðin eigi að fara beint í gegn
                new_subentry.related_words = subentry.related_words

                # Uppfæra tögin
                for word in new_subentry.translations:
                    word.type = ItemType.TY

                for word in new_subentry.synonyms:
                    word.type = ItemType.SH

                new_entry = Entry()

                new_entry.word = íðorð.content
                new_entry.category = entry.category
                new_entry.subentries.append(new_subentry)
                new_entry.plural = entry.plural

                kyn, updated_word, plural = analyze_gender(new_entry.word)

                new_entry.kyn = kyn
                new_entry.word = updated_word

                # Viljum að \pl skipanir ráði
                if not new_entry.plural:
                    new_entry.plural = plural

                if reversed.entries_by_letter.get(letter):
                    reversed.entries_by_letter[letter].append(new_entry)
                else:
                    reversed.entries_by_letter[letter] = [new_entry]

    return reversed