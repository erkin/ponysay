#!/usr/bin/env python3

import os, sys, random
from os.path import dirname, realpath, exists
import argparse, textwrap
try:
	import re2 as re
except:
	import re

# (oneline, multiline, bottom, top, linkl, linkr)
# {one,multi}line := (left, right)
# {left,right} := (top, middle, bottom)
balloonstyles= {'cowsay':		(((' ', '', '< '), (' ', '', '> ')), ((' /', '|', '\\ '), (' \\', '|', '/ ')), '-', '_', '\\', '/'),
				'cowsay.think':	(((' ', '', '( '), (' ', '', ') ')), ((' (', '(', '( '), (' )', ')', ') ')), '-', '_', 'o', 'o'),
				'ascii':		(((' /|', '', '\\ '), (' \\|', '', '/ ')), ((' /|', '|', '|\\'), (' \\|', '|', '|/')), '_', '_', '\\', '/'),
				'ascii.think':	(((' ((', '', '( '), (' ))', '', ') ')), ((' ((', '(', '(('), (' ))', ')', '))')), '_', '_', 'o', 'o'),
				'unicode':		((('┌││', '', '│└ '), ('┐││', '', '│┘ ')), (('┌││', '│', '││└'), ('┐││', '│', '││┘')), '─', '─', '╲', '╱'),
				'round':		((('╭││', '', '│╰ '), ('╮││', '', '│╯ ')), (('╭││', '│', '││╰'), ('╮││', '│', '││╯')), '─', '─', '╲', '╱'),
				'linux-vt':		((('┌││', '', '│└ '), ('┐││', '', '│┘ ')), (('┌││', '│', '││└'), ('┐││', '│', '││┘')), '─', '─', '\\', '/')}

ponypath = realpath(dirname(__file__)+'/../share/ponysay')
if not exists(ponypath):
	ponypath=realpath(dirname(__file__)+'/ponies')
termwidth = 80
try:
	termwidth = os.get_terminal_size()[0]
except:
	pass

def list_ponies(markQuotes=False):
	quotes = lambda n: ' (quotes)' if markQuotes and exists(ponypath+'/'+n+'.quotes') else ''
	return [ f[:-5]+quotes(f[:-5]) for f in os.listdir(ponypath) if not f.endswith('quotes') ]

def list_ponies_with_quotes(markQuotes=False):
	return [ f[:-7] for f in os.listdir(ponypath) if f.endswith('quotes') ]

def load_pony(name):
	return open(ponypath+'/'+name+'.pony').readlines()

def random_quote(name):
	quotepath=ponypath+'/'+name+'.quotes'
	if exists(quotepath):
		return random.choice(open(quotepath).read().split('\n\n'))
	else:
		return None

def render_balloon(text, balloonstyle, minwidth=0, maxwidth=40, pad=str.center):
	if text is None:
		return []
	(oneline, multiline, bottom, top, linkl, linkr) = balloonstyle
	lines = [ ' '+wrapline+' ' for textline in text.center(minwidth).split('\n') for wrapline in textwrap.wrap(textline, maxwidth) ]
	width = max([ len(line) for line in lines ]+[minwidth])
	side = lambda top, middle, bottom: top + middle*(len(lines)-2) + bottom
	leftside, rightside = oneline if len(lines) == 1 else multiline
	topextra, bottomextra = len(leftside[0])-2, len(leftside[2])-2
	leftside, rightside = side(*leftside), side(*rightside)
	lines = [top*width] + [' '*width]*topextra + [ pad(line, width) for line in lines ] + [' '*width]*bottomextra + [bottom*width]
	return [ l+m+r for l,m,r in zip(leftside, lines, rightside) ]

def render_pony(name, text, balloonstyle, width=80, center=False, centertext=False):
	pony = load_pony(name) #CAUTION: these lines already end with '\n'
	balloon = link_l = link_r = ''
	if text:
		[link_l, link_r] = balloonstyle[-2:]
	for i,line in enumerate(pony):
		match = re.search('\$balloon([0-9]*)\$', line)
		if match:
			minwidth = int(match.group(1) or '0')
			pony[i:i+1] = render_balloon(text, balloonstyle, minwidth=minwidth, maxwidth=int(width/2), pad=str.center if centertext else str.ljust)
			break
	try:
		first = pony.index('$$$\n')
		second = pony[first+1:].index('$$$\n')
		pony[first:] = pony[first+1+second+1:]
	except:
		pass
	pony = [ line.replace('$\\$', link_l).replace('$/$', link_r) for line in pony ]
	indent = ''
	if center:
		ponywidth = max([ len(re.sub(r'\x1B\[[0-9;]+m|\$.*\$', '', line)) for line in pony ])
		indent = ' '*int((width-ponywidth)/2)
	wre = re.compile('((\x1B\[[0-9;]+m)*.){0,%s}' % width)
	return ''.join([ indent+wre.search(line).group()+'\n[49m' for line in pony ])

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Cowsay with ponies')
	parser.add_argument('-p', '--pony', type=str, default='random', help='The name of the pony to be used. Use "-p list" to list all ponies, "-p random" (default) to use a random pony.')
	parser.add_argument('-q', '--quote', action='store_true', help='Use a random quote of the pony being displayed as text')
	parser.add_argument('-c', '--center', action='store_true', help='Use a random quote of the pony being displayed as text')
	parser.add_argument('-C', '--center-text', action='store_true', help='Center the text in the bubble')
	parser.add_argument('-w', '--width', type=int, default=termwidth, help='Terminal width. Use 0 for unlimited width. Default: autodetect')
	parser.add_argument('-b', '--balloon', type=str, default='cowsay', help='Balloon style to use. Use "-b list" to list available styles.')
	parser.add_argument('text', type=str, nargs='*', help='The text to be placed in the speech bubble')
	args = parser.parse_args()
  
	think = sys.argv[0].endswith('think')
	if args.pony == "list":
		print('\n'.join(sorted(list_ponies() if not args.quote else list_ponies_with_quotes())))
		sys.exit()
	if args.balloon == 'list':
		print('\n'.join([ s.replace('.think', '') for s in balloonstyles.keys() if s.endswith('.think') == think ]))
		sys.exit()
	pony = args.pony
	if pony == "random":
		pony = random.choice(list_ponies() if not args.quote else list_ponies_with_quotes())
	text = ' '.join(args.text) or None
	if text == '-':
		text = '\n'.join(sys.stdin.readlines())
	if args.quote:
		text = random_quote(pony)

	balloonstyle = None
	if think:
		balloonstyle = balloonstyles[args.balloon+'.think']
	else:
		balloonstyle = balloonstyles[args.balloon]

	print(render_pony(pony, text,
					  balloonstyle=balloonstyle,
					  width=args.width or sys.maxint,
					  center=args.center,
					  centertext=args.center_text))
