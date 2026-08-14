from idlelib.run import flush_stdout

import pandas as pd

def table_to_dataframe(path):
    table = open(path).read()

    table = table.removeprefix('\\begin{longtable}{p{0.03\\textwidth}|p{0.22\\textwidth}|p{0.22\\textwidth}|p{0.22\\textwidth}|p{0.22\\textwidth}}')
    table = table.removeprefix('\\hline')
    table = table.removeprefix('\\textbf{id} & \\textbf{Hugtök} & \\textbf{Skilgreining} & \\textbf{Skýring} & \\textbf{Athugasemdir} \\\\')
    table = table.removeprefix('\\hline')

    table = table.replace('\\hline', '')

    table = table.removesuffix('\\end{longtable}')

    parsed_rows = []

    for row in table.split('\\\\'):
        print(row)
        columns = row.split('&')
        print(columns)

        new_row = {
            "id": columns[0].strip(),
            "Hugtök": columns[1].strip(),
            "Skilgreining": columns[2].strip(),
            "Skýring": columns[3].strip(),
            "Athugasemdir": columns[4].strip(),
        }

        print(new_row)

        new_row["Skilgreining"] += "."

        parsed_rows.append(new_row)


    df = pd.DataFrame(parsed_rows)
    df.set_index("id", inplace=True)

    return df
