import sys
from pathlib import Path

from invert import invert
from parser.lex import lex
from parser.parse import parse
from remove_duplicates import remove_duplicates

if len(sys.argv) < 2:
    sys.exit("Notkun: python main.py [skrá]")

path = Path(sys.argv[1])
outpath_dat = path.with_stem(path.stem + "_isl")
outpath_csv = outpath_dat.with_suffix(".csv")

try:
    file = open(path, "r")

    characters = file.read()

    tokens = lex(characters)

    ast = parse(tokens)

    ast = remove_duplicates(ast)

    reversed = invert(ast)

    reversed.sort()

    outfile_dat = open(outpath_dat, "w")
    outfile_csv = open(outpath_csv, "w")

    outfile_dat.write(str(reversed))
    outfile_csv.write(reversed.to_csv())

except OSError:
    sys.exit(f"Villa: {path} fannst ekki")
