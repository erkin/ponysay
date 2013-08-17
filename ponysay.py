#!/usr/bin/env python3

import os, sys, random
from os.path import dirname, realpath, exists
from pkg_resources import resource_string, resource_listdir, resource_exists
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

def list_ponies(markQuotes=False):
	quotes = lambda n: ' (quotes)' if markQuotes and exists(ponypath+'/'+n+'.quotes') else ''
	return [ f[:-5]+quotes(f[:-5]) for f in resource_listdir(__name__, 'ponies') if not f.endswith('.quotes') ]

def list_ponies_with_quotes():
	return [ f[:-7] for f in resource_listdir(__name__, 'ponies') if f.endswith('.quotes') ]

def load_pony(name):
	return str(resource_string(__name__, 'ponies/'+name+'.pony'), 'utf-8').split('\n')

def random_quote(name):
	quotepath='ponies/'+name+'.quotes'
	if resource_exists(__name__, quotepath):
		return random.choice(str(resource_string(__name__, quotepath), 'utf-8').split('\n\n'))
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
	pony = load_pony(name)
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
		first = pony.index('$$$')
		second = pony[first+1:].index('$$$')
		pony[first:] = pony[first+1+second+1:]
	except:
		pass
	pony = [ line.replace('$\\$', link_l).replace('$/$', link_r) for line in pony ]
	indent = ''
	if center:
		ponywidth = max([ len(re.sub(r'\x1B\[[0-9;]+m|\$.*\$', '', line)) for line in pony ])
		indent = ' '*int((width-ponywidth)/2)
	wre = re.compile('((\x1B\[[0-9;]+m)*.){0,%s}' % width)
	reset = '[39;49m\n'
	return indent+(reset+indent).join([ wre.search(line).group() for line in pony ])+reset

