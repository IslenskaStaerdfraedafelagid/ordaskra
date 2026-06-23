import pandas as pd

# GPT kóði

df = pd.read_csv("ordaskra_sorted.csv")
df = df[["Hugtök: is", "Skilgreining: is", "id"]].fillna("")

f = open("ordaskra_table.tex", "w", encoding="utf-8")

f.write("\\begin{longtable}{p{0.03\\textwidth} | p{0.48\\textwidth} | p{0.48\\textwidth}}\n")
f.write("\\hline\n")
f.write("\\textbf{id} & \\textbf{Hugtök} & \\textbf{Skilgreining} \\\\\n")
f.write("\\hline\n")

for _, row in df.iterrows():
    term = str(row["Hugtök: is"]).replace("&", "\\&")
    definition = str(row["Skilgreining: is"]).replace("&", "\\&")
    f.write(f"{row['id']} & {term} & {definition} \\\\\n\\hline\n")

f.write("\\hline\n")
f.write("\\end{longtable}\n")

f.close()