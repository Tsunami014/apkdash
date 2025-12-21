from getch import getch
from test import Test

t = Test()
t.print()
while True:
    t.updprint(getch())

