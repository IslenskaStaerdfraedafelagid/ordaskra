def count_branching(ast):
    i = 0

    for entry in ast.flatten():
        if len(entry.subentries) > 1:
            i += len(entry.subentries)

    return i