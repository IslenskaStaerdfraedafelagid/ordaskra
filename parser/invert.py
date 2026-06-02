from .ast import *

def invert(ast):
    reversed = Ast()

    for entry in ast.flatten():
        for subentry in entry.subentries:
            if len(subentry.translations) > 0:
                íðorð = subentry.translations[0]
                letter = íðorð.content[0]

                new_word = Item()
                new_word.content = entry.word
                new_word.type = ItemType.TY

                new_subentry = SubEntry()
                new_subentry.translations.append(new_word)
                new_subentry.translations.extend(subentry.synonyms)

                new_subentry.synonyms = subentry.translations[1:]
                new_subentry.inserts = subentry.inserts
                # TODO
                new_subentry.related_words = subentry.related_words

                for word in new_subentry.translations:
                    word.type = ItemType.TY

                for word in new_subentry.synonyms:
                    word.type = ItemType.SH

                new_entry = Entry()

                new_entry.word = íðorð.content
                new_entry.category = entry.category
                new_entry.subentries.append(new_subentry)
                new_entry.plural = entry.plural

                if reversed.entries_by_letter.get(letter):
                    reversed.entries_by_letter[letter].append(new_entry)
                else:
                    reversed.entries_by_letter[letter] = [new_entry]

    return reversed