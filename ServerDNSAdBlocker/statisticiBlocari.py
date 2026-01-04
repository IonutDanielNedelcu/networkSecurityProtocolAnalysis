from collections import Counter
import re

companii = {
    'Google': re.compile(r'google'),
    'Facebook': re.compile(r'facebook'),
    'Amazon': re.compile(r'amazon'),
    'Microsoft': re.compile(r'microsoft'),
    'Adobe': re.compile(r'adobe'),
    'Apple': re.compile(r'apple'),
}

#citim domeniile din fisier
domenii = []
with open('blocked.txt', 'r') as f:
    for linie in f:
        if 'BLOCKED' in linie:
            obiecte = linie.strip().split()
            if len(obiecte) >= 4:
                domenii.append(obiecte[3])

#calculam frecventa fiecarui domeniu
contorDomenii = Counter(domenii)

#vedem pentru companiile mari din lista noastra 
contorCompanii = Counter()
for domeniu, cnt in contorDomenii.items():
    gasit = False
    for companie, expresie in companii.items():
        if expresie.search(domeniu):
            contorCompanii[companie] += cnt
            gasit = True
            break

#statistici pe companii
print("Statistici pe companii:")
for companie in companii.keys():
    cnt = contorCompanii.get(companie, 0)
    print(f"{companie} {cnt}")


#topul domeniilor 
print("\nTop 5 domenii:")
for dom, cnt in contorDomenii.most_common(5):
    print(f"{dom} {cnt}")

