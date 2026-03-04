import sys
p='templates/assets.html'
with open(p,'rb') as f:
    data=f.read()
print(repr(data[-400:]))
