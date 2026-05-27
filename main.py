import sys
from parser.parse import parse
from parser.lex import lex


if len(sys.argv) < 2:
    sys.exit("Notkun: python parse.py [skrá]")

path = sys.argv[1]

try:
    file = open(path, encoding="latin-1")

    characters = file.read()

    tokens = lex(characters)

    ast = parse(tokens)

    print(ast)

except OSError:
    sys.exit(f"Villa: {path} fannst ekki")
