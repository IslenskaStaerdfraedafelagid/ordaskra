from parser.parse import first_char
from unidecode import unidecode

def count_conflicts(ast):
    i = 0

    for entry in ast.flatten():
        for subentry in entry.subentries:
            for synonym in subentry.synonyms:
                word = unidecode(synonym.content)
                letter = first_char(word).lower()

                if next((x for x in ast.entries_by_letter.get(letter, []) if x.word == synonym.content), None):
                    i += 1

    return i
