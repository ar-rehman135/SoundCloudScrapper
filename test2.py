import re
s = 'https://gate.sc/?url=http%3A%2F%2Finstagram.com%2Ftroubledte6&token=9bc1d3-1-1616572838086'
s1 = 'Part 1. Part 2. Part 3 then more text'

r = re.search(r'com%2F(.*?)&', s)
r1 = re.search(r'Part 1(.*?)Part 3', s1).group(1)

print(r)
print(r1)
