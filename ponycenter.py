#!/usr/bin/env python3

import os,sys,time, itertools
import argparse
from subprocess import *
try:
	import re2 as re
except:
	import re

'''
Gets the size of the terminal in (rows, columns)

@return  (rows, columns):(int, int)  The number or lines and the number of columns in the terminal's display area, [24, 80] if the size cannot be found
'''
def gettermsize():
	return	[int(x) for x in
				next(itertools.chain(
						(x for x in
							(Popen(['stty', 'size'], stdout=PIPE, stdin=fd, stderr=PIPE).communicate()[0].split()
								for fd in [sys.stdin, sys.stdout, sys.stderr])
						if x),
						[[24, 80]]
					)
				)
			]

parser = argparse.ArgumentParser(description='Center stuff on terminals')
parser.add_argument('string', nargs='*', type=str)
args = parser.parse_args()

for e in [sys.stdin] + args.string:
	lines = [e] if isinstance(e, str) else e.readlines()
	if lines:
		width = max(map(len, map(lambda s: re.sub(r'\x1B\[[0-9;]+m|\$.*\$', '', s), lines)))
		pad = int((gettermsize()[1]- width)/2)
		for line in lines:
			print(' '*pad + re.sub(r'\$.*\$|\n', '', line))

