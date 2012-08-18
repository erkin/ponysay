#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay.py - POC of ponysay in python
Copyright (C) 2012  Erkin Batu Altunbaş

Authors: Erkin Batu Altunbaş:              Project leader, helped write the first implementation
         Mattias "maandree" Andrée:        Major contributor of both implementions
         Elis "etu" Axelsson:              Major contributor of current implemention and patcher of first implementation
         Sven-Hendrik "svenstaro" Haase:   Major contributor first implementation
         Kyah "L-four" Rindlisbacher:      Patched the first implementation
         Jan Alexander "heftig" Steffens:  Major contributor first implementation

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
VERSION = '2.0-rc1'


'''
The directory where ponysay is installed, this is modified when building with make
'''
INSTALLDIR = '/usr'


'''
The user's home directory
'''
HOME = os.environ['HOME']


'''
Whether the program is execute in Linux VT (TTY)
'''
linuxvt = os.environ['TERM'] == 'linux'


'''
Whether the program is launched in subshell/being redirected
'''
redirected = False #not sys.stdout.isatty()  # currently impossible, we need to get rid of the little shell script first


'''
The directories where pony files are stored, ttyponies/ are used if the terminal is Linux VT (also known as TTY)
'''
ponydirs = []
if linuxvt:  _ponydirs = [HOME + '/.local/share/ponysay/ttyponies/',  INSTALLDIR + '/share/ponysay/ttyponies/']
else:        _ponydirs = [HOME + '/.local/share/ponysay/ponies/',     INSTALLDIR + '/share/ponysay/ponies/'   ]
for ponydir in _ponydirs:
    if os.path.isdir(ponydir):
        ponydirs.append(ponydir)


'''
The directories where quotes files are stored
'''
quotedirs = []
_quotedirs = [HOME + '/.local/share/ponysay/quotes/',  INSTALLDIR + '/share/ponysay/quotes/']
for quotedir in _quotedirs:
    if os.path.isdir(quotedir):
        quotedirs.append(quotedir)



'''
Argument parsing
'''
parser = argparse.ArgumentParser(prog = 'ponysay', description = 'cowsay wrapper for ponies')

parser.add_argument('-v', '--version', action = 'version',                       version = '%s %s' % ('ponysay', VERSION))
parser.add_argument('-l', '--list',    action = 'store_true', dest = 'list',     help = 'list pony files')
parser.add_argument('-L', '--altlist', action = 'store_true', dest = 'linklist', help = 'list pony files with alternatives')
parser.add_argument(      '--quoters', action = 'store_true', dest = 'quoters',  help = 'list ponies with quotes (visible in -l and -L)')  # for shell completions
parser.add_argument(      '--onelist', action = 'store_true', dest = 'onelist',  help = 'list pony files in one columns')                  # for shell completions
parser.add_argument('-W', '--wrap',    action = 'store',      dest = 'wrap',     help = 'specify the column when the message should be wrapped')
parser.add_argument('-f', '--pony',    action = 'append',     dest = 'pony',     help = 'select a pony (either a file name or a pony name)')
parser.add_argument('-q', '--quote',   nargs  = '*',          dest = 'quote',    help = 'select a pony which will quote herself')
parser.add_argument('message',         nargs  = '?',                             help = 'message to ponysay')

args = parser.parse_args()
# TODO implement   if [ -t 0 ] && [ $# == 0 ]; then
#                    usage
#                    exit
#                  fi



'''
This is the mane class of ponysay
'''
class ponysay():
    '''
    Starts the part of the program the arguments indicate
    '''
    def __init__(self, args):
        if args.list and redirected:
            args.list = False
            args.onelist = True
        
        if   args.list:      self.list()
        elif args.linklist:  self.linklist()
        elif args.quoters:   self.quoters()
        elif args.onelist:   self.onelist()
        elif args.quote:     self.quote(args)
        else:                self.print_pony(args)
    
    
    ##
    ## Auxiliary methods
    ##
    
    '''
    Returns one .pony-file with full path, names is filter for names, also accepts filepaths
    '''
    def __getponypath(self, names = None):
        ponies = {}
        
        if not names == None:
            for name in names:
                if os.path.isfile(name):
                    return name
        
        for ponydir in ponydirs:
            for ponyfile in os.listdir(ponydir):
                pony = ponyfile[:-5]
                if pony not in ponies:
                    ponies[pony] = ponydir + ponyfile
        
        if names == None:
            names = list(ponies.keys())
        
        return ponies[names[random.randrange(0, len(names))]]
    
    
    '''
    Returns a set with all ponies that have quotes and are displayable
    '''
    def __quoters(self):
        quotes = []
        quoteshash = set()
        _quotes = []
        for quotedir in quotedirs:
            _quotes += [item[:item.index('.')] for item in os.listdir(INSTALLDIR + '/share/ponysay/quotes/')]
        for quote in _quotes:
            if not quote == '':
                if not quote in quoteshash:
                    quoteshash.add(quote)
                    quotes.append(quote)
        
        ponies = set()
        for ponydir in ponydirs:
            for pony in os.listdir(ponydir):
                if not pony[0] == '.':
                    p = pony[:-5] # remove .pony
                    for quote in quotes:
                        if ('+' + p + '+') in ('+' + quote + '+'):
                            if not p in ponies:
                                ponies.add(p)
        
        return ponies
    
    
    '''
    Returns a list with all (pony, quote file) pairs
    '''
    def __quotes(self):
        quotes = []
        for quotedir in quotedirs:
            quotes += [quotedir + item for item in os.listdir(quotedir)]
        rc = []
        
        for ponydir in ponydirs:
            for pony in os.listdir(ponydir):
                if not pony[0] == '.':
                    p = pony[:-5] # remove .pony
                    for quote in quotes:
                        q = quote[quote.rindex('/') + 1:]
                        if ('+' + p + '+') in ('+' + q + '+'):
                            rc.append((p, quote))
        
        return rc
    
    
    '''
    Gets the size of the terminal in (rows, columns)
    '''
    def __gettermsize(self):
        termsize = Popen(['stty', 'size'], stdout=PIPE, stdin=sys.stderr).communicate()[0]
        termsize = termsize.decode('utf8', 'replace')[:-1].split(' ') # [:-1] removes a \n
        termsize = [int(item) for item in termsize]
        return termsize
    
    
    ##
    ## Listing methods
    ##
    
    '''
    Lists the available ponies
    '''
    def list(self):
        termsize = self.__gettermsize()
        quoters = self.__quoters()
        
        for ponydir in ponydirs: # Loop ponydirs
            print('\033[1mponyfiles located in ' + ponydir + '\033[21m')
            
            ponies = os.listdir(ponydir)
            ponies = [item[:-5] for item in ponies] # remove .pony from file name
            ponies.sort()
            
            width = len(max(ponies, key = len)) + 2 # Get the longest ponyfilename lenght + 2 spaces
            
            x = 0
            for pony in ponies:
                spacing = ' ' * (width - len(pony))
                print(('\033[1m' + pony + '\033[21m' if (pony in quoters) else pony) + spacing, end='') # Print ponyfilename
                x += width
                if x > (termsize[1] - width): # If too wide, make new line
                    print()
                    x = 0
                    
            print('\n');
    
    
    '''
    Lists the available ponies with alternatives inside brackets
    '''
    def linklist(self):
        termsize = self.__gettermsize()
        quoters = self.__quoters()
        
        for ponydir in ponydirs: # Loop ponydirs
            print('\033[1mponyfiles located in ' + ponydir + '\033[21m')
            
            files = os.listdir(ponydir)
            files = [item[:-5] for item in files] # remove .pony from file name
            files.sort()
            pairs = [(item, os.readlink(ponydir + item + '.pony') if os.path.islink(ponydir + item + '.pony') else '') for item in files]
            
            ponymap = {}
            for pair in pairs:
                if pair[1] == '':
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
            
            width = 0
            ponies = []
            widths = []
            for pony in ponymap:
                w = len(pony)
                item = '\033[1m' + pony + '\033[21m' if (pony in quoters) else pony
                syms = ponymap[pony]
                if len(syms) > 0:
                    w += 2 + len(syms)
                    item += ' ('
                    first = True
                    for sym in syms:
                        w += len(sym)
                        if not first:
                            item += ' '
                        else:
                            first = False
                        item += '\033[1m' + sym + '\033[21m' if (sym in quoters) else sym
                    item += ')'
                ponies.append(item)
                widths.append(w)
                if width < w:
                    width = w
            
            width += 2;
            x = 0
            index = 0
            for pony in ponies:
                spacing = ' ' * (width - widths[index])
                index += 1
                print(pony + spacing, end='') # Print ponyfilename
                x += width
                if x > (termsize[1] - width): # If too wide, make new line
                    print()
                    x = 0
            
            print('\n');
    
    
    '''
    Lists with all ponies that have quotes and are displayable
    '''
    def quoters(self):
        last = ""
        ponies = []
        for pony in self.__quoters():
            ponies.append(pony)
        ponies.sort()
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    '''
    Lists the available ponies one one column without anything bold
    '''
    def onelist(self):
        last = ""
        ponies = []
        for ponydir in ponydirs: # Loop ponydirs
            ponies += os.listdir(ponydir)
        ponies = [item[:-5] for item in ponies] # remove .pony from file name
        ponies.sort()
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    ##
    ## Displaying methods
    ##
    
    '''
    Returns (the cowsay command, whether it is a custom program)
    '''
    def __getcowsay(self):
        isthink = 'think.py' in __file__
        
        if isthink:
            cowthink = os.environ['PONYSAY_COWTHINK'] if 'PONYSAY_COWTHINK' in os.environ else None
            return ('cowthink', False) if (cowthink is None) or (cowthink == '') else (cowthink, True)
        
        cowsay = os.environ['PONYSAY_COWSAY'] if 'PONYSAY_COWSAY' in os.environ else None
        return ('cowsay', False) if (cowsay is None) or (cowsay == '') else (cowsay, True)
    
    
    '''
    Print the pony with a speech or though bubble
    '''
    def print_pony(self, args):
        if args.message == None:
            msg = sys.stdin.read().strip()
        else:
            msg = args.message
        
        pony = self.__getponypath(args.pony)
        (cowsay, customcowsay) = self.__getcowsay()
        
        cmd = [cowsay, '-f', self.__kms(pony)]
        if args.wrap is not None:
            cmd += ['-W', args.wrap]
        cmd.append(msg)
        
        if linuxvt:
            print('\033[H\033[2J', end='')
        
        proc = Popen(cmd, stdout=PIPE, stdin=sys.stderr)
        output = proc.communicate()[0].decode('utf8', 'replace')
        if (len(output) > 0) and (output[-1] == '\n'):
            output = output[:-1]
        exit_value = proc.returncode
        
        
        env_bottom = os.environ['PONYSAY_BOTTOM'] if 'PONYSAY_BOTTOM' in os.environ else None
        if env_bottom is None:  env_bottom = ''
        
        env_height = os.environ['PONYSAY_TRUNCATE_HEIGHT'] if 'PONYSAY_TRUNCATE_HEIGHT' in os.environ else None
        if env_height is None:  env_height = ''
        
        env_lines = os.environ['PONYSAY_SHELL_LINES'] if 'PONYSAY_SHELL_LINES' in os.environ else None
        if (env_lines is None) or (env_lines == ''):  env_lines = '2'
        
        lines = self.__gettermsize()[1] - int(env_lines)
        
        
        if not exit_value == 0:
            sys.stderr.write('Unable to successfully execute' + (' custom ' if customcowsay else ' ') + 'cowsay [' + cowsay + ']\n')
        else:
            if linuxvt or (env_height is ("yes", "y", "1")):
                if env_bottom is ("yes", "y", "1"):
                    for line in output[: -lines]:
                        print(line)
                else:
                    for line in output[: lines]:
                        print(line)
            else:
                print(output);
        
        
        ## TODO not implement, but it will be obsolete if we rewrite cowsay
        '''
        (if not customcowsay)
        
        pcmd='#!/usr/bin/perl\nuse utf8;'
        ccmd=$(for c in $(echo $PATH":" | sed -e 's/:/\/'"$cmd"' /g'); do if [ -f $c ]; then echo $c; break; fi done)
        
        if [ ${0} == *ponythink ]; then
            cat <(echo -e $pcmd) $ccmd > "/tmp/ponythink"
            perl '/tmp/ponythink' "$@"
            rm '/tmp/ponythink'
        else
            perl <(cat <(echo -e $pcmd) $ccmd) "$@"
        fi
        '''
    
    
    '''
    Print the pony with a speech or though bubble and a self quote
    '''
    def quote(self, args):
        pairs = self.__quotes()
        if len(args.quote) > 0:
            ponyset = set(args.quote)
            alts = []
            for pair in pairs:
                if pair[0] in ponyset:
                    alts.append(pair)
            pairs = alts
        
        if not len(pairs) == 0:
            pair = pairs[random.randrange(0, len(pairs))]
            qfile = None
            try:
                qfile = open(pair[1], 'r')
                args.message = '\n'.join(qfile.readlines()).strip()
            finally:
                if qfile is not None:
                    qfile.close()
            args.pony = [pair[0]]
        elif len(args.quote) == 0:
            sys.stderr.write('All the ponies are mute! Call the Princess!')
            exit(1)
        else:
            args.pony = args.quote[random.randrange(0, len(args.quote))]
            args.message = 'I got nuthin\' good to say :('
        
        self.print_pony(args)
    
    
    '''
    Returns the file name of the input pony converted to a KMS pony, or if KMS is not used, the input pony itself
    '''
    def __kms(self, pony):
        if not linuxvt:
            return pony
        
        env_kms = os.environ['PONYSAY_KMS_PALETTE'] if 'PONYSAY_KMS_PALETTE' in os.environ else None
        if env_kms is None:  env_kms = ''
        
        env_kms_cmd = os.environ['PONYSAY_KMS_PALETTE_CMD'] if 'PONYSAY_KMS_PALETTE_CMD' in os.environ else None
        if (env_kms_cmd is not None) and (not env_kms_cmd == ''):
            env_kms = Popen(shlex.split(env_kms_cmd), stdout=PIPE, stdin=sys.stderr).communicate()[0].decode('utf8', 'replace')
            if env_kms[-1] == '\n':
                env_kms = env_kms[:-1]
        
        if env_kms == '':
            return pony
        
        palette = env_kms
        palettefile = env_kms.replace('\033]P', '')
        
        kmsponies = '/var/cache/ponysay/kmsponies/' + palettefile
        kmspony = kmsponies + pony
        
        if not os.path.isfile(kmspony):
            protokmsponies = '/var/cache/ponysay/protokmsponies/'
            protokmspony = protokmsponies + pony
            
            _protokmspony = '\'' + protokmspony.replace('\'', '\'\\\'\'') + '\''
            _kmspony      = '\'' +      kmspony.replace('\'', '\'\\\'\'') + '\''
            _pony         = '\'' +         pony.replace('\'', '\'\\\'\'') + '\''
            
            if not os.path.isfile(protokmspony):
                os.makedirs(protokmsponies)
                if not os.system('ponysay2ttyponysay < ' + _pony + ' > ' + _protokmspony) == 0:
                    sys.stderr.write('Unable to run ponysay2ttyponysay successfully, you need util-say for KMS support\n')
                    exit(1)
            
            os.makedirs(kmsponies)
            if not os.system('tty2colourfultty -e -p ' + palette + ' < ' + _protokmspony + ' > ' + _kmspony) == 0:
                sys.stderr.write('Unable to run tty2colourfultty successfully, you need util-say for KMS support\n')
                exit(1)
        
        return kmspony



'''
Start the program from ponysay.__init__ if this is the executed file
'''
if __name__ == '__main__':
    ponysay(args)
