import sys

from count_conflicts import count_conflicts
from count_ungendered import count_ungendered
from parser.parse import parse
from parser.lex import lex
from parser.invert import invert
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("Notkun: python parse.py [skrá]")

path = Path(sys.argv[1])
outpath_dat = path.with_stem(path.stem + "_isl")
outpath_csv = outpath_dat.with_suffix(".csv")

try:
    file = open(path, "r")

    characters = file.read()

    tokens = lex(characters)

    ast = parse(tokens)

    reversed = invert(ast)

    outfile_dat = open(outpath_dat, "w")
    outfile_csv = open(outpath_csv, "w")

    outfile_dat.write(str(reversed))
    outfile_csv.write(reversed.to_csv())

    print(f'Fjöldi ókyngreindra orða: {count_ungendered(reversed)}')

except OSError:
    sys.exit(f"Villa: {path} fannst ekki")
