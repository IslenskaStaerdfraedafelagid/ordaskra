# GPT kóði
# TODO Fara yfir

import sys
import pandas as pd

if len(sys.argv) != 2:
    print(f"Usage: python {sys.argv[0]} <input.csv>")
    sys.exit(1)

input_file = sys.argv[1]

df = pd.read_csv(input_file)
df = df[["Hugtök: is", "Skilgreining: is", "id"]].fillna("")

f = open("ordaskra_table2.tex", "w", encoding="utf-8")

f.write("\\begin{longtable}{p{0.03\\textwidth} | p{0.22\\textwidth} | p{0.2\\textwidth} | p{0.2\\textwidth} | p{0.2\\textwidth}}\n")
f.write("\\hline\n")
f.write("\\textbf{id} & \\textbf{Hugtök} & \\textbf{Skilgreining} & \textbf{Skýring} & \textbf{Athugasemdir} \\\\\n")
f.write("\\hline\n")

for _, row in df.iterrows():
    term = str(row["Hugtök: is"]).replace("&", "\\&")
    definition = str(row["Skilgreining: is"]).replace("&", "\\&")
    f.write(f"{row['id']} & {term} & {definition} & &  \\\\\n\\hline\n")

f.write("\\hline\n")
f.write("\\end{longtable}\n")

f.close()
