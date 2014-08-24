#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies

Copyright (C) 2012, 2013, 2014  Erkin Batu Altunbaş et al.


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


If you intend to redistribute ponysay or a fork of it commercially,
it contains aggregated images, some of which may not be commercially
redistribute, you would be required to remove those. To determine
whether or not you may commercially redistribute an image make use
that line ‘FREE: yes’, is included inside the image between two ‘$$$’
lines and the ‘FREE’ is and upper case and directly followed by
the colon.


File listing functions.
'''


from ucs import *


class List: pass

def _columnise(ponies):
    '''
    Columnise a list and prints it
    
    @param  ponies:list<(str, str)>  All items to list, each item should have to elements: unformated name, formated name
    '''
    ## Get terminal width, and a 2 which is the space between columns
    termwidth = gettermsize()[1] + 2
    ## Sort the ponies, and get the cells' widths, and the largest width + 2
    ponies.sort(key = lambda pony : pony[0])
    widths = [UCS.dispLen(pony[0]) for pony in ponies]
    width = max(widths) + 2 # longest pony file name + space between columns
    
    ## Calculate the number of rows and columns, can create a list of empty columns
    cols = termwidth // width # do not believe electricians, this means ⌊termwidth / width⌋
    rows = (len(ponies) + cols - 1) // cols
    columns = []
    for c in range(0, cols):  columns.append([])
    
    ## Fill the columns with cells of ponies
    (y, x) = (0, 0)
    for j in range(0, len(ponies)):
        cell = ponies[j][1] + ' ' * (width - widths[j]);
        columns[x].append(cell)
        y += 1
        if y == rows:
            x += 1
            y = 0
    
    ## Make the columnisation nicer by letting the last row be partially empty rather than the last column
    diff = rows * cols - len(ponies)
    if (diff > 2) and (rows > 1):
        c = cols - 1
        diff -= 1
        while diff > 0:
            columns[c] = columns[c - 1][-diff:] + columns[c]
            c -= 1
            columns[c] = columns[c][:-diff]
            diff -= 1
    
    ## Create rows from columns
    lines = []
    for r in range(0, rows):
         lines.append([])
         for c in range(0, cols):
             if r < len(columns[c]):
                 line = lines[r].append(columns[c][r])
    
    ## Print the matrix, with one extra blank row
    print('\n'.join([''.join(line)[:-2] for line in lines]))
    print()


def simplelist(ponydirs, quoters = [], ucsiser = None):
    '''
    Lists the available ponies
    
    @param  ponydirs:itr<str>          The pony directories to use
    @param  quoters:__in__(str)→bool   Set of ponies that of quotes
    @param  ucsiser:(list<str>)?→void  Function used to UCS:ise names
    '''
    for ponydir in ponydirs: # Loop ponydirs
        ## Get all ponies in the directory
        _ponies = os.listdir(ponydir)
        
        ## Remove .pony from all files and skip those that does not have .pony
        ponies = []
        for pony in _ponies:
            if endswith(pony, '.pony'):
                ponies.append(pony[:-5])
        
        ## UCS:ise pony names, they are already sorted
        if ucsiser is not None:
            ucsiser(ponies)
        
        ## If ther directory is not empty print its name and all ponies, columnised
        if len(ponies) == 0:
            continue
        print('\033[1mponies located in ' + ponydir + '\033[21m')
        _columnise([(pony, '\033[1m' + pony + '\033[21m' if pony in quoters else pony) for pony in ponies])


def linklist(ponydirs = None, quoters = [], ucsiser = None):
    '''
    Lists the available ponies with alternatives inside brackets
    
    @param  ponydirs:itr<str>                        The pony directories to use
    @param  quoters:__in__(str)→bool                  Set of ponies that of quotes
    @param  ucsiser:(list<str>, map<str, str>)?→void  Function used to UCS:ise names
    '''
    ## Get the size of the terminal
    termsize = gettermsize()
    
    for ponydir in ponydirs: # Loop ponydirs
        ## Get all pony files in the directory
        _ponies = os.listdir(ponydir)
        
        ## Remove .pony from all files and skip those that does not have .pony
        ponies = []
        for pony in _ponies:
            if endswith(pony, '.pony'):
                ponies.append(pony[:-5])
        
        ## If there are no ponies in the directory skip to next directory, otherwise, print the directories name
        if len(ponies) == 0:
            continue
        print('\033[1mponies located in ' + ponydir + '\033[21m')
        
        ## UCS:ise pony names
        pseudolinkmap = {}
        if ucsiser is not None:
            ucsiser(ponies, pseudolinkmap)
        
        ## Create target–link-pair, with `None` as link if the file is not a symlink or in `pseudolinkmap`
        pairs = []
        for pony in ponies:
            if pony in pseudolinkmap:
                pairs.append((pony, pseudolinkmap[pony] + '.pony'));
            else:
                pairs.append((pony, os.path.realpath(ponydir + pony + '.pony') if os.path.islink(ponydir + pony + '.pony') else None))
        
        ## Create map from source pony to alias ponies for each pony
        ponymap = {}
        for pair in pairs:
            if (pair[1] is None) or (pair[1] == ''):
                if pair[0] not in ponymap:
                    ponymap[pair[0]] = []
            else:
                target = pair[1][:-5]
                if '/' in target:
                    target = target[target.rindex('/') + 1:]
                if target in ponymap:
                    ponymap[target].append(pair[0])
                else:
                    ponymap[target] = [pair[0]]
        
        ## Create list of source ponies concatenated with alias ponies in brackets
        ponies = {}
        for pony in ponymap:
            w = UCS.dispLen(pony)
            item = '\033[1m' + pony + '\033[21m' if (pony in quoters) else pony
            syms = ponymap[pony]
            syms.sort()
            if len(syms) > 0:
                w += 2 + len(syms)
                item += ' ('
                first = True
                for sym in syms:
                    w += UCS.dispLen(sym)
                    if first:  first = False
                    else:      item += ' '
                    item += '\033[1m' + sym + '\033[21m' if (sym in quoters) else sym
                item += ')'
            ponies[(item.replace('\033[1m', '').replace('\033[21m', ''), item)] = w
        
        ## Print the ponies, columnised
        _columnise(list(ponies))


def onelist(standarddirs, extradirs = None, ucsiser = None):
    '''
    Lists the available ponies on one column without anything bold or otherwise formated
    
    @param  standard:itr<str>?         Include standard ponies
    @param  extra:itr<str>?            Include extra ponies
    @param  ucsiser:(list<str>)?→void  Function used to UCS:ise names
    '''
    ## Get all pony files
    _ponies = []
    if standarddirs is not None:
        for ponydir in standarddirs:
            _ponies += os.listdir(ponydir)
    if extradirs is not None:
        for ponydir in extradirs:
            _ponies += os.listdir(ponydir)
        
    ## Remove .pony from all files and skip those that does not have .pony
    ponies = []
    for pony in _ponies:
        if endswith(pony, '.pony'):
            ponies.append(pony[:-5])
    
    ## UCS:ise and sort
    if ucsiser is not None:
        ucsiser(ponies)
    ponies.sort()
    
    ## Print each one on a seperate line, but skip duplicates
    last = ''
    for pony in ponies:
        if not pony == last:
            last = pony
            print(pony)


def balloonlist(balloondirs, isthink):
    '''
    Prints a list of all balloons
    
    @param  balloondirs:itr<str>  The balloon directories to use
    @param  isthink:bool          Whether the ponythink command is used
    '''
    ## Get the size of the terminal
    termsize = gettermsize()
    
    ## Get all balloons
    balloonset = set()
    for balloondir in balloondirs:
        for balloon in os.listdir(balloondir):
            ## Use .think if running ponythink, otherwise .say
            if isthink and endswith(balloon, '.think'):
                balloon = balloon[:-6]
            elif (not isthink) and endswith(balloon, '.say'):
                balloon = balloon[:-4]
            else:
                continue
            
            ## Add the balloon if there is none with the same name
            if balloon not in balloonset:
                balloonset.add(balloon)
    
    ## Print all balloos, columnised
    _columnise([(balloon, balloon) for balloon in balloonset])
