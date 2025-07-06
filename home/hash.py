def Hash(input):
    hash = 17
    for i in input:
        hash = hash * 23 + int(ord(i))
    return hash
code = 75737917631
print(Hash("testing"))