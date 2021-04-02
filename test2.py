import re
s = 'https://gate.sc/?url=http%3A%2F%2Finstagram.com%2Ftroubledte6&token=9bc1d3-1-1616572838086'
s1 = 'https://gate.sc/?url=https%3A%2F%2Fwww.instagram.com%2Fwarhol.ss%2F%3Fhl%3Den&token=dabdb8-1-1617369807034'
# s1 = 'Part 1. Part 2. Part 3 then more text'

r = s1.split(".com%2F")[1].split('&')[0]
if not r.find("%2F") == -1:
    r = r.split("%2F")[0]
# if r.contains('%2F'):
# r = re.search(r'com(.*?)&', s).group(0).
# r1 = re.search(r'Part 1(.*?)Part 3', s1).group(1)

print(r)
# print(r1)
