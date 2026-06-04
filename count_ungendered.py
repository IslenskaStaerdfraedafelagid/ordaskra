from parser.ast import Category, Kyn


def count_ungendered(ast):
    i = 0

    for entry in ast.flatten():
        if entry.category == Category.NA and entry.kyn == Kyn.NONE:
            i += 1

    return i
