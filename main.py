import sys
from parser.parse import parse
from parser.lex import lex
from parser.invert import invert


if len(sys.argv) < 2:
    sys.exit("Notkun: python parse.py [skrá]")

path = sys.argv[1]

try:
    file = open(path, encoding="latin-1")

    characters = file.read()

    tokens = lex(characters)

    ast = parse(tokens)

    reversed = invert(ast)

    print(reversed)

except OSError:
    sys.exit(f"Villa: {path} fannst ekki")
