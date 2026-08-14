import pandas as pd

from parser.lex import replace_dollars, replace_double_dollars


def maybe_add_period(definition):
    new_definition = definition

    if not (new_definition == "" or new_definition.endswith(".") or new_definition.endswith(". \\]") or new_definition.endswith(". $$")):
        if new_definition.endswith("\\]"):
            new_definition = new_definition.removesuffix("\\]")
            new_definition += ".\\]"
        elif new_definition.endswith("$$"):
            new_definition = new_definition.removesuffix("$$")
            new_definition += ". $$]"
        else:
            new_definition += "."

    return new_definition

def table_to_dataframe(path):
    table = open(path).read()

    table = table.removeprefix('\\begin{longtable}{p{0.03\\textwidth}|p{0.22\\textwidth}|p{0.22\\textwidth}|p{0.22\\textwidth}|p{0.22\\textwidth}}')
    table = table.removeprefix('\\hline')
    table = table.removeprefix('\\textbf{id} & \\textbf{Hugtök} & \\textbf{Skilgreining} & \\textbf{Skýring} & \\textbf{Athugasemdir} \\\\')
    table = table.removeprefix('\\hline')

    table = table.replace('\\hline', '')

    table = table.removesuffix('\\\\\n\n\\end{longtable}\n')

    parsed_rows = []

    for row in table.split('\\\\'):
        columns = row.split('&')

        new_row = {
            "id": columns[0].strip(),
            "Hugtök": columns[1].strip(),
            "Skilgreining": columns[2].strip(),
            "Skýring": columns[3].strip(),
            "Athugasemdir": columns[4].strip(),
        }

        new_row["Skilgreining"] = maybe_add_period(new_row["Skilgreining"])
        new_row["Skýring"] = maybe_add_period(new_row["Skýring"])

        new_row["Skilgreining"] = replace_dollars(new_row["Skilgreining"])
        new_row["Skýring"] = replace_dollars(new_row["Skýring"])

        new_row["Skilgreining"] = replace_double_dollars(new_row["Skilgreining"])
        new_row["Skýring"] = replace_double_dollars(new_row["Skýring"])

        parsed_rows.append(new_row)


    df = pd.DataFrame(parsed_rows)
    df.set_index("id", inplace=True)

    return df
