#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay.py - POC of ponysay in python
Copyright (C) 2012 Elis "etu" Axelsson

License: WTFPL
'''

import argparse
import os
import curses
import sys
import random


version   = 1.98
if os.environ['TERM'] == 'linux':
    ponydirs = ['/usr/share/ponysay/ttyponies/', os.environ['HOME'] + '/.local/share/ponysay/ttyponies/']
else:
    ponydirs = ['/usr/share/ponysay/ponies/',    os.environ['HOME'] + '/.local/share/ponysay/ponies/']


parser = argparse.ArgumentParser(description = 'Ponysay, like cowsay with ponies')

parser.add_argument('-v', '--version', action = 'version',    version='%s %s' % (__file__, version))
parser.add_argument('-l', '--list',    action = 'store_true', dest = 'list', help = 'list pony files')
parser.add_argument('-f', '--pony',    action = 'append',     dest = 'pony', help = 'select a pony (either a file name or a pony name)')
parser.add_argument('message', nargs = '?', help = 'message to ponysay')

args = parser.parse_args()


class ponysay():
    def __init__(self, args):
        if args.list:
            self.list()
        else:
            self.print_pony(args)
    
    def list(self): # List ponies
        screen = curses.initscr()
        termsize = screen.getmaxyx()
        
        y = 0
        
        for ponydir in ponydirs: # Loop ponydirs
            screen.addstr(y, 0, 'ponyfiles located in ' + ponydir, curses.A_BOLD) # Print header
            y = y + 1
            
            ponies = os.listdir(ponydir)
            ponies.sort()
            width = len(max(ponies, key = len)) + 2 # Get the longest ponyfilename lenght + 2 spaces
            
            x = 0
            for pony in ponies:
                screen.addstr(y, x, pony) # Print ponyfilename
                
                x = x + width # Add width
                if x > (termsize[1] - width): # If too wide, make new line
                    x = 0
                    y = y + 1
            
            y = y + 2 # Increase y before the loop restart to make space for the next header
        
        screen.addstr(y, 0, '') # Make newline at end of output
        screen.refresh()
    
    def print_pony(self, args):
        if args.message == None:
            msg = sys.stdin.read().strip()
        else:
            msg = args.message
        
        
        if args.pony == None:
            ponies = [] # Make array with direct paths to all ponies
            for ponydir in ponydirs:
                for ponyfile in os.listdir(ponydir):
                    ponies.append(ponydir + ponyfile)
            
            pony = ponies[random.randrange(0, len(ponies) - 1)] # Select random pony
            
        else:
            for ponydir in ponydirs:
                if os.path.isfile(ponydir + args.pony[0]):
                    pony = ponydir + args.pony[0]
        
        os.system('cowsay -f ' + pony + ' "' + msg + '"')


if __name__ == '__main__':
    ponysay(args)

