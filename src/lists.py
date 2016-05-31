#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies

Copyright (C) 2012-2016  Erkin Batu Altunbaş et al.


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
import itertools


def _columnise_list(items: list, available_width: int, length_fn: callable, separation : int = 2):
    """
    From a list of items, produce a list of columns. Each columns is a list of tuples. Each tuple contains the element and a an int, specifying how much shorter the element is compared to the column width. 
    
    :param items: A list of items.
    :param available_width: The maximum with available horizontally for the items.
    :param length_fn: Function that is called to compute an element's width.
    :param separation: Amount of space to insert between columns. 
    """
    
    num_items = len(items)
    items_with_length = [(i, length_fn(i)) for i in items]
    max_item_length = max(i for _, i in items_with_length)
    
    # Make at least one column to handle very narrow terminals.
    num_columns = max((available_width + separation) // (max_item_length + separation), 1)
    column_length = (num_items - 1) // num_columns + 1
    
    items_with_spacing = [(i, max_item_length - l + separation) for i, l in items_with_length]
    
    return [items_with_spacing[i:i + column_length] for i in range(0, num_items, column_length)]


def _print_columnised(items):
    '''
    Columnise a list and prints it
    
    @param  ponies:list<(str, str)>  All items to list, each item should have to elements: unformatted name, formatted name.
    '''
    ## Get terminal width
    _, term_width = gettermsize()
    
    columns = _columnise_list(
        sorted(items, key = lambda x: x[0]),
        term_width,
        lambda x: UCS.dispLen(x[0]))
    
    for row in itertools.zip_longest(*columns):
        def iter_parts():
            spacing = 0
            
            for cell in row:
                if cell:
                    # Yield this here to prevent whitespace to be printed after the last column.
                    yield ' ' * spacing
                    
                    (_, item), spacing = cell
                    
                    yield item
        
        print(''.join(iter_parts()))
    
    print()


def _get_file_list(dir_path : str, extension : str):
    """
    Return a list of files in the specified directory with have the specified file name extension.
    
    :param dir_path: Path to the directory.
    :param extension: The allowed file name extension.
    """
    
    return [i[:-len(extension)] for i in os.listdir(dir_path) if endswith(i, extension)]


def simplelist(ponydirs, quoters = [], ucsiser = None):
    '''
    Lists the available ponies
    
    @param  ponydirs:itr<str>          The pony directories to use
    @param  quoters:__in__(str)→bool   Set of ponies that of quotes
    @param  ucsiser:(list<str>)?→void  Function used to UCS:ise names
    '''
    for ponydir in ponydirs: # Loop ponydirs
        ## Get all ponies in the directory
        ponies = _get_file_list(ponydir, '.pony')
        
        print()
        
        ## UCS:ise pony names, they are already sorted
        if ucsiser is not None:
            ucsiser(ponies)
        
        ## If ther directory is not empty print its name and all ponies, columnised
        if len(ponies) == 0:
            continue
        print('\033[1mponies located in ' + ponydir + '\033[21m')
        _print_columnised([(pony, '\033[1m' + pony + '\033[21m' if pony in quoters else pony) for pony in ponies])


def linklist(ponydirs = None, quoters = [], ucsiser = None):
    '''
    Lists the available ponies with alternatives inside brackets
    
    @param  ponydirs:itr<str>                        The pony directories to use
    @param  quoters:__in__(str)→bool                  Set of ponies that of quotes
    @param  ucsiser:(list<str>, map<str, str>)?→void  Function used to UCS:ise names
    '''
    
    for ponydir in ponydirs: # Loop ponydirs
        ## Get all pony files in the directory
        ponies = _get_file_list(ponydir, '.pony')
        
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
        _print_columnised(list(ponies))


def onelist(pony_dirs, ucsiser):
    '''
    Lists the available ponies on one column without anything bold or otherwise formated
    
    @param  pony_dirs:itr<str>        List of directories to search for ponies
    @param  ucsiser:(list<str>)→void  Function used to UCS:ise names
    '''
    ## Get all pony files
    ponies = [name for dir in pony_dirs for name in _get_file_list(dir, '.pony')]
    
    ## UCS:ise and sort
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
    
    extension = '.think' if isthink else '.say'
    
    ## Get all balloons
    balloonset = set(j for i in balloondirs for j in _get_file_list(i, extension))
    
    ## Print all balloos, columnised
    _print_columnised([(balloon, balloon) for balloon in balloonset])
