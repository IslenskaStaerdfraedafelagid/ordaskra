import pandas as pd
#from collections import defaultdict

df = pd.read_csv("ordaskra_sorted.csv")

multiple = df[
    df["Hugtök: is"].astype(str).str.contains(",", na=False)
]

co = df[
    df["Hugtak: en"].astype(str).str.contains(r"\(", na=False)
]

# duplicate_rows = []
#
# for idx1, row1 in multiple.iterrows():
#     print (f'Handling {idx1} of {multiple.shape[0]}')
#
#     íðorð1 = [x.strip() for x in row1["Hugtök: is"].split(",")]
#
#     duplicates = []
#
#     for orð in íðorð1:
#         for idx2, row2 in df.iterrows():
#             if idx1 == idx2:
#                 continue
#
#             íðorð2 = [x.strip() for x in row2["Hugtök: is"].split(",")]
#
#             if orð in íðorð2:
#                 duplicates.append(row2)
#
#     if duplicates:
#         duplicate_rows.append(row1)
#
#         for row in duplicates:
#             duplicate_rows.append(row)
#
# duplicates_df = pd.DataFrame(duplicate_rows)

# term_to_indices = defaultdict(set)
#
# for idx, value in df["Hugtök: is"].dropna().items():
#     terms = [x.strip() for x in str(value).split(",")]
#
#     for term in terms:
#         term_to_indices[term].add(idx)
#
#
# duplicate_indices = set()
#
# for idx1, row1 in multiple.iterrows():
#     terms1 = [x.strip() for x in str(row1["Hugtök: is"]).split(",")]
#
#     matching_indices = set()
#
#     for term in terms1:
#         matching_indices.update(term_to_indices[term])
#
#     matching_indices.discard(idx1)
#
#     if matching_indices:
#         duplicate_indices.add(idx1)
#         duplicate_indices.update(matching_indices)
#
# duplicates_df = df.loc[df.index.intersection(duplicate_indices)]

from collections import defaultdict, deque
import pandas as pd

term_to_indices = defaultdict(set)
row_to_terms = {}

for idx, value in df["Hugtök: is"].dropna().items():
    terms = {x.strip() for x in str(value).split(",") if x.strip()}
    row_to_terms[idx] = terms

    for term in terms:
        term_to_indices[term].add(idx)


seen = set()
grouped_rows = []
group_id = 0

for start_idx in multiple.index:
    if start_idx in seen:
        continue

    queue = deque([start_idx])
    component = set()

    while queue:
        idx = queue.popleft()

        if idx in component:
            continue

        component.add(idx)

        for term in row_to_terms.get(idx, set()):
            neighbors = term_to_indices[term]

            for neighbor_idx in neighbors:
                if neighbor_idx not in component:
                    queue.append(neighbor_idx)

    if len(component) > 1:
        group_id += 1

        for idx in df.index.intersection(component):
            row_copy = df.loc[idx].copy()
            row_copy["duplicate_group"] = group_id
            grouped_rows.append(row_copy)

        seen.update(component)

duplicates_df = pd.DataFrame(grouped_rows)

duplicates_df.set_index("Hugtök: is", inplace=True)
multiple.set_index("Hugtök: is", inplace=True)
co.set_index("Hugtök: is", inplace=True)

multiple.to_csv("ordaskra_val.csv")
duplicates_df.to_csv("ordaskra_tvitekning.csv")
co.to_csv("ordaskra_svigar.csv")
