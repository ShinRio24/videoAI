from imageGetter import download
from imageDescription import describe


l=download("jeff Bezos")
descriptions = []

print(l)
for x in l:
    descriptions.append(describe(x))

print(descriptions)