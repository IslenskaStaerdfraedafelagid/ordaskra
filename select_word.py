import pandas as pd

ordaskra = pd.read_csv("ordaskra.csv")
ordaskra['Val: is'] = ordaskra['Val: is'].fillna(0).astype(int)
ordaskra['Val: en'] = ordaskra['Val: en'].fillna(0).astype(int)
ordaskra['Samheiti: is'] = ordaskra['Samheiti: is'].fillna('').astype(str)
ordaskra['Samheiti: en'] = ordaskra['Samheiti: en'].fillna('').astype(str)

for idx, row in ordaskra.iterrows():
    is_words = row['Hugtök: is'].split(',')
    is_choice = int(row['Val: is'])
    ordaskra.loc[idx, 'Hugtök: is'] = is_words[is_choice]
    is_words.pop(is_choice)
    is_words = list(map(str.strip, is_words))
    en_words = row['Hugtak: en'].split(',')
    en_choice = int(row['Val: en'])
    ordaskra.loc[idx, 'Hugtak: en'] = en_words[en_choice]
    en_words.pop(en_choice)
    en_words = list(map(str.strip, en_words))

    ordaskra.loc[idx, 'Samheiti: is'] = ", ".join(is_words)
    ordaskra.loc[idx, 'Samheiti: en'] = ", ".join(en_words)

ordaskra = ordaskra.drop('Val: is', axis=1)
ordaskra = ordaskra.drop('Val: en', axis=1)

ordaskra.set_index("Hugtök: is", inplace=True)
ordaskra.to_csv("ordaskra_finished.csv")
