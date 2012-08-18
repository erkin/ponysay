#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay.py - POC of ponysay in python
Copyright (C) 2012 Elis "etu" Axelsson, Mattias "maandree" Andrée

License: WTFPL
'''

import argparse
import os
import sys
import random
from subprocess import Popen, PIPE


'''
The version of ponysay
'''
version = "2.0-alpha"


'''
The directory where ponysay is installed, this is modified when building with make
'''
installdir = '/usr'


'''
The directories where pony files are stored, ttyponies/ are used if the terminal is Linux VT (also known as TTY)
'''
ponydirs = []
if os.environ['TERM'] == 'linux':  _ponydirs = [installdir + '/share/ponysay/ttyponies/',  os.environ['HOME'] + '/.local/share/ponysay/ttyponies/']
else:                              _ponydirs = [installdir + '/share/ponysay/ponies/',     os.environ['HOME'] + '/.local/share/ponysay/ponies/'   ]
for ponydir in _ponydirs:
    if os.path.isdir(ponydir):
        ponydirs.append(ponydir)

parser = argparse.ArgumentParser(description = 'Ponysay, like cowsay with ponies')

parser.add_argument('-v', '--version', action = 'version',    version='%s %s' % (__file__, version))
parser.add_argument('-l', '--list',    action = 'store_true', dest = 'list', help = 'list pony files')
parser.add_argument('-f', '--pony',    action = 'append',     dest = 'pony', help = 'select a pony (either a file name or a pony name)')
parser.add_argument('message', nargs = '?', help = 'message to ponysay')

args = parser.parse_args()


class ponysay():
    def __init__(self, args):
        if args.list:  self.list()
        else:          self.print_pony(args)
    
    
    '''
    Lists the available ponies
    '''
    def list(self):
        termsize = Popen(['stty', 'size'], stdout=PIPE).communicate()[0].decode('utf8', 'replace')[:-1].split(" ")
        termsize = [int(item) for item in termsize]
        
        for ponydir in ponydirs: # Loop ponydirs
            print('\033[1mponyfiles located in ' + ponydir + '\033[21m')
            
            ponies = os.listdir(ponydir)
            ponies = [item[:-5] for item in ponies] # remove .pony from file name
            ponies.sort()
            
            width = len(max(ponies, key = len)) + 2 # Get the longest ponyfilename lenght + 2 spaces
            
            x = 0
            for pony in ponies:
                print(pony + (" " * (width - len(pony))), end="") # Print ponyfilename
                x = x + width
                if x > (termsize[1] - width): # If too wide, make new line
                    print();
                    x = 0
                    
            print("\n");
            
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




'''
Start the program from ponysay.__init__ if this is the executed file
'''
if __name__ == '__main__':
    ponysay(args)
