import pandas as pd

from parse_table import table_to_dataframe

input_file = "ordaskra_table.tex"

df = table_to_dataframe(input_file)

non_empty = df[df["Skilgreining"] != ""]

def collect_references_and_replace_with_hyperlinks(table, row, column):
    references = []

    string = str(row[column])
    new_string = ""

    i = string.find('idTerm')
    k = 0

    while i < len(string) and i != -1:
        new_string += string[k:i - 5]

        i += 7

        j = string.find('>', i)

        ref = string[i:j]

        references.append(ref)

        k = string.find('<', j + 1)

        new_string += f'\\hyperlink{{row:{ref}}}{{{string[j + 1:k]}}}'

        k += 6

        i = string.find('idTerm', i)

    new_string += string[k:]

    table.loc[row.name, column] = new_string

    return references

def collect_referenced_entries(table, starting_row, reachable_rows):
    references = collect_references_and_replace_with_hyperlinks(table, starting_row, "Skilgreining")
    references.extend(collect_references_and_replace_with_hyperlinks(table, starting_row, "Skýring"))

    for ref in references:
        if ref in reachable_rows:
            continue

        reachable_rows.add(ref)

    return reachable_rows


reachable_rows = set(non_empty.index)

for _, row in non_empty.iterrows():
    reachable_rows = reachable_rows.union(collect_referenced_entries(df, row, reachable_rows))

defined_terms = df[df.index.isin(reachable_rows)]

f = open("ordaskra_table_finished.tex", "w", encoding="utf-8")

f.write("\\begin{longtable}{p{0.03\\textwidth} | p{0.22\\textwidth} | p{0.22\\textwidth} | p{0.22\\textwidth} | p{0.22\\textwidth}}\n")
f.write("\\hline\n")
f.write("\\textbf{id} & \\textbf{Hugtök} & \\textbf{Skilgreining} & \\textbf{Skýring} & \\textbf{Athugasemdir} \\\\\n")
f.write("\\hline\n")

for idx, row in defined_terms.iterrows():
    term = str(row["Hugtök"]).replace("&", "\\&")
    definition = str(row["Skilgreining"]).replace("&", "\\&")
    explanation = str(row["Skýring"]).replace("&", "\\&")
    comments = str(row["Athugasemdir"]).replace("&", "\\&")
    f.write(f"{idx} & \\hypertarget{{row:{idx}}}{{{term}}} & {definition} & {explanation} & {comments} \\\\\n\\hline\n")

f.write("\\hline\n")
f.write("\\end{longtable}\n")

f.close()

ordaskra = pd.read_csv("ordaskra_sorted.csv")

ordaskra["Skilgreining: is"] = ordaskra["Skilgreining: is"].fillna('').astype(str)
ordaskra["Skýring: is"] = ordaskra["Skýring: is"].fillna('').astype(str)

for idx, row in non_empty.iterrows():
    # Skauta framhjá MISSING færslunni
    if int(idx) == 0:
        continue
    elif not int(idx) in ordaskra["id"].values:
        continue

    ordaskra.loc[ordaskra["id"] == int(idx), "Hugtök: is"] = row["Hugtök"]
    ordaskra.loc[ordaskra["id"] == int(idx), "Skilgreining: is"] = row["Skilgreining"]
    ordaskra.loc[ordaskra["id"] == int(idx), "Skýring: is"] = row["Skýring"]

ordaskra.loc[:, "Skilgreining: is"] = ordaskra["Skilgreining: is"].apply(lambda x: x.replace('\n', '\\n'))
ordaskra.loc[:, "Skýring: is"] = ordaskra["Skýring: is"].apply(lambda x: x.replace('\n', '\\n'))

ordaskra.to_csv("ordaskra_new.csv", index=False)
