import re
import pandas as pd

input_file = "ordaskra_table.tex"

# Þetta kemur allt frá ChatGPT

def strip_comments(text):
    out = []
    i = 0

    while i < len(text):
        if text[i] == "%" and (i == 0 or text[i - 1] != "\\"):
            while i < len(text) and text[i] != "\n":
                i += 1
        else:
            out.append(text[i])
            i += 1

    return "".join(out)


def find_longtable_body(text):
    m1 = re.search(r"\\begin\{longtable\}\{", text)
    m2 = re.search(r"\\end\{longtable\}", text)

    if m1 is None or m2 is None:
        raise RuntimeError("Could not find longtable environment")

    i = m1.end()
    depth = 1

    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1

    return text[i:m2.start()]


def split_rows(body):
    rows = []
    current = []
    i = 0
    brace_depth = 0

    while i < len(body):
        ch = body[i]

        if ch == "\\":
            if i + 1 < len(body) and body[i + 1] == "\\" and brace_depth == 0:
                rows.append("".join(current).strip())
                current = []
                i += 2
                continue

            current.append(ch)
            i += 1
            continue

        if ch == "{":
            brace_depth += 1
        elif ch == "}" and brace_depth > 0:
            brace_depth -= 1

        current.append(ch)
        i += 1

    leftover = "".join(current).strip()
    if leftover:
        rows.append(leftover)

    return rows


def split_cells(row):
    cells = []
    current = []
    i = 0
    brace_depth = 0

    while i < len(row):
        ch = row[i]

        if ch == "\\":
            if i + 1 < len(row):
                current.append(row[i:i + 2])
                i += 2
            else:
                current.append(ch)
                i += 1
            continue

        if ch == "{":
            brace_depth += 1
        elif ch == "}" and brace_depth > 0:
            brace_depth -= 1

        if ch == "&" and brace_depth == 0:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(ch)

        i += 1

    cells.append("".join(current).strip())
    return cells


def clean_cell(cell):
    cell = cell.strip()
    cell = re.sub(r"^\s*\\hline\s*", "", cell)
    cell = re.sub(r"\s*\\hline\s*$", "", cell)
    cell = cell.strip()
    return cell

text = open(input_file, "r", encoding="utf-8").read()
text = strip_comments(text)

body = find_longtable_body(text)

body = re.sub(r"(?m)^\s*\\hline\s*$", "", body)
body = re.sub(r"(?m)^\s*\\endfirsthead\s*$", "", body)
body = re.sub(r"(?m)^\s*\\endhead\s*$", "", body)
body = re.sub(r"(?m)^\s*\\endfoot\s*$", "", body)
body = re.sub(r"(?m)^\s*\\endlastfoot\s*$", "", body)

parsed_rows = []

for row in split_rows(body):
    cells = [clean_cell(c) for c in split_cells(row)]

    if len(cells) == 0:
        continue

    if len(cells) == 5 and cells[0].strip().isdigit():
        parsed_rows.append({
            "id": cells[0].strip(),
            "Hugtök": cells[1],
            "Skilgreining": cells[2],
            "Skýring": cells[3],
            "Athugasemdir": cells[4],
        })

df = pd.DataFrame(parsed_rows)
df.set_index("id", inplace=True)

non_empty = df[df["Skilgreining"] != ""]

def collect_references_and_replace_with_hyperlinks(row):
    references = []

    string = str(row["Skilgreining"])
    new_string = ""

    i = string.find('idTerm')
    k = 0

    while i < len(string) and i != -1:
        new_string += string[k:i-5]

        i += 7

        j = string.find('>', i)

        ref = string[i:j]

        references.append(ref)

        k = string.find('<', j+1)

        new_string += f'\\hyperlink{{row:{ref}}}{{{string[j+1:k]}}}'

        k += 6

        i = string.find('idTerm', i)

    new_string += string[k:]

    return references, new_string

def table_dfs(table, starting_row, reachable_rows):
    references, new_row = collect_references_and_replace_with_hyperlinks(starting_row)

    table.loc[starting_row.name, "Skilgreining"] = new_row

    for ref in references:
        if ref in reachable_rows:
            continue

        reachable_rows.add(ref)

        reachable_rows.union(table_dfs(table, table.loc[ref], reachable_rows))

    return reachable_rows

reachable_rows = set(non_empty.index)

for _, row in non_empty.iterrows():
    reachable_rows = reachable_rows.union(table_dfs(df, row, reachable_rows))

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

