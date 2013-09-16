#!/usr/bin/env python3
import random
from ponysay import ponysay

for i in range(0, 1000):
	pony = random.choice(ponysay.list_ponies_with_quotes())
	print(ponysay.render_pony(pony, ponysay.random_quote(pony),
					  balloonstyle=ponysay.balloonstyles['cowsay'],
					  width=ponysay.termwidth,
					  center=True,
					  centertext=False))
