# Finnur fyrsta raunverulega bókstafinn í streng, aðallega notað til að hunsa dollaramerki og bandstrik í upphafi
def first_char(string):
    i = 0

    while not string[i].isalpha():
        i += 1

    return string[i]
