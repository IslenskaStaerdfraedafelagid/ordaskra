from parser.ast import Ast, Entry


def remove_duplicates(ast):
    new_ast = Ast()

    islensk_idord = set()

    for entry in ast.flatten():
        new_entry = Entry()

        new_entry.word = entry.word
        new_entry.category = entry.category
        new_entry.plural = entry.plural
        new_entry.kyn = entry.kyn

        for subentry in entry.subentries:
            duplicate = False
            new = False

            # Ef það eru engar íslenskar þýðingar þá verður þeim hent út síðar hvort eð er
            if subentry.translations != []:
                for idord in subentry.translations:
                    if idord.content not in islensk_idord:
                        islensk_idord.add(idord.content)
                        new = True

                # Ef nýju íslensku íðorði var bætt við lítum við ekki á þessa undirfærslu sem tvítekningu
                if new:
                    new_entry.subentries.append(subentry)
                    continue

                # Annars athugum við hvort þessi undirfærsla vitni í núverandi færslur sem samheiti
                for w in subentry.synonyms:
                    e = ast.lookup(w.content)

                    if e:
                        # Ef þessi færsla er til nú þegar og það var ekki verið að vitna í sérstaka undirfærslu lítum
                        # við á það sem tvítekningu
                        if w.idx == 0:
                            duplicate = True
                        # Annars athugum við hvort það hafi verið að vitna í undirfærslu sem ekki var búið að henda út
                        else:
                            for subentry2 in e.subentries:
                                if w.idx == subentry2.idx:
                                    duplicate = True
                                    break

            if not duplicate:
                new_entry.subentries.append(subentry)

        if new_entry.subentries != []:
            new_ast.add_entry(new_entry)

    return new_ast