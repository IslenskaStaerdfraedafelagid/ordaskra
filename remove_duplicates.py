from parser.ast import Ast, Entry


def remove_duplicates(ast):
    new_ast = Ast()

    for entry in ast.flatten():
        new_entry = Entry()

        new_entry.word = entry.word
        new_entry.category = entry.category
        new_entry.plural = entry.plural
        new_entry.kyn = entry.kyn

        for subentry in entry.subentries:
            duplicate = False

            if subentry.translations != []:
                for w in subentry.synonyms:
                    e = ast.lookup(w.content)

                    if e:
                        for subentry2 in e.subentries:
                            if w.idx != 0 and w.idx == subentry2.idx:
                                duplicate = True
                                break

            if not duplicate:
                new_entry.subentries.append(subentry)

        if new_entry.subentries != []:
            new_ast.add_entry(new_entry)

    return new_ast