#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies
Copyright (C) 2012, 2013  Erkin Batu Altunbaş et al.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.


Authors of ponysay.py:

         Erkin Batu Altunbaş:              Project leader, helped write the first implementation
         Mattias "maandree" Andrée:        Major contributor of both implementions
         Elis "etu" Axelsson:              Major contributor of current implemention and patcher of the first implementation
         Sven-Hendrik "svenstaro" Haase:   Major contributor of the first implementation
         Jan Alexander "heftig" Steffens:  Major contributor of the first implementation
         Kyah "L-four" Rindlisbacher:      Patched the first implementation
'''

import os
import shutil
import sys
import random
from subprocess import Popen, PIPE



'''
The version of ponysay
'''
VERSION = 'dev'  # this line should not be edited, it is fixed by the build system



'''
Hack to enforce UTF-8 in output (in the future, if you see anypony not using utf-8 in
programs by default, report them to Princess Celestia so she can banish them to the moon)

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def print(text = '', end = '\n'):
    sys.stdout.buffer.write((str(text) + end).encode('utf-8'))

'''
stderr equivalent to print()

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def printerr(text = '', end = '\n'):
    sys.stderr.buffer.write((str(text) + end).encode('utf-8'))

fd3 = None
'''
/proc/self/fd/3 equivalent to print()

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def printinfo(text = '', end = '\n'):
    global fd3
    if os.path.exists('/proc/self/fd/3') and os.path.isfile('/proc/self/fd/3'):
        if fd3 is None:
            fd3 = os.fdopen(3, 'w')
    if fd3 is not None:
        fd3.write(str(text) + end)


'''
Checks whether a text ends with a specific text, but has more

@param   text    The text to test
@param   ending  The desired end of the text
@return  :bool   The result of the test
'''
def endswith(text, ending):
    return text.endswith(ending) and not (text == ending)



'''
This is the mane class of ponysay
'''
class Ponysay():
    '''
    Constructor
    '''
    def __init__(self):
        '''
        The user's home directory
        '''
        self.HOME = os.environ['HOME'] if 'HOME' in os.environ else ''
        if len(self.HOME) == 0:
            os.environ['HOME'] = self.HOME = os.path.expanduser('~')
        
        
        '''
        Parse a file name encoded with environment variables
        
        @param   file  The encoded file name
        @return        The target file name, None if the environment variables are not declared
        '''
        def parsefile(file):
            if '$' in file:
                buf = ''
                esc = False
                var = None
                for c in file:
                    if esc:
                        buf += c
                        esc = False
                    elif var is not None:
                        if c == '/':
                            var = os.environ[var] if var in os.environ else ''
                            if len(var) == 0:
                                return None
                            buf += var + c
                            var = None
                        else:
                            var += c
                    elif c == '$':
                        var = ''
                    elif c == '\\':
                        esc = True
                    else:
                        buf += c
                return buf
            return file
        
        
        ## Change system enviroment variables with ponysayrc
        for file in ('$XDG_CONFIG_HOME/ponysay/ponysayrc', '$HOME/.config/ponysay/ponysayrc', '$HOME/.ponysayrc', '/etc/ponysayrc'):
            file = parsefile(file)
            if (file is not None) and os.path.exists(file):
                with open(file, 'rb') as ponysayrc:
                    code = ponysayrc.read().decode('utf8', 'replace') + '\n'
                    env = os.environ
                    code = compile(code, file, 'exec')
                    exec(code)
                break
        
        self.HOME = os.environ['HOME'] if 'HOME' in os.environ else '' # in case ~/.ponysayrc changes it
        if len(self.HOME) == 0:
            os.environ['HOME'] = self.HOME = os.path.expanduser('~')
        
        
        '''
        Whether any unrecognised options was parsed, this should be set by the invoker before run()
        '''
        self.unrecognised = False
        
        
        '''
        Whether the program is execute in Linux VT (TTY)
        '''
        self.linuxvt = ('TERM' in os.environ) and (os.environ['TERM'] == 'linux')
        
        
        '''
        Whether the script is executed as ponythink
        '''
        self.isthink =  (len(__file__) >= len('think'))    and (__file__.endswith('think'))
        self.isthink = ((len(__file__) >= len('think.py')) and (__file__.endswith('think.py'))) or self.isthink
        
        
        '''
        Whether stdin is piped
        '''
        self.pipelinein = not sys.stdin.isatty()
        
        '''
        Whether stdout is piped
        '''
        self.pipelineout = not sys.stdout.isatty()
        
        '''
        Whether stderr is piped
        '''
        self.pipelineerr = not sys.stderr.isatty()
        
        
        '''
        Whether KMS is used
        '''
        self.usekms = self.isUsingKMS()
        
        
        '''
        Mode string that modifies or adds $ variables in the pony image
        '''
        self.mode = ''
        
        
        def share(file):
            def cat(a, b):
                if a is None:
                    return None
                return a + b
            return [cat(parsefile(item), file) for item in [
                    '$XDG_DATA_HOME/ponysay/',
                    '$HOME/.local/share/ponysay/',
                    '/usr/share/ponysay/',
                   ]]
        
        
        '''
        The directories where pony files are stored, ttyponies/ are used if the terminal is Linux VT (also known as TTY) and not with KMS
        '''
        appendset = set()
        self.xponydirs = []
        _ponydirs = share('ponies/')
        for ponydir in _ponydirs:
            if (ponydir is not None) and os.path.isdir(ponydir) and (ponydir not in appendset):
                self.xponydirs.append(ponydir)
                appendset.add(ponydir)
        appendset = set()
        self.vtponydirs = []
        _ponydirs = share('ttyponies/')
        for ponydir in _ponydirs:
            if (ponydir is not None) and os.path.isdir(ponydir) and (ponydir not in appendset):
                self.vtponydirs.append(ponydir)
                appendset.add(ponydir)
        
        
        '''
        The directories where pony files are stored, extrattyponies/ are used if the terminal is Linux VT (also known as TTY) and not with KMS
        '''
        appendset = set()
        self.extraxponydirs = []
        _extraponydirs = share('extraponies/')
        for extraponydir in _extraponydirs:
            if (extraponydir is not None) and os.path.isdir(extraponydir) and (extraponydir not in appendset):
                self.extraxponydirs.append(extraponydir)
                appendset.add(extraponydir)
        appendset = set()
        self.extravtponydirs = []
        _extraponydirs = share('extrattyponies/')
        for extraponydir in _extraponydirs:
            if (extraponydir is not None) and os.path.isdir(extraponydir) and (extraponydir not in appendset):
                self.extravtponydirs.append(extraponydir)
                appendset.add(extraponydir)
        
        
        '''
        The directories where quotes files are stored
        '''
        appendset = set()
        self.quotedirs = []
        _quotedirs = share('quotes/')
        for quotedir in _quotedirs:
            if (quotedir is not None) and os.path.isdir(quotedir) and (quotedir not in appendset):
                self.quotedirs.append(quotedir)
                appendset.add(quotedir)
        
        
        '''
        The directories where balloon style files are stored
        '''
        appendset = set()
        self.balloondirs = []
        _balloondirs = share('balloons/')
        for balloondir in _balloondirs:
            if (balloondir is not None) and os.path.isdir(balloondir) and (balloondir not in appendset):
                self.balloondirs.append(balloondir)
                appendset.add(balloondir)
        
        
        '''
        ucsmap files
        '''
        appendset = set()
        self.ucsmaps = []
        _ucsmaps = share('ucsmap/')
        for ucsmap in _ucsmaps:
            if (ucsmap is not None) and os.path.isdir(ucsmap) and (ucsmap not in appendset):
                self.ucsmaps.append(ucsmap)
                appendset.add(ucsmap)
    
    
    
    '''
    Starts the part of the program the arguments indicate
    
    @param  args:ArgParser  Parsed command line arguments
    '''
    def run(self, args):
        if (args.argcount == 0) and not self.pipelinein:
            args.help()
            exit(254)
            return
        
        ## Emulate termial capabilities
        if   args.opts['-X'] is not None:  (self.linuxvt, self.usekms) = (False, False)
        elif args.opts['-V'] is not None:  (self.linuxvt, self.usekms) = (True, False)
        elif args.opts['-K'] is not None:  (self.linuxvt, self.usekms) = (True, True)
        self.ponydirs      = self.vtponydirs      if self.linuxvt and not self.usekms else self.xponydirs
        self.extraponydirs = self.extravtponydirs if self.linuxvt and not self.usekms else self.extraxponydirs
        
        ## Variadic variants of -f, -q &c
        for sign in ('-', '+'):
            for letter in ('f', 'F', 'q', 'Q'):
                ssl = sign + sign + letter
                sl = sign + letter
                if (ssl in args.opts) and (args.opts[ssl] is not None):
                    if args.opts[sl] is not None:  args.opts[sl] += args.opts[ssl]
                    else:                          args.opts[sl]  = args.opts[ssl]
        
        ## Run modes
        if   args.opts['-h']        is not None:  args.help()
        elif args.opts['--quoters'] is not None:  self.quoters()
        elif args.opts['--onelist'] is not None:  self.onelist()
        elif args.opts['-v']        is not None:  self.version()
        elif args.opts['-l']        is not None:  self.list()
        elif args.opts['-L']        is not None:  self.linklist()
        elif args.opts['-B']        is not None:  self.balloonlist()
        elif args.opts['++onelist'] is not None:  self.__extraponies(); self.onelist()
        elif args.opts['+l']        is not None:  self.__extraponies(); self.list()
        elif args.opts['+L']        is not None:  self.__extraponies(); self.linklist()
        elif args.opts['-A']        is not None:  self.list(); self.__extraponies(); self.list()
        elif args.opts['+A']        is not None:  self.linklist(); self.__extraponies(); self.linklist()
        else:
            ## Colouring features
            if args.opts['--colour-pony'] is not None:
                self.mode += '\033[' + ';'.join(args.opts['--colour-pony']) + 'm'
            else:
                self.mode += '\033[0m'
            if args.opts['+c'] is not None:
                if args.opts['--colour-msg']    is None:  args.opts['--colour-msg']    = args.opts['+c']
                if args.opts['--colour-link']   is None:  args.opts['--colour-link']   = args.opts['+c']
                if args.opts['--colour-bubble'] is None:  args.opts['--colour-bubble'] = args.opts['+c']
            
            ## Other extra features
            self.__extraponies(args)
            self.__bestpony(args)
            self.__ucsremap(args)
            if args.opts['-o'] is not None:
                self.mode += '$/= $$\\= $'
                args.message = ''
                self.ponyonly = True
            else:
                self.ponyonly = False
            if (args.opts['-i'] is not None) or (args.opts['+i'] is not None):
                args.message = ''
            self.restriction = args.opts['-r']
            
            ## The stuff
            if args.opts['-q'] is not None:
                warn = (args.opts['-f'] is not None) or (args.opts['+f'] is not None)
                if (len(args.opts['-q']) == 1) and ((args.opts['-q'][0] == '-f') or (args.opts['-q'][0] == '+f')):
                    warn = True
                    if args.opts['-q'][0] == '-f':
                        args.opts['-q'] = args.files
                        if args.opts['-f'] is not None:
                            args.opts['-q'] += args.opts['-f']
                self.quote(args)
                if warn:
                    printerr('-q cannot be used at the same time as -f or +f.')
            elif not self.unrecognised:
                self.print_pony(args)
            else:
                args.help()
                exit(255)
                return
    
    
    ##############################################
    ## Methods that run before the mane methods ##
    ##############################################
    
    '''
    Use extra ponies
    
    @param  args:ArgParser  Parsed command line arguments, may be `None`
    '''
    def __extraponies(self, args = None):
        ## If extraponies are used, change ponydir to extraponydir
        if args is None:
            self.ponydirs[:] = self.extraponydirs
        elif args.opts['+f'] is not None:
            args.opts['-f'] = args.opts['+f']
            self.ponydirs[:] = self.extraponydirs
    
    
    '''
    Use best.pony if nothing else is set
    
    @param  args:ArgParser  Parsed command line arguments
    '''
    def __bestpony(self, args):
        ## Set best.pony as the pony to display if none is selected
        if (args.opts['-f'] is None) or (args.opts['-q'] is None) or (len(args.opts['-q']) == 0):
            for ponydir in self.ponydirs:
                if os.path.isfile(ponydir + 'best.pony') or os.path.islink(ponydir + 'best.pony'):
                    pony = os.path.realpath(ponydir + 'best.pony') # Canonical path
                    args.opts['-f' if args.opts['-q'] is None else '-q'] = [pony]
                    break
    
    
    '''
    Apply pony name remapping to args according to UCS settings
    
    @param  args:ArgParser  Parsed command line arguments
    '''
    def __ucsremap(self, args):
        ## Read UCS configurations
        env_ucs = os.environ['PONYSAY_UCS_ME'] if 'PONYSAY_UCS_ME' in os.environ else ''
        ucs_conf = 0
        if   env_ucs in ('yes',    'y', '1'):  ucs_conf = 1
        elif env_ucs in ('harder', 'h', '2'):  ucs_conf = 2
        
        ## Stop UCS is not used
        if ucs_conf == 0:
            return
        
        ## Read all lines in all UCS → ASCII map files
        maplines = []
        for ucsmap in self.ucsmaps:
            if os.path.isfile(ucsmap):
                with open(ucsmap, 'rb') as mapfile:
                    maplines += [line.replace('\n', '') for line in mapfile.read().decode('utf8', 'replace').split('\n')]
        
        ## Create UCS → ASCII mapping from read lines
        map = {}
        stripset = ' \t' # must be string, wtf! and way doesn't python's doc say so
        for line in maplines:
            if (len(line) > 0) and not (line[0] == '#'):
                s = line.index('→')
                ucs   = line[:s]    .strip(stripset)
                ascii = line[s + 1:].strip(stripset)
                map[ucs] = ascii
        
        ## Apply UCS → ASCII mapping to -f and -q arguments
        for flag in ('-f', '-q'):
            if args.opts[flag] is not None:
                for i in range(0, len(args.opts[flag])):
                    if args.opts[flag][i] in map:
                        args.opts[flag][i] = map[args.opts[flag][i]]
    
    
    #######################
    ## Auxiliary methods ##
    #######################
    
    '''
    Apply UCS:ise pony names according to UCS settings
    
    @param  ponies:list<str>  List of all ponies (of interrest)
    @param  links:map<str>    Map to fill with simulated symlink ponies, may be `None`
    '''
    def __ucsise(self, ponies, links = None):
        ## Read UCS configurations
        env_ucs = os.environ['PONYSAY_UCS_ME'] if 'PONYSAY_UCS_ME' in os.environ else ''
        ucs_conf = 0
        if   env_ucs in ('yes',    'y', '1'):  ucs_conf = 1
        elif env_ucs in ('harder', 'h', '2'):  ucs_conf = 2
        
        ## Stop UCS is not used
        if ucs_conf == 0:
            return
        
        ## Read all lines in all UCS → ASCII map files
        maplines = []
        for ucsmap in self.ucsmaps:
            if os.path.isfile(ucsmap):
                with open(ucsmap, 'rb') as mapfile:
                    maplines += [line.replace('\n', '') for line in mapfile.read().decode('utf8', 'replace').split('\n')]
        
        ## Create UCS → ASCII mapping from read lines
        map = {}
        stripset = ' \t' # must be string, wtf! and way doesn't python's doc say so
        for line in maplines:
            if not line.startswith('#'):
                s = line.index('→')
                ucs   = line[:s]    .strip(stripset)
                ascii = line[s + 1:].strip(stripset)
                map[ascii] = ucs
        
        ## Apply UCS → ACII mapping to ponies, by alias if weak settings
        if ucs_conf == 1:
            for pony in ponies:
                if pony in map:
                    ponies.append(map[pony])
                    if links is not None:
                        links[map[pony]] = pony
        else:
            for j in range(0, len(ponies)):
                if ponies[j] in map:
                    ponies[j] = map[ponies[j]]
    
    
    '''
    Returns one file with full path, names is filter for names, also accepts filepaths
    
    @param   names:list<str>  Ponies to choose from, may be `None`
    @param   alt:bool         For method internal use...
    @return  :str             The file name of a pony
    '''
    def __getponypath(self, names = None, alt = False):
        ponies = {}
        
        ## List all pony files, without the .pony ending
        for ponydir in self.ponydirs:
            for ponyfile in os.listdir(ponydir):
                if endswith(ponyfile, '.pony'):
                    pony = ponyfile[:-5]
                    if pony not in ponies:
                        ponies[pony] = ponydir + ponyfile
        
        ## Support for explicit pony file names
        if names is not None:
            for name in names:
                if os.path.exists(name):
                    ponies[name] = name
        
        '''
        Get ponies that fit the terminal
        
        @param  fitting      The set to fill
        @param  requirement  The maximum allowed value
        @param  file         The file with all data
        '''
        def getfitting(fitting, requirement, file):
            data = file.read() # not too much data, can load everything at once
            ptr = 0
            while data[ptr] != 47: # 47 == ord('/')
                ptr += 1
            ptr += 1
            size = 0
            while data[ptr] != 47: # 47 == ord('/')
                size = (size * 10) - (data[ptr] & 15)
                ptr += 1
            ptr += 1
            jump = ptr - size
            stop = 0
            backjump = 0
            while ptr < jump:
                size = 0
                while data[ptr] != 47: # 47 == ord('/')
                    size = (size * 10) - (data[ptr] & 15)
                    ptr += 1
                ptr += 1
                if -size > requirement:
                    if backjump > 0:
                        ptr = backjump
                        while data[ptr] != 47: # 47 == ord('/')
                            stop = (stop * 10) - (data[ptr] & 15)
                            ptr += 1
                        stop = -stop
                    break
                backjump = ptr
                while data[ptr] != 47: # 47 == ord('/')
                    ptr += 1
                ptr += 1
            if ptr == jump:
                stop = len(data)
            else:
                ptr = jump
                stop += ptr
            passed = data[jump : stop].decode('utf8', 'replace').split('/')
            for pony in passed:
                fitting.add(pony)
            
        
        ## If there is not select ponies, choose all of them
        if (names is None) or (len(names) == 0):
            oldponies = ponies
            if self.restriction is not None:
                logic = Ponysay.makeRestrictionLogic(self.restriction)
                ponies = {}
                for ponydir in self.ponydirs:
                    for pony in Ponysay.restrictedPonies(ponydir, logic):
                        if (pony not in passed) and (pony in oldponies):
                            ponyfile = ponydir + pony + '.pony'
                            if oldponies[pony] == ponyfile:
                                ponies[pony] = ponyfile
                oldponies = ponies
            ponies = {}
            (termh, termw) = self.__gettermsize()
            for ponydir in self.ponydirs:
                (fitw, fith) = (None, None)
                if os.path.exists(ponydir + 'widths'):
                    fitw = set()
                    with open(ponydir + 'widths', 'rb') as file:
                        getfitting(fitw, termw, file)
                if os.path.exists(ponydir + ('onlyheights' if self.ponyonly else 'heights')):
                    fith = set()
                    with open(ponydir + ('onlyheights' if self.ponyonly else 'heights'), 'rb') as file:
                        getfitting(fith, termh, file)
                for ponyfile in oldponies.values():
                    if ponyfile.startswith(ponydir):
                        pony = ponyfile[len(ponydir) : -5]
                        if (fitw is None) or (pony in fitw):
                            if (fith is None) or (pony in fith):
                                ponies[pony] = ponyfile
                #for ponyfile in os.listdir(ponydir):
                #    if endswith(ponyfile, '.pony'):
                #        pony = ponyfile[:-5]
                #        if pony not in ponies:
                #            if (fitw is None) or (pony in fitw):
                #                if (fith is None) or (pony in fith):
                #                    ponies[pony] = ponydir + ponyfile
            names = list((oldponies if len(ponies) == 0 else ponies).keys())
        
        ## Select a random pony of the choosen ones
        pony = names[random.randrange(0, len(names))]
        if pony not in ponies:
            if not alt:
                autocorrect = SpelloCorrecter(self.ponydirs, '.pony')
                (alternatives, dist) = autocorrect.correct(pony)
                limit = os.environ['PONYSAY_TYPO_LIMIT'] if 'PONYSAY_TYPO_LIMIT' in os.environ else ''
                limit = 5 if len(limit) == 0 else int(dist)
                if (len(alternatives) > 0) and (dist <= limit):
                    return self.__getponypath(alternatives, True)
            sys.stderr.write('I have never heard of anypony named %s\n' % (pony));
            exit(1)
        else:
            return ponies[pony]
    
    
    '''
    Make restriction test logic function
    
    @param   restriction:list<string>  Metadata based restrictions
    @return  :dict<str, str>→bool      Test function
    '''
    @staticmethod
    def makeRestrictionLogic(restriction):
        table = [(get_test(cell[:cell.index('=')],
                           cell[cell.index('=') + 1:]
                          )
                  for cell in clause.lower().replace('_', '').replace(' ', '').split('+'))
                  for clause in restriction
                ]
        
        def get_test(cell):
            strict = cell[0][-1] != '?'
            key = cell[0][:-2 if strict else -1]
            invert = cell[1][0] == '!'
            value = cell[1][1 if invert else 0:]
            
            class SITest:
                def __init__(self, cellkey, cellvalue):
                    (self.cellkey, self.callvalue) = (key, value)
                def __call__(self, has):
                    return False if key not in has else (value not in has[key])
            class STest:
                def __init__(self, cellkey, cellvalue):
                    (self.cellkey, self.callvalue) = (key, value)
                def __call__(self, has):
                    return False if key not in has else (value in has[key])
            class ITest:
                def __init__(self, cellkey, cellvalue):
                    (self.cellkey, self.callvalue) = (key, value)
                def __call__(self, has):
                    return True if key not in has else (value not in has[key])
            class NTest:
                def __init__(self, cellkey, cellvalue):
                    (self.cellkey, self.callvalue) = (key, value)
                def __call__(self, has):
                    return True if key not in has else (value in has[key])
            
            if strict and invert:  return SITest(key, value)
            if strict:             return STest(key, value)
            if invert:             return ITest(key, value)
            return NTest(key, value)
        
        def logic(cells):
            for alternative in table:
                ok = True
                for cell in alternative:
                    if not cell(cells):
                        ok = False
                        break
                if ok:
                    return True
            return False
        
        return logic
    
    
    '''
    Get ponies that pass restriction
    
    @param   ponydir:str                Pony directory
    @param   logic:dict<str, str>→bool  Restriction test functor
    @return  :list<str>                 Passed ponies
    '''
    @staticmethod
    def restrictedPonies(ponydir, logic):
        import cPickle
        passed = []
        if os.path.exists(ponydir + 'metadata'):
            data = None
            with open(ponydir + 'metadata', 'rb') as file:
                data = cPickle.load(file)
            for ponydata in data:
                (pony, meta) = ponydata
                if logic(meta):
                    passed.append(pony)
        return passed
    
    
    '''
    Returns a set with all ponies that have quotes and are displayable
    
    @return  :set<str>  All ponies that have quotes and are displayable
    '''
    def __quoters(self):
        ## List all unique quote files
        quotes = []
        quoteshash = set()
        _quotes = []
        for quotedir in self.quotedirs:
            _quotes += [item[:item.index('.')] for item in os.listdir(quotedir)]
        for quote in _quotes:
            if not quote == '':
                if not quote in quoteshash:
                    quoteshash.add(quote)
                    quotes.append(quote)
        
        ## Create a set of all ponyes that have quotes
        ponies = set()
        for ponydir in self.ponydirs:
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
    
    @return  (pony, quote):(str, str)  All ponies–quote file-pairs
    '''
    def __quotes(self):
        ## Get all ponyquote files
        quotes = []
        for quotedir in self.quotedirs:
            quotes += [quotedir + item for item in os.listdir(quotedir)]
        
        ## Create list of all pony–quote file-pairs
        rc = []
        for ponydir in self.ponydirs:
            for pony in os.listdir(ponydir):
                if not pony[0] == '.':
                    p = pony[:-5] # remove .pony
                    for quote in quotes:
                        q = quote[quote.rindex('/') + 1:]
                        q = q[:q.rindex('.')]
                        if ('+' + p + '+') in ('+' + q + '+'):
                            rc.append((p, quote))
        
        return rc
    
    
    '''
    Gets the size of the terminal in (rows, columns)
    
    @return  (rows, columns):(int, int)  The number or lines and the number of columns in the terminal's display area
    '''
    def __gettermsize(self):
        ## Call `stty` to determine the size of the terminal, this way is better than using python's ncurses
        for channel in (sys.stderr, sys.stdout, sys.stdin):
            termsize = Popen(['stty', 'size'], stdout=PIPE, stdin=channel, stderr=PIPE).communicate()[0]
            if len(termsize) > 0:
                termsize = termsize.decode('utf8', 'replace')[:-1].split(' ') # [:-1] removes a \n
                termsize = [int(item) for item in termsize]
                return termsize
        return (24, 80) # fall back to minimal sane size
    
    
    
    #####################
    ## Listing methods ##
    #####################
    
    '''
    Columnise a list and prints it
    
    @param  ponies:list<(str, str)>  All items to list, each item should have to elements: unformated name, formated name
    '''
    def __columnise(self, ponies):
        ## Get terminal width, and a 2 which is the space between columns
        termwidth = self.__gettermsize()[1] + 2
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
    
    
    '''
    Lists the available ponies
    '''
    def list(self):
        ## Get all quoters
        quoters = self.__quoters()
        
        for ponydir in self.ponydirs: # Loop ponydirs
            ## Get all ponies in the directory
            _ponies = os.listdir(ponydir)
            
            ## Remove .pony from all files and skip those that does not have .pony
            ponies = []
            for pony in _ponies:
                if endswith(pony, '.pony'):
                    ponies.append(pony[:-5])
            
            ## UCS:ise pony names, they are already sorted
            self.__ucsise(ponies)
            
            ## If ther directory is not empty print its name and all ponies, columnised
            if len(ponies) == 0:
                continue
            print('\033[1mponies located in ' + ponydir + '\033[21m')
            self.__columnise([(pony, '\033[1m' + pony + '\033[21m' if pony in quoters else pony) for pony in ponies])
    
    
    '''
    Lists the available ponies with alternatives inside brackets
    '''
    def linklist(self):
        ## Get the size of the terminal and all ponies with quotes
        termsize = self.__gettermsize()
        quoters = self.__quoters()
        
        for ponydir in self.ponydirs: # Loop ponydirs
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
            self.__ucsise(ponies, pseudolinkmap)
            
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
            self.__columnise(list(ponies))
    
    
    '''
    Lists with all ponies that have quotes and are displayable, on one column without anything bold or otherwise formated
    '''
    def quoters(self):
        ## Get all quoters
        ponies = self.__quoters()
        
        ## UCS:ise and sort
        self.__ucsise(ponies)
        ponies = list(ponies)
        ponies.sort()
        
        ## Print each one on a seperate line, but skip duplicates
        last = ''
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    '''
    Lists the available ponies on one column without anything bold or otherwise formated
    '''
    def onelist(self):
        ## Get all pony files
        _ponies = []
        for ponydir in self.ponydirs: # Loop ponydirs
            _ponies += os.listdir(ponydir)
        
        ## Remove .pony from all files and skip those that does not have .pony
        ponies = []
        for pony in _ponies:
            if endswith(pony, '.pony'):
                ponies.append(pony[:-5])
        
        ## UCS:ise and sort
        self.__ucsise(ponies)
        ponies.sort()
        
        ## Print each one on a seperate line, but skip duplicates
        last = ''
        for pony in ponies:
            if not pony == last:
                last = pony
                print(pony)
    
    
    #####################
    ## Balloon methods ##
    #####################
    
    '''
    Prints a list of all balloons
    '''
    def balloonlist(self):
        ## Get the size of the terminal
        termsize = self.__gettermsize()
        
        ## Get all balloons
        balloonset = set()
        for balloondir in self.balloondirs:
            for balloon in os.listdir(balloondir):
                ## Use .think if running ponythink, otherwise .say
                if self.isthink and endswith(balloon, '.think'):
                    balloon = balloon[:-6]
                elif (not self.isthink) and endswith(balloon, '.say'):
                    balloon = balloon[:-4]
                else:
                    continue
                
                ## Add the balloon if there is none with the same name
                if balloon not in balloonset:
                    balloonset.add(balloon)
        
        ## Print all balloos, columnised
        self.__columnise([(balloon, balloon) for balloon in list(balloonset)])
    
    
    '''
    Returns one file with full path, names is filter for style names, also accepts filepaths
    
    @param  names:list<str>  Balloons to choose from, may be `None`
    @param  alt:bool         For method internal use
    @param  :str             The file name of the balloon, will be `None` iff `names` is `None`
    '''
    def __getballoonpath(self, names, alt = False):
        ## Stop if their is no choosen balloon
        if names is None:
            return None
        
        ## Get all balloons
        balloons = {}
        for balloondir in self.balloondirs:
            for balloon in os.listdir(balloondir):
                balloonfile = balloon
                ## Use .think if running ponythink, otherwise .say
                if self.isthink and endswith(balloon, '.think'):
                    balloon = balloon[:-6]
                elif (not self.isthink) and endswith(balloon, '.say'):
                    balloon = balloon[:-4]
                else:
                    continue
                
                ## Add the balloon if there is none with the same name
                if balloon not in balloons:
                    balloons[balloon] = balloondir + balloonfile
        
        ## Support for explicit balloon file names
        for name in names:
            if os.path.exists(name):
                balloons[name] = name
        
        ## Select a random balloon of the choosen ones
        balloon = names[random.randrange(0, len(names))]
        if balloon not in balloons:
            if not alt:
                autocorrect = SpelloCorrecter(self.balloondirs, '.think' if self.isthink else '.say')
                (alternatives, dist) = autocorrect.correct(balloon)
                limit = os.environ['PONYSAY_TYPO_LIMIT'] if 'PONYSAY_TYPO_LIMIT' in os.environ else ''
                limit = 5 if len(limit) == 0 else int(dist)
                if (len(alternatives) > 0) and (dist <= limit):
                    return self.__getballoonpath(alternatives, True)
            sys.stderr.write('That balloon style %s does not exist\n' % (balloon));
            exit(1)
        else:
            return balloons[balloon]
    
    
    '''
    Creates the balloon style object
    
    @param   balloonfile:str  The file with the balloon style, may be `None`
    @return  :Balloon         Instance describing the balloon's style
    '''
    def __getballoon(self, balloonfile):
        ## Use default balloon if none is specified
        if balloonfile is None:
            if self.isthink:
                return Balloon('o', 'o', '( ', ' )', [' _'], ['_'], ['_'], ['_'], ['_ '], ' )',  ' )', ' )', ['- '], ['-'], ['-'], ['-'], [' -'],  '( ', '( ', '( ')
            return    Balloon('\\', '/', '< ', ' >', [' _'], ['_'], ['_'], ['_'], ['_ '], ' \\', ' |', ' /', ['- '], ['-'], ['-'], ['-'], [' -'], '\\ ', '| ', '/ ')
        
        ## Initialise map for balloon parts
        map = {}
        for elem in ('\\', '/', 'ww', 'ee', 'nw', 'nnw', 'n', 'nne', 'ne', 'nee', 'e', 'see', 'se', 'sse', 's', 'ssw', 'sw', 'sww', 'w', 'nww'):
            map[elem] = []
        
        ## Read all lines in the balloon file
        with open(balloonfile, 'rb') as balloonstream:
            data = balloonstream.read().decode('utf8', 'replace')
            data = [line.replace('\n', '') for line in data.split('\n')]
        
        ## Parse the balloon file, and fill the map
        last = None
        for line in data:
            if len(line) > 0:
                if line[0] == ':':
                    map[last].append(line[1:])
                else:
                    last = line[:line.index(':')]
                    value = line[len(last) + 1:]
                    map[last].append(value)
        
        ## Return the balloon
        return Balloon(map['\\'][0], map['/'][0], map['ww'][0], map['ee'][0], map['nw'], map['nnw'], map['n'],
                       map['nne'], map['ne'], map['nee'][0], map['e'][0], map['see'][0], map['se'], map['sse'],
                       map['s'], map['ssw'], map['sw'], map['sww'][0], map['w'][0], map['nww'][0])
    
    
    
    ########################
    ## Displaying methods ##
    ########################
    
    '''
    Prints the name of the program and the version of the program
    '''
    def version(self):
        ## Prints the "ponysay $VERSION", if this is modified, ./dev/dist.sh must be modified accordingly
        print('%s %s' % ('ponysay', VERSION))
    
    
    '''
    Print the pony with a speech or though bubble. message, pony and wrap from args are used.
    
    @param  args:ArgParser  Parsed command line arguments
    '''
    def print_pony(self, args):
        ## Get message and remove tailing whitespace from stdin (but not for each line)
        if args.message == None:
            msg = ''.join(sys.stdin.readlines()).rstrip()
        else:
            msg = args.message
        if args.opts['--colour-msg'] is not None:
            msg = '\033[' + ';'.join(args.opts['--colour-msg']) + 'm' + msg
        
        ## This algorithm should give some result as cowsay's (according to tests)
        if args.opts['-c'] is not None:
            buf = ''
            last = ' '
            CHARS = '\t \n'
            for c in msg:
                if (c in CHARS) and (last in CHARS):
                    if last == '\n':
                        buf += last
                    last = c
                else:
                    buf += c
                    last = c
            msg = buf.strip(CHARS)
            buf = ''
            for c in msg:
                if (c != '\n') or (last != '\n'):
                    buf += c
                    last = c
            msg = buf.replace('\n', '\n\n')
        
        ## Get the pony
        pony = self.__getponypath(args.opts['-f'])
        printinfo('pony file: ' + pony)
        
        ## Use PNG file as pony file
        if endswith(pony.lower(), '.png'):
            pony = '\'' + pony.replace('\'', '\'\\\'\'') + '\''
            pngcmd = 'ponytool --in image --file %s --out ponysay --platform %s --balloon y'
            pngcmd %= (pony, ('linux' if self.linuxvt else 'xterm')) # XXX xterm should be haiku in Haiku
            pngpipe = os.pipe()
            Popen(pngcmd, stdout=os.fdopen(pngpipe[1], 'w'), shell=True).wait()
            pony = '/proc/' + str(os.getpid()) + '/fd/' + str(pngpipe[0])
        
        ## If KMS is utilies, select a KMS pony file and create it if necessary
        pony = self.__kms(pony)
        
        ## If in Linux VT clean the terminal (See info/pdf-manual [Printing in TTY with KMS])
        if self.linuxvt:
            print('\033[H\033[2J', end='')
        
        ## Get width truncation and wrapping
        env_width = os.environ['PONYSAY_FULL_WIDTH'] if 'PONYSAY_FULL_WIDTH' in os.environ else None
        if env_width is None:  env_width = ''
        widthtruncation = self.__gettermsize()[1] if env_width not in ('yes', 'y', '1') else None
        messagewrap = 40
        if (args.opts['-W'] is not None) and (len(args.opts['-W'][0]) > 0):
            messagewrap = args.opts['-W'][0]
            if messagewrap[0] in 'nmsNMS': # m is left to n on QWERTY and s is left to n on Dvorak
                messagewrap = None
            elif messagewrap[0] in 'iouIOU': # o is left to i on QWERTY and u is right to i on Dvorak
                messagewrap = self.__gettermsize()[1]
            else:
                messagewrap = int(args.opts['-W'][0])
        
        ## Get balloon object
        balloonfile = self.__getballoonpath(args.opts['-b'])
        printinfo('balloon style file: ' + str(balloonfile))
        balloon = self.__getballoon(balloonfile) if args.opts['-o'] is None else None
        
        ## Get hyphen style
        hyphen = os.environ['PONYSAY_WRAP_HYPHEN'] if 'PONYSAY_WRAP_HYPHEN' in os.environ else None
        if (hyphen is None) or (len(hyphen) == 0):
            hyphen = '-'
        hyphencolour = ''
        if args.opts['--colour-wrap'] is not None:
            hyphencolour = '\033[' + ';'.join(args.opts['--colour-wrap']) + 'm'
        hyphen = '\033[31m' + hyphencolour + hyphen
        
        ## Link and balloon colouring
        linkcolour = ''
        if args.opts['--colour-link'] is not None:
            linkcolour = '\033[' + ';'.join(args.opts['--colour-link']) + 'm'
        ballooncolour = ''
        if args.opts['--colour-bubble'] is not None:
            ballooncolour = '\033[' + ';'.join(args.opts['--colour-bubble']) + 'm'
        
        ## Determine --info/++info settings
        minusinfo = args.opts['-i'] is not None
        plusinfo  = args.opts['+i'] is not None
        
        ## Run cowsay replacement
        backend = Backend(message = msg, ponyfile = pony, wrapcolumn = messagewrap, width = widthtruncation, balloon = balloon,
                          hyphen = hyphen, linkcolour = linkcolour, ballooncolour = ballooncolour, mode = self.mode,
                          infolevel = 2 if plusinfo else (1 if minusinfo else 0))
        backend.parse()
        output = backend.output
        if output.endswith('\n'):
            output = output[:-1]
        
        
        ## Load height trunction settings
        env_bottom = os.environ['PONYSAY_BOTTOM'] if 'PONYSAY_BOTTOM' in os.environ else None
        if env_bottom is None:  env_bottom = ''
        
        env_height = os.environ['PONYSAY_TRUNCATE_HEIGHT'] if 'PONYSAY_TRUNCATE_HEIGHT' in os.environ else None
        if env_height is None:  env_height = ''
        
        env_lines = os.environ['PONYSAY_SHELL_LINES'] if 'PONYSAY_SHELL_LINES' in os.environ else None
        if (env_lines is None) or (env_lines == ''):  env_lines = '2'
        
        ## Print the output, truncated on height is so set
        lines = self.__gettermsize()[0] - int(env_lines)
        if self.linuxvt or (env_height is ('yes', 'y', '1')):
            if env_bottom is ('yes', 'y', '1'):
                for line in output.split('\n')[: -lines]:
                    print(line)
            else:
                for line in output.split('\n')[: lines]:
                    print(line)
        else:
            print(output)
    
    
    '''
    Print the pony with a speech or though bubble and a self quote
    
    @param  args:ArgParser  Parsed command line arguments
    '''
    def quote(self, args):
        ## Get all quotes, and if any pony is choosen just keep them
        pairs = self.__quotes()
        if len(args.opts['-q']) > 0:
            ponyset = {}
            for pony in args.opts['-q']:
                if endswith(pony, '.pony'):
                    ponyname = pony[:-5]
                    if '/' in ponyname:
                        ponyname = ponyname[ponyname.rindex('/') + 1:]
                    ponyset[ponyname] = pony
                else:
                    ponyset[pony] = pony
            alts = []
            for pair in pairs:
                if pair[0] in ponyset:
                    alts.append((ponyset[pair[0]], pair[1]))
            pairs = alts
        
        ## Select a random pony–quote-pair, load it and print it
        if not len(pairs) == 0:
            pair = pairs[random.randrange(0, len(pairs))]
            printinfo('quote file: ' + pair[1])
            with open(pair[1], 'rb') as qfile:
                args.message = qfile.read().decode('utf8', 'replace').strip()
            args.opts['-f'] = [pair[0]]
        elif len(args.opts['-q']) == 0:
            sys.stderr.write('Princess Celestia! All the ponies are mute!\n')
            exit(1)
        else:
            args.opts['-f'] = [args.opts['-q'][random.randrange(0, len(args.opts['-q']))]]
            args.message = 'Zecora! Help me, I am mute!'
        
        self.print_pony(args)
    
    
    '''
    Identifies whether KMS support is utilised
    '''
    def isUsingKMS(self):
        ## KMS is not utilised if Linux VT is not used
        if not self.linuxvt:
            return False
        
        ## Read the PONYSAY_KMS_PALETTE environment variable
        env_kms = os.environ['PONYSAY_KMS_PALETTE'] if 'PONYSAY_KMS_PALETTE' in os.environ else None
        if env_kms is None:  env_kms = ''
        
        ## Read the PONYSAY_KMS_PALETTE_CMD environment variable, and run it
        env_kms_cmd = os.environ['PONYSAY_KMS_PALETTE_CMD'] if 'PONYSAY_KMS_PALETTE_CMD' in os.environ else None
        if (env_kms_cmd is not None) and (not env_kms_cmd == ''):
            env_kms = Popen(shlex.split(env_kms_cmd), stdout=PIPE, stdin=sys.stderr).communicate()[0].decode('utf8', 'replace')
            if env_kms[-1] == '\n':
                env_kms = env_kms[:-1]
        
        ## If the palette string is empty KMS is not utilised
        return env_kms != ''
    
    
    '''
    Returns the file name of the input pony converted to a KMS pony, or if KMS is not used, the input pony itself
    
    @param   pony:str  Choosen pony file
    @return  :str      Pony file to display
    '''
    def __kms(self, pony):
        ## If not in Linux VT, return the pony as is
        if not self.linuxvt:
            return pony
        
        ## KMS support version constant
        KMS_VERSION = '2'
        
        ## Read the PONYSAY_KMS_PALETTE environment variable
        env_kms = os.environ['PONYSAY_KMS_PALETTE'] if 'PONYSAY_KMS_PALETTE' in os.environ else None
        if env_kms is None:  env_kms = ''
        
        ## Read the PONYSAY_KMS_PALETTE_CMD environment variable, and run it
        env_kms_cmd = os.environ['PONYSAY_KMS_PALETTE_CMD'] if 'PONYSAY_KMS_PALETTE_CMD' in os.environ else None
        if (env_kms_cmd is not None) and (not env_kms_cmd == ''):
            env_kms = Popen(shlex.split(env_kms_cmd), stdout=PIPE, stdin=sys.stderr).communicate()[0].decode('utf8', 'replace')
            if env_kms[-1] == '\n':
                env_kms = env_kms[:-1]
        
        ## If not using KMS, return the pony as is
        if env_kms == '':
            return pony
        
        ## Store palette string and a clone with just the essentials
        palette = env_kms
        palettefile = env_kms.replace('\033]P', '')
        
        ## Get and in necessary make cache directory
        cachedir = '/var/cache/ponysay'
        shared = True
        if not os.path.isdir(cachedir):
            cachedir = self.HOME + '/.cache/ponysay'
            shared = False
            if not os.path.isdir(cachedir):
                os.makedirs(cachedir)
        _cachedir = '\'' + cachedir.replace('\'', '\'\\\'\'') + '\''
        
        ## KMS support version control, clean everything if not matching
        newversion = False
        if not os.path.isfile(cachedir + '/.version'):
            newversion = True
        else:
            with open(cachedir + '/.version', 'rb') as cachev:
                if cachev.read().decode('utf8', 'replace').replace('\n', '') != KMS_VERSION:
                    newversion = True
        if newversion:
            for cached in os.listdir(cachedir):
                cached = cachedir + '/' + cached
                if os.path.isdir(cached) and not os.path.islink(cached):
                    shutil.rmtree(cached, False)
                else:
                    os.remove(cached)
            with open(cachedir + '/.version', 'w+') as cachev:
                cachev.write(KMS_VERSION)
                if shared:
                    Popen('chmod 666 -- ' + _cachedir + '/.version', shell=True).wait()
        
        ## Get kmspony directory and kmspony file
        kmsponies = cachedir + '/kmsponies/' + palettefile
        kmspony = (kmsponies + pony).replace('//', '/')
        
        ## If the kmspony is missing, create it
        if not os.path.isfile(kmspony):
            ## kmspony directory
            kmsponydir = kmspony[:kmspony.rindex('/')]
            
            ## Change file names to be shell friendly
            _kmspony = '\'' + kmspony.replace('\'', '\'\\\'\'') + '\''
            _pony    = '\'' +    pony.replace('\'', '\'\\\'\'') + '\''
            
            ## Create kmspony
            if not os.path.isdir(kmsponydir):
                os.makedirs(kmsponydir)
                if shared:
                    Popen('chmod -R 6777 -- ' + _cachedir, shell=True).wait()
            ponytoolcmd = 'ponytoolcmd --import ponysay --file %s --export ponysay --file %s --platform linux ' +
                          '--balloon n --colourful y --fullcolour y --left - --right - --top - --bottom - --palette %s'
            if not os.system(ponytoolcmd % (_pony, _kmspony, palette)) == 0:
                sys.stderr.write('Unable to run ponytool successfully, you need util-say>=3 for KMS support\n')
                exit(1)
            if shared:
                Popen('chmod 666 -- ' + _kmspony, shell=True).wait()
        
        return kmspony



'''
Option takes no arguments
'''
ARGUMENTLESS = 0

'''
Option takes one argument per instance
'''
ARGUMENTED = 1

'''
Option consumes all following arguments
'''
VARIADIC = 2

'''
Simple argument parser
'''
class ArgParser():
    '''
    Constructor.
    The short description is printed on same line as the program name
    
    @param  program:str          The name of the program
    @param  description:str      Short, single-line, description of the program
    @param  usage:str            Formated, multi-line, usage text
    @param  longdescription:str  Long, multi-line, description of the program, may be `None`
    '''
    def __init__(self, program, description, usage, longdescription = None):
        self.linuxvt = ('TERM' in os.environ) and (os.environ['TERM'] == 'linux')
        self.__program = program
        self.__description = description
        self.__usage = usage
        self.__longdescription = longdescription
        self.__arguments = []
        self.opts = {}
        self.optmap = {}
    
    
    '''
    Add option that takes no arguments
    
    @param  alternatives:list<str>  Option names
    @param  help:str                Short description, use `None` to hide the option
    '''
    def add_argumentless(self, alternatives, help = None):
        self.__arguments.append((ARGUMENTLESS, alternatives, None, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, ARGUMENTLESS)
    
    '''
    Add option that takes one argument
    
    @param  alternatives:list<str>  Option names
    @param  arg:str                 The name of the takes argument, one word
    @param  help:str                Short description, use `None` to hide the option
    '''
    def add_argumented(self, alternatives, arg, help = None):
        self.__arguments.append((ARGUMENTED, alternatives, arg, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, ARGUMENTED)
    
    '''
    Add option that takes all following argument
    
    @param  alternatives:list<str>  Option names
    @param  arg:str                 The name of the takes arguments, one word
    @param  help:str                Short description, use `None` to hide the option
    '''
    def add_variadic(self, alternatives, arg, help = None):
        self.__arguments.append((VARIADIC, alternatives, arg, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, VARIADIC)
    
    
    '''
    Parse arguments
    
    @param   args:list<str>  The command line arguments, should include the execute file at index 0, `sys.argv` is default
    @return  :bool           Whether no unrecognised option is used
    '''
    def parse(self, argv = sys.argv):
        self.argcount = len(argv) - 1
        self.files = []
        
        argqueue = []
        optqueue = []
        deque = []
        for arg in argv[1:]:
            deque.append(arg)
        
        dashed = False
        tmpdashed = False
        get = 0
        dontget = 0
        self.rc = True
        
        self.unrecognisedCount = 0
        def unrecognised(arg):
            self.unrecognisedCount += 1
            if self.unrecognisedCount <= 5:
                sys.stderr.write('%s: warning: unrecognised option %s\n' % (self.__program, arg))
            self.rc = False
        
        while len(deque) != 0:
            arg = deque[0]
            deque = deque[1:]
            if (get > 0) and (dontget == 0):
                get -= 1
                argqueue.append(arg)
            elif tmpdashed:
                self.files.append(arg)
                tmpdashed = False
            elif dashed:        self.files.append(arg)
            elif arg == '++':   tmpdashed = True
            elif arg == '--':   dashed = True
            elif (len(arg) > 1) and (arg[0] in ('-', '+')):
                if (len(arg) > 2) and (arg[:2] in ('--', '++')):
                    if dontget > 0:
                        dontget -= 1
                    elif (arg in self.optmap) and (self.optmap[arg][1] == ARGUMENTLESS):
                        optqueue.append(arg)
                        argqueue.append(None)
                    elif '=' in arg:
                        arg_opt = arg[:arg.index('=')]
                        if (arg_opt in self.optmap) and (self.optmap[arg_opt][1] >= ARGUMENTED):
                            optqueue.append(arg_opt)
                            argqueue.append(arg[arg.index('=') + 1:])
                            if self.optmap[arg_opt][1] == VARIADIC:
                                dashed = True
                        else:
                            unrecognised(arg)
                    elif (arg in self.optmap) and (self.optmap[arg][1] == ARGUMENTED):
                        optqueue.append(arg)
                        get += 1
                    elif (arg in self.optmap) and (self.optmap[arg][1] == VARIADIC):
                        optqueue.append(arg)
                        argqueue.append(None)
                        dashed = True
                    else:
                        unrecognised(arg)
                else:
                    sign = arg[0]
                    i = 1
                    n = len(arg)
                    while i < n:
                        narg = sign + arg[i]
                        i += 1
                        if (narg in self.optmap):
                            if self.optmap[narg][1] == ARGUMENTLESS:
                                optqueue.append(narg)
                                argqueue.append(None)
                            elif self.optmap[narg][1] == ARGUMENTED:
                                optqueue.append(narg)
                                nargarg = arg[i:]
                                if len(nargarg) == 0:
                                    get += 1
                                else:
                                    argqueue.append(nargarg)
                                break
                            elif self.optmap[narg][1] == VARIADIC:
                                optqueue.append(narg)
                                nargarg = arg[i:]
                                argqueue.append(nargarg if len(nargarg) > 0 else None)
                                dashed = True
                                break
                        else:
                            unrecognised(narg)
            else:
                self.files.append(arg)
        
        i = 0
        n = len(optqueue)
        while i < n:
            opt = optqueue[i]
            arg = argqueue[i] if len(argqueue) > i else None
            i += 1
            opt = self.optmap[opt][0]
            if (opt not in self.opts) or (self.opts[opt] is None):
                self.opts[opt] = []
            if len(argqueue) >= i:
                self.opts[opt].append(arg)
        
        for arg in self.__arguments:
            if arg[0] == VARIADIC:
                varopt = self.opts[arg[1][0]]
                if varopt is not None:
                    additional = ','.join(self.files).split(',') if len(self.files) > 0 else []
                    if varopt[0] is None:
                        self.opts[arg[1][0]] = additional
                    else:
                        self.opts[arg[1][0]] = varopt[0].split(',') + additional
                    self.files = []
                    break
        
        self.message = ' '.join(self.files) if len(self.files) > 0 else None
        
        if self.unrecognisedCount > 5:
            sys.stderr.write('%s: warning: %i more unrecognised %s\n' % (self.unrecognisedCount - 5, 'options' if self.unrecognisedCount == 6 else 'options'))
        
        return self.rc
    
    
    '''
    Prints a colourful help message
    '''
    def help(self):
        print('\033[1m%s\033[21m %s %s' % (self.__program, '-' if self.linuxvt else '—', self.__description))
        print()
        if self.__longdescription is not None:
            print(self.__longdescription)
        print()
        
        print('\033[1mUSAGE:\033[21m', end='')
        first = True
        for line in self.__usage.split('\n'):
            if first:
                first = False
            else:
                print('    or', end='')
            print('\t%s' % (line))
        print()
        
        maxfirstlen = []
        for opt in self.__arguments:
            opt_alts = opt[1]
            opt_help = opt[3]
            if opt_help is None:
                continue
            first = opt_alts[0]
            last = opt_alts[-1]
            if first is not last:
                maxfirstlen.append(first)
        maxfirstlen = len(max(maxfirstlen, key = len))
        
        print('\033[1mSYNOPSIS:\033[21m')
        (lines, lens) = ([], [])
        for opt in self.__arguments:
            opt_type = opt[0]
            opt_alts = opt[1]
            opt_arg = opt[2]
            opt_help = opt[3]
            if opt_help is None:
                continue
            (line, l) = ('', 0)
            first = opt_alts[0]
            last = opt_alts[-1]
            alts = ['', last] if first is last else [first, last]
            alts[0] += ' ' * (maxfirstlen - len(alts[0]))
            for opt_alt in alts:
                if opt_alt is alts[-1]:
                    line += '%colour%' + opt_alt
                    l += len(opt_alt)
                    if   opt_type == ARGUMENTED:  line += ' \033[4m%s\033[24m'      % (opt_arg);  l += len(opt_arg) + 1
                    elif opt_type == VARIADIC:    line += ' [\033[4m%s\033[24m...]' % (opt_arg);  l += len(opt_arg) + 6
                else:
                    line += '    \033[2m%s\033[22m  ' % (opt_alt)
                    l += len(opt_alt) + 6
            lines.append(line)
            lens.append(l)
        
        col = max(lens)
        col += 8 - ((col - 4) & 7)
        index = 0
        for opt in self.__arguments:
            opt_help = opt[3]
            if opt_help is None:
                continue
            first = True
            colour = '36' if (index & 1) == 0 else '34'
            print(lines[index].replace('%colour%', '\033[%s;1m' % (colour)), end=' ' * (col - lens[index]))
            for line in opt_help.split('\n'):
                if first:
                    first = False
                    print('%s' % (line), end='\033[21;39m\n')
                else:
                    print('%s\033[%sm%s\033[39m' % (' ' * col, colour, line))
            index += 1
        
        print()



'''
Balloon format class
'''
class Balloon():
    '''
    Constructor
    
    @param  link:str        The \-directional balloon line character
    @param  linkmirror:str  The /-directional balloon line character
    @param  ww:str          See the info manual
    @param  ee:str          See the info manual
    @param  nw:list<str>    See the info manual
    @param  nnw:list<str>   See the info manual
    @param  n:list<str>     See the info manual
    @param  nne:list<str>   See the info manual
    @param  ne:list<str>    See the info manual
    @param  nee:str         See the info manual
    @param  e:str           See the info manual
    @param  see:str         See the info manual
    @param  se:list<str>    See the info manual
    @param  sse:list<str>   See the info manual
    @param  s:list<str>     See the info manual
    @param  ssw:list<str>   See the info manual
    @param  sw:list<str>    See the info manual
    @param  sww:str         See the info manual
    @param  w:str           See the info manual
    @param  nww:str         See the info manual
    '''
    def __init__(self, link, linkmirror, ww, ee, nw, nnw, n, nne, ne, nee, e, see, se, sse, s, ssw, sw, sww, w, nww):
        (self.link, self.linkmirror) = (link, linkmirror)
        (self.ww, self.ee) = (ww, ee)
        (self.nw, self.ne, self.se, self.sw) = (nw, ne, se, sw)
        (self.nnw, self.n, self.nne) = (nnw, n, nne)
        (self.nee, self.e, self.see) = (nee, e, see)
        (self.sse, self.s, self.ssw) = (sse, s, ssw)
        (self.sww, self.w, self.nww) = (sww, w, nww)
        
        _ne = max(ne, key = UCS.dispLen)
        _nw = max(nw, key = UCS.dispLen)
        _se = max(se, key = UCS.dispLen)
        _sw = max(sw, key = UCS.dispLen)
        
        minE = UCS.dispLen(max([_ne, nee, e, see, _se, ee], key = UCS.dispLen))
        minW = UCS.dispLen(max([_nw, nww, e, sww, _sw, ww], key = UCS.dispLen))
        minN = len(max([ne, nne, n, nnw, nw], key = len))
        minS = len(max([se, sse, s, ssw, sw], key = len))
        
        self.minwidth  = minE + minE
        self.minheight = minN + minS
    
    
    '''
    Generates a balloon with a message
    
    @param   minw:int          The minimum number of columns of the balloon
    @param   minh:int          The minimum number of lines of the balloon
    @param   lines:list<str>   The text lines to display
    @param   lencalc:int(str)  Function used to compute the length of a text line
    @return  :str              The balloon as a formated string
    '''
    def get(self, minw, minh, lines, lencalc):
        h = self.minheight + len(lines)
        w = self.minwidth + lencalc(max(lines, key = lencalc))
        if w < minw:  w = minw
        if h < minh:  h = minh
        
        if len(lines) > 1:
            (ws, es) = ({0 : self.nww, len(lines) - 1 : self.sww}, {0 : self.nee, len(lines) - 1 : self.see})
            for j in range(1, len(lines) - 1):
                ws[j] = self.w
                es[j] = self.e
        else:
            (ws, es) = ({0 : self.ww}, {0 : self.ee})
        
        rc = []
        
        for j in range(0, len(self.n)):
            outer = UCS.dispLen(self.nw[j]) + UCS.dispLen(self.ne[j])
            inner = UCS.dispLen(self.nnw[j]) + UCS.dispLen(self.nne[j])
            if outer + inner <= w:
                rc.append(self.nw[j] + self.nnw[j] + self.n[j] * (w - outer - inner) + self.nne[j] + self.ne[j])
            else:
                rc.append(self.nw[j] + self.n[j] * (w - outer) + self.ne[j])
        
        for j in range(0, len(lines)):
            rc.append(ws[j] + lines[j] + ' ' * (w - lencalc(lines[j]) - UCS.dispLen(self.w) - UCS.dispLen(self.e)) + es[j])
        
        for j in range(0, len(self.s)):
            outer = UCS.dispLen(self.sw[j]) + UCS.dispLen(self.se[j])
            inner = UCS.dispLen(self.ssw[j]) + UCS.dispLen(self.sse[j])
            if outer + inner <= w:
                rc.append(self.sw[j] + self.ssw[j] + self.s[j] * (w - outer - inner) + self.sse[j] + self.se[j])
            else:
                rc.append(self.sw[j] + self.s[j] * (w - outer) + self.se[j])
        
        return '\n'.join(rc)



'''
Super-ultra-extreme-awesomazing replacement for cowsay
'''
class Backend():
    '''
    Constructor
    
    @param  message:str        The message spoken by the pony
    @param  ponyfile:str       The pony file
    @param  wrapcolumn:int     The column at where to wrap the message, `None` for no wrapping
    @param  width:int          The width of the screen, `None` if truncation should not be applied
    @param  balloon:Balloon    The balloon style object, `None` if only the pony should be printed
    @param  hyphen:str         How hyphens added by the wordwrapper should be printed
    @param  linkcolour:str     How to colour the link character, empty string if none
    @param  ballooncolour:str  How to colour the balloon, empty string if none
    @param  mode:str           Mode string for the pony
    @parma  infolevel:int      2 if ++info is used, 1 if --info is used and 0 otherwise
    '''
    def __init__(self, message, ponyfile, wrapcolumn, width, balloon, hyphen, linkcolour, ballooncolour, mode, infolevel):
        self.message = message
        self.ponyfile = ponyfile
        self.wrapcolumn = None if wrapcolumn is None else wrapcolumn - (0 if balloon is None else balloon.minwidth)
        self.width = width
        self.balloon = balloon
        self.hyphen = hyphen
        self.ballooncolour = ballooncolour
        self.mode = mode
        self.balloontop = 0
        self.balloonbottom = 0
        self.infolevel = infolevel
        
        if self.balloon is not None:
            self.link = {'\\' : linkcolour + self.balloon.link,
                         '/'  : linkcolour + self.balloon.linkmirror}
        else:
            self.link = {}
        
        self.output = ''
        self.pony = None
    
    
    '''
    Process all data
    '''
    def parse(self):
        self.__loadFile()
        
        if self.pony.startswith('$$$\n'):
            self.pony = self.pony[4:]
            if self.pony.startswith('$$$\n'):
                infoend = 4
                info = ''
            else:
                infoend = self.pony.index('\n$$$\n')
                info = self.pony[:infoend]
                infoend += 5
            if self.infolevel == 2:
                self.message = Backend.formatInfo(info)
            elif self.infolevel == 1:
                self.pony = Backend.formatInfo(info).replace('$', '$$')
            else:
                info = info.split('\n')
                for line in info:
                    sep = line.find(':')
                    if sep > 0:
                        key = line[:sep].strip()
                        if key == 'BALLOON TOP':
                            value = line[sep + 1:].strip()
                            if len(value) > 0:
                                self.balloontop = int(value)
                        if key == 'BALLOON BOTTOM':
                            value = line[sep + 1:].strip()
                            if len(value) > 0:
                                self.balloonbottom = int(value)
                printinfo(info)
                self.pony = self.pony[infoend:]
        elif self.infolevel == 2:
            self.message = '\033[01;31mI am the mysterious mare...\033[21;39m'
        elif self.infolevel == 1:
            self.pony = 'There is not metadata for this pony file'
        self.pony = self.mode + self.pony
        
        self.__expandMessage()
        self.__unpadMessage()
        self.__processPony()
        self.__truncate()
    
    
    '''
    Format metadata to be nicely printed, this include bold keys
    
    @param   info:str  The metadata
    @return  :str      The metadata nicely formated
    '''
    @staticmethod
    def formatInfo(info):
        info = info.split('\n')
        tags = ''
        comment = ''
        for line in info:
            sep = line.find(':')
            if sep > 0:
                key = line[:sep]
                test = key
                for c in 'ABCDEFGHIJKLMN OPQRSTUVWXYZ':
                    test = test.replace(c, '')
                if (len(test) == 0) and (len(key.replace(' ', '')) > 0):
                    value = line[sep + 1:].strip()
                    line = '\033[1m%s\033[21m: %s\n' % (key.strip(), value)
                    tags += line
                    continue
            comment += '\n' + line
        comment = comment.lstrip('\n')
        if len(comment) > 0:
            comment = '\n' + comment
        return tags + comment
    
    
    '''
    Remove padding spaces fortune cookies are padded with whitespace (damn featherbrains)
    '''
    def __unpadMessage(self):
        lines = self.message.split('\n')
        for spaces in (8, 4, 2, 1):
            padded = True
            for line in lines:
                if not line.startswith(' ' * spaces):
                    padded = False
                    break
            if padded:
                for i in range(0, len(lines)):
                    line = lines[i]
                    while line.startswith(' ' * spaces):
                        line = line[spaces:]
                    lines[i] = line
        lines = [line.rstrip(' ') for line in lines]
        self.message = '\n'.join(lines)
    
    
    '''
    Converts all tabs in the message to spaces by expanding
    '''
    def __expandMessage(self):
        lines = self.message.split('\n')
        buf = ''
        for line in lines:
            (i, n, x) = (0, len(line), 0)
            while i < n:
                c = line[i]
                i += 1
                if c == '\033':
                    colour = Backend.getcolour(line, i - 1)
                    i += len(colour) - 1
                    buf += colour
                elif c == '\t':
                    nx = 8 - (x & 7)
                    buf += ' ' * nx
                    x += nx
                else:
                    buf += c
                    if not UCS.isCombining(c):
                        x += 1
            buf += '\n'
        self.message = buf[:-1]
    
    
    '''
    Loads the pony file
    '''
    def __loadFile(self):
        with open(self.ponyfile, 'rb') as ponystream:
            self.pony = ponystream.read().decode('utf8', 'replace')
    
    
    '''
    Truncate output to the width of the screen
    '''
    def __truncate(self):
        if self.width is None:
            return
        lines = self.output.split('\n')
        self.output = ''
        for line in lines:
            (i, n, x) = (0, len(line), 0)
            while i < n:
                c = line[i]
                i += 1
                if c == '\033':
                    colour = Backend.getcolour(line, i - 1)
                    i += len(colour) - 1
                    self.output += colour
                else:
                    if x < self.width:
                        self.output += c
                        if not UCS.isCombining(c):
                            x += 1
            self.output += '\n'
        self.output = self.output[:-1]
    
    
    '''
    Process the pony file and generate output to self.output
    '''
    def __processPony(self):
        self.output = ''
        
        AUTO_PUSH = '\033[01010~'
        AUTO_POP  = '\033[10101~'
        
        variables = {'' : '$'}
        for key in self.link:
            variables[key] = AUTO_PUSH + self.link[key] + AUTO_POP
        
        indent = 0
        dollar = None
        balloonLines = None
        colourstack = ColourStack(AUTO_PUSH, AUTO_POP)
        
        (i, n, lineindex, skip, nonskip) = (0, len(self.pony), 0, 0, 0)
        while i < n:
            c = self.pony[i]
            if c == '\t':
                n += 7 - (indent & 7)
                ed = ' ' * (8 - (indent & 7))
                c = ' '
                self.pony = self.pony[:i] + ed + self.pony[i + 1:]
            i += 1
            if c == '$':
                if dollar is not None:
                    if '=' in dollar:
                        name = dollar[:dollar.find('=')]
                        value = dollar[dollar.find('=') + 1:]
                        variables[name] = value
                    elif not dollar.startswith('balloon'):
                        data = variables[dollar].replace('$', '$$')
                        if data == '$$': # if not handled specially we will get an infinity loop
                            if (skip == 0) or (nonskip > 0):
                                if nonskip > 0:
                                    nonskip -= 1
                                self.output += '$'
                                indent += 1
                            else:
                                skip -= 1
                        else:
                            n += len(data)
                            self.pony = self.pony[:i] + data + self.pony[i:]
                    elif self.balloon is not None:
                        (w, h, x, justify) = ('0', 0, 0, None)
                        props = dollar[7:]
                        if len(props) > 0:
                            if ',' in props:
                                if props[0] is not ',':
                                    w = props[:props.index(',')]
                                h = int(props[props.index(',') + 1:])
                            else:
                                w = props
                        if 'l' in w:
                            (x, w) = (int(w[:w.find('l')]), int(w[w.find('l') + 1:]))
                            justify = 'l'
                            w -= x;
                        elif 'c' in w:
                            (x, w) = (int(w[:w.find('c')]), int(w[w.find('c') + 1:]))
                            justify = 'c'
                            w -= x;
                        elif 'r' in w:
                            (x, w) = (int(w[:w.find('r')]), int(w[w.find('r') + 1:]))
                            justify = 'r'
                            w -= x;
                        else:
                            w = int(w)
                        balloon = self.__getballoon(w, h, x, justify, indent)
                        balloon = balloon.split('\n')
                        balloon = [AUTO_PUSH + self.ballooncolour + item + AUTO_POP for item in balloon]
                        for b in balloon[0]:
                            self.output += b + colourstack.feed(b)
                        if lineindex == 0:
                            balloonpre = '\n' + (' ' * indent)
                            for line in balloon[1:]:
                                self.output += balloonpre;
                                for b in line:
                                    self.output += b + colourstack.feed(b);
                            indent = 0
                        elif len(balloon) > 1:
                            balloonLines = balloon
                            balloonLine = 0
                            balloonIndent = indent
                            indent += Backend.len(balloonLines[0])
                            balloonLines[0] = None
                    dollar = None
                else:
                    dollar = ''
            elif dollar is not None:
                if c == '\033':
                    c = self.pony[i]
                    i += 1
                dollar += c
            elif c == '\033':
                colour = Backend.getcolour(self.pony, i - 1)
                for b in colour:
                    self.output += b + colourstack.feed(b);
                i += len(colour) - 1
            elif c == '\n':
                self.output += c
                indent = 0
                (skip, nonskip) = (0, 0)
                lineindex += 1
                if balloonLines is not None:
                    balloonLine += 1
                    if balloonLine == len(balloonLines):
                        balloonLines = None
            else:
                if (balloonLines is not None) and (balloonLines[balloonLine] is not None) and (balloonIndent == indent):
                    data = balloonLines[balloonLine]
                    datalen = Backend.len(data)
                    skip += datalen
                    nonskip += datalen
                    data = data.replace('$', '$$')
                    n += len(data)
                    self.pony = self.pony[:i] + data + self.pony[i:]
                    balloonLines[balloonLine] = None
                else:
                    if (skip == 0) or (nonskip > 0):
                        if nonskip > 0:
                            nonskip -= 1
                        self.output += c + colourstack.feed(c);
                        if not UCS.isCombining(c):
                            indent += 1
                    else:
                        skip -= 1
        
        if balloonLines is not None:
            for line in balloonLines[balloonLine:]:
                data = ' ' * (balloonIndent - indent) + line + '\n'
                for b in data:
                    self.output += b + colourstack.feed(b);
                indent = 0
        
        self.output = self.output.replace(AUTO_PUSH, '').replace(AUTO_POP, '')
        
        if self.balloon is not None:
            if (self.balloontop > 0) or (self.balloonbottom > 0):
                self.output = self.output.split('\n')
                self.output = self.output[self.balloontop : ~(self.balloonbottom)]
                self.output = '\n'.join(self.output)
    
    
    '''
    Gets colour code att the currect offset in a buffer
    
    @param   input:str   The input buffer
    @param   offset:int  The offset at where to start reading, a escape must begin here
    @return  :str        The escape sequence
    '''
    @staticmethod
    def getcolour(input, offset):
        (i, n) = (offset, len(input))
        rc = input[i]
        i += 1
        if i == n: return rc
        c = input[i]
        i += 1
        rc += c
        
        if c == ']':
            if i == n: return rc
            c = input[i]
            i += 1
            rc += c
            if c == 'P':
                di = 0
                while (di < 7) and (i < n):
                    c = input[i]
                    i += 1
                    di += 1
                    rc += c
            while c == '0':
                c = input[i]
                i += 1
                rc += c
            if c == '4':
                c = input[i]
                i += 1
                rc += c
                if c == ';':
                    c = input[i]
                    i += 1
                    rc += c
                    while c != '\\':
                        c = input[i]
                        i += 1
                        rc += c
        elif c == '[':
            while i < n:
                c = input[i]
                i += 1
                rc += c
                if (c == '~') or (('a' <= c) and (c <= 'z')) or (('A' <= c) and (c <= 'Z')):
                    break
        
        return rc
    
    
    '''
    Calculates the number of visible characters in a text
    
    @param   input:str  The input buffer
    @return  :int       The number of visible characters
    '''
    @staticmethod
    def len(input):
        (rc, i, n) = (0, 0, len(input))
        while i < n:
            c = input[i]
            if c == '\033':
                i += len(Backend.getcolour(input, i))
            else:
                i += 1
                if not UCS.isCombining(c):
                    rc += 1
        return rc
    
    
    '''
    Generates a balloon with the message
    
    @param   width:int      The minimum width of the balloon
    @param   height:int     The minimum height of the balloon
    @param   innerleft:int  The left column of the required span, excluding that of `left`
    @param   justify:str    Balloon placement justification, 'c' → centered,
                            'l' → left (expand to right), 'r' → right (expand to left)
    @param   left:int       The column where the balloon starts
    @return  :str           The balloon the the message as a string
    '''
    def __getballoon(self, width, height, innerleft, justify, left):
        wrap = None
        if self.wrapcolumn is not None:
            wrap = self.wrapcolumn - left
            if wrap < 8:
                wrap = 8
        
        msg = self.message
        if wrap is not None:
            msg = self.__wrapMessage(msg, wrap)
        
        msg = msg.replace('\n', '\033[0m%s\n' % (self.ballooncolour)) + '\033[0m' + self.ballooncolour
        msg = msg.split('\n')
        
        extraleft = 0
        if justify is not None:
            msgwidth = self.len(max(msg, key = self.len)) + self.balloon.minwidth
            extraleft = innerleft
            if msgwidth > width:
                if (justify == 'l') and (wrap is not None):
                    if innerleft + msgwidth > wrap:
                        extraleft -= msgwidth - wrap
                elif justify == 'r':
                    extraleft -= msgwidth - width
                elif justify == 'c':
                    extraleft -= (msgwidth - width) >> 1
                    if extraleft < 0:
                        extraleft = 0
                    if wrap is not None:
                        if extraleft + msgwidth > wrap:
                            extraleft -= msgwidth - wrap
        
        rc = self.balloon.get(width, height, msg, Backend.len);
        if extraleft > 0:
            rc = ' ' * extraleft + rc.replace('\n', '\n' + ' ' * extraleft)
        return rc
    
    
    '''
    Wraps the message
    
    @param   message:str  The message to wrap
    @param   wrap:int     The width at where to force wrapping
    @return  :str         The message wrapped
    '''
    def __wrapMessage(self, message, wrap):
        wraplimit = os.environ['PONYSAY_WRAP_LIMIT'] if 'PONYSAY_WRAP_LIMIT' in os.environ else ''
        wraplimit = 8 if len(wraplimit) == 0 else int(wraplimit)
        
        wrapexceed = os.environ['PONYSAY_WRAP_EXCEED'] if 'PONYSAY_WRAP_EXCEED' in os.environ else ''
        wrapexceed = 5 if len(wrapexceed) == 0 else int(wrapexceed)
        
        buf = ''
        try:
            AUTO_PUSH = '\033[01010~'
            AUTO_POP  = '\033[10101~'
            msg = message.replace('\n', AUTO_PUSH + '\n' + AUTO_POP);
            cstack = ColourStack(AUTO_PUSH, AUTO_POP)
            for c in msg:
                buf += c + cstack.feed(c)
            lines = buf.replace(AUTO_PUSH, '').replace(AUTO_POP, '').split('\n')
            buf = ''
            
            for line in lines:
                b = [None] * len(line)
                map = {0 : 0}
                (bi, cols, w) = (0, 0, wrap)
                (indent, indentc) = (-1, 0)
                
                (i, n) = (0, len(line))
                while i <= n:
                    d = None
                    if i < n:
                        d = line[i]
                    i += 1
                    if d == '\033':
                        ## Invisible stuff
                        i -= 1
                        colourseq = Backend.getcolour(line, i)
                        b[bi : bi + len(colourseq)] = colourseq
                        i += len(colourseq)
                        bi += len(colourseq)
                    elif (d is not None) and (d != ' '):
                        ## Fetch word
                        if indent == -1:
                            indent = i - 1
                            for j in range(0, indent):
                                if line[j] == ' ':
                                    indentc += 1
                        b[bi] = d
                        bi += 1
                        if (not UCS.isCombining(d)) and (d != '­'):
                            cols += 1
                        map[cols] = bi
                    else:
                        ## Wrap?
                        mm = 0
                        bisub = 0
                        iwrap = wrap - (0 if indent == 1 else indentc)
                        
                        while ((w > wraplimit) and (cols > w + wrapexceed)) or (cols > iwrap):
                            ## wrap
                            x = w;
                            if mm + x not in map: # Too much whitespace?
                                cols = 0
                                break
                            nbsp = b[map[mm + x]] == ' '
                            m = map[mm + x]
                            
                            if ('­' in b[bisub : m]) and not nbsp:
                                hyphen = m - 1
                                while b[hyphen] != '­':
                                    hyphen -= 1
                                while map[mm + x] > hyphen: ## Only looking backward, if foreward is required the word is probabily not hyphenated correctly
                                    x -= 1
                                x += 1
                                m = map[mm + x]
                            
                            mm += x - (0 if nbsp else 1) ## − 1 so we have space for a hythen
                            
                            for bb in b[bisub : m]:
                                buf += bb
                            buf += '\n' if nbsp else '\0\n'
                            cols -= x - (0 if nbsp else 1)
                            bisub = m
                            
                            w = iwrap
                            if indent != -1:
                                buf += line[:indent]
                        
                        for j in range(bisub, bi):
                            b[j - bisub] = b[j]
                        bi -= bisub
                        
                        if cols > w:
                            buf += '\n'
                            w = wrap
                            if indent != -1:
                                buf += line[:indent]
                                w -= indentc
                        for bb in b[:bi]:
                            if bb is not None:
                                buf += bb
                        w -= cols
                        cols = 0
                        bi = 0
                        if d is None:
                            i += 1
                        else:
                            if w > 0:
                                buf += ' '
                                w -= 1
                            else:
                                buf += '\n'
                                w = wrap
                                if indent != -1:
                                    buf + line[:indent]
                                    w -= indentc
                buf += '\n'
            
            rc = '\n'.join(line.rstrip() for line in buf[:-1].split('\n'));
            rc = rc.replace('­', ''); # remove soft hyphens
            rc = rc.replace('\0', '%s%s%s' % (AUTO_PUSH, self.hyphen, AUTO_POP))
            return rc
        except Exception as err:
            import traceback
            errormessage = ''.join(traceback.format_exception(type(err), err, None))
            rc = '\n'.join(line.rstrip() for line in buf.split('\n'));
            rc = rc.replace('\0', '%s%s%s' % (AUTO_PUSH, self.hyphen, AUTO_POP))
            errormessage += '\n---- WRAPPING BUFFER ----\n\n' + rc
            try:
                if os.readlink('/proc/self/fd/2') != os.readlink('/proc/self/fd/1'):
                    printerr(errormessage, end='')
                    return message
            except:
                pass
            return message + '\n\n\033[0;1;31m---- EXCEPTION IN PONYSAY WHILE WRAPPING ----\033[0m\n\n' + errormessage


'''
ANSI colour stack

This is used to make layers with independent coloursations
'''
class ColourStack():
    '''
    Constructor
    
    @param  autopush:str  String that, when used, will create a new independently colourised layer
    @param  autopop:str   String that, when used, will end the current layer and continue of the previous layer
    '''
    def __init__(self, autopush, autopop):
        self.autopush = autopush
        self.autopop  = autopop
        self.lenpush  = len(autopush)
        self.lenpop   = len(autopop)
        self.bufproto = ' ' * (self.lenpush if self.lenpush > self.lenpop else self.lenpop)
        self.stack    = []
        self.push()
        self.seq      = None
    
    
    '''
    Create a new independently colourised layer
    
    @return  :str  String that should be inserted into your buffer
    '''
    def push(self):
        self.stack.insert(0, [self.bufproto, None, None, [False] * 9])
        if len(self.stack) == 1:
            return None
        return '\033[0m'
    
    
    '''
    End the current layer and continue of the previous layer
    
    @return  :str  String that should be inserted into your buffer
    '''
    def pop(self):
        old = self.stack.pop(0)
        rc = '\033[0;'
        if len(self.stack) == 0: # last resort in case something made it pop too mush
            push()
        new = self.stack[0]
        if new[1] is not None:  rc += new[1] + ';'
        if new[2] is not None:  rc += new[2] + ';'
        for i in range(0, 9):
            if new[3][i]:
                rc += str(i + 1) + ';'
        return rc[:-1] + 'm'
    
    
    '''
    Use this, in sequence, for which character in your buffer that contains yor autopush and autopop
    string, the automatically get push and pop string to insert after each character
    
    @param   :chr  One character in your buffer
    @return  :str  The text to insert after the input character
    '''
    def feed(self, char):
        if self.seq is not None:
            self.seq += char
            if (char == '~') or (('a' <= char) and (char <= 'z')) or (('A' <= char) and (char <= 'Z')):
                if (self.seq[0] == '[') and (self.seq[-1] == 'm'):
                    self.seq = self.seq[1:-1].split(';')
                    (i, n) = (0, len(self.seq))
                    while i < n:
                        part = self.seq[i]
                        p = 0 if part == '' else int(part)
                        i += 1
                        if p == 0:                       self.stack[0][1:] = [None, None, [False] * 9]
                        elif (1 <= p) and (p <= 9):      self.stack[0][3][p - 1] = True
                        elif (21 <= p) and (p <= 29):    self.stack[0][3][p - 21] = False
                        elif p == 39:                    self.stack[0][1] = None
                        elif p == 49:                    self.stack[0][2] = None
                        elif (30 <= p) and (p <= 37):    self.stack[0][1] = part
                        elif (90 <= p) and (p <= 97):    self.stack[0][1] = part
                        elif (40 <= p) and (p <= 47):    self.stack[0][2] = part
                        elif (100 <= p) and (p <= 107):  self.stack[0][2] = part
                        elif p == 38:
                            self.stack[0][1] = '%s;%s;%s' % (part, self.seq[i], self.seq[i + 1])
                            i += 2
                        elif p == 48:
                            self.stack[0][2] = '%s;%s;%s' % (part, self.seq[i], self.seq[i + 1])
                            i += 2
                self.seq = None
        elif char == '\033':
            self.seq = ''
        buf = self.stack[0][0]
        buf = buf[1:] + char
        rc = ''
        if   buf[-self.lenpush:] == self.autopush:  rc = self.push()
        elif buf[-self.lenpop:]  == self.autopop:   rc = self.pop()
        self.stack[0][0] = buf
        return rc



'''
UCS utility class
'''
class UCS():
    '''
    Checks whether a character is a combining character
    
    @param   char:chr  The character to test
    @return  :bool     Whether the character is a combining character
    '''
    @staticmethod
    def isCombining(char):
        o = ord(char)
        if (0x0300 <= o) and (o <= 0x036F):  return True
        if (0x20D0 <= o) and (o <= 0x20FF):  return True
        if (0x1DC0 <= o) and (o <= 0x1DFF):  return True
        if (0xFE20 <= o) and (o <= 0xFE2F):  return True
        return False
    
    
    '''
    Gets the number of combining characters in a string
    
    @param   string:str  A text to count combining characters in
    @return  :int        The number of combining characters in the string
    '''
    @staticmethod
    def countCombining(string):
        rc = 0
        for char in string:
            if UCS.isCombining(char):
                rc += 1
        return rc
    
    
    '''
    Gets length of a string not counting combining characters
    
    @param   string:str  The text of which to determine the monospaced width
    @return              The determine the monospaced width of the text, provided it does not have escape sequnces
    '''
    @staticmethod
    def dispLen(string):
        return len(string) - UCS.countCombining(string)



'''
Class used for correcting spellos and typos,

Note that this implementation will not find that correctly spelled word are correct faster than it corrects words.
It is also limited to words of size 0 to 127 (inclusive)
'''
class SpelloCorrecter(): # Naïvely and quickly proted and adapted from optimised Java, may not be the nicest, or even fast, Python code
    '''
    Constructor
    
    @param  directories:list<str>  List of directories that contains the file names with the correct spelling
    @param  ending:str             The file name ending of the correctly spelled file names, this is removed for the name
    '''
    def __init__(self, directories, ending):
        self.weights = {'k' : {'c' : 0.25, 'g' : 0.75, 'q' : 0.125},
                        'c' : {'k' : 0.25, 'g' : 0.75, 's' : 0.5, 'z' : 0.5, 'q' : 0.125},
                        's' : {'z' : 0.25, 'c' : 0.5},
                        'z' : {'s' : 0.25, 'c' : 0.5},
                        'g' : {'k' : 0.75, 'c' : 0.75, 'q' : 0.9},
                        'o' : {'u' : 0.5},
                        'u' : {'o' : 0.5, 'v' : 0.75, 'w' : 0.5},
                        'b' : {'v' : 0.75},
                        'v' : {'b' : 0.75, 'w' : 0.5, 'u' : 0.7},
                        'w' : {'v' : 0.5, 'u' : 0.5},
                        'q' : {'c' : 0.125, 'k' : 0.125, 'g' : 0.9}}
        
        self.corrections = None
        self.dictionary = [None] * 513
        self.reusable = [0] * 512
        self.dictionaryEnd = 512
        self.closestDistance = 0
        
        self.M = [None] * 128
        for y in range(0, 128):
            self.M[y] = [0] * 128
            self.M[y][0] = y
        m0 = self.M[0]
        x = 127
        while x > -1:
            m0[x] = x
            x -= 1
        
        previous = ''
        self.dictionary[-1] = previous;
        
        for directory in directories:
            for filename in os.listdir(directory):
                if (not endswith(filename, ending)) or (len(filename) - len(ending) > 127):
                    continue
                proper = filename[:-len(ending)]
                
                if self.dictionaryEnd == 0:
                    self.dictionaryEnd = len(self.dictionary)
                    self.reusable = [0] * self.dictionaryEnd + self.reusable
                    self.dictionary = [None] * self.dictionaryEnd + self.dictionary
                
                self.dictionaryEnd -= 1
                self.dictionary[self.dictionaryEnd] = proper
                
                prevCommon = min(len(previous), len(proper))
                for i in range(0, prevCommon):
                    if previous[i] != proper[i]:
                        prevCommon = i
                        break
                previous = proper
                self.reusable[self.dictionaryEnd] = prevCommon
        #part = self.dictionary[self.dictionaryEnd : len(self.dictionary) - 1]
        #part.sort()
        #self.dictionary[self.dictionaryEnd : len(self.dictionary) - 1] = part
        #
        #index = len(self.dictionary) - 1
        #while index >= self.dictionaryEnd:
        #    proper = self.dictionary[index]
        #    prevCommon = min(len(previous), len(proper))
        #    for i in range(0, prevCommon):
        #        if previous[i] != proper[i]:
        #            prevCommon = i
        #            break
        #    previous = proper
        #    self.reusable[self.dictionaryEnd] = prevCommon
        #    index -= 1;    
    
    
    '''
    Finds the closests correct spelled word
    
    @param   used:str                               The word to correct
    @return  (words, distance):(list<string>, int)  A list the closest spellings and the weighted distance
    '''
    def correct(self, used):
        if len(used) > 127:
            return ([used], 0)
        
        self.__correct(used)
        return (self.corrections, self.closestDistance)
    
    
    '''
    Finds the closests correct spelled word
    
    @param  used:str  The word to correct, it must satisfy all restrictions
    '''
    def __correct(self, used):
        self.closestDistance = 0x7FFFFFFF
        previous = self.dictionary[-1]
        prevLen = 0
        usedLen = len(used)
        
        proper = None
        prevCommon = 0
        
        d = len(self.dictionary) - 1
        while d > self.dictionaryEnd:
            d -= 1
            proper = self.dictionary[d]
            if abs(len(proper) - usedLen) <= self.closestDistance:
                if previous == self.dictionary[d + 1]:
                    prevCommon = self.reusable[d];
                else:
                    prevCommon = min(prevLen, len(proper))
                    for i in range(0, prevCommon):
                        if previous[i] != proper[i]:
                            prevCommon = i
                            break
                
                skip = min(prevLen, len(proper))
                i = prevCommon
                while i < skip:
                    for u in range(0, usedLen):
                        if (used[u] == previous[i]) or (used[u] == proper[i]):
                            skip = i
                            break
                    i += 1
                
                common = min(skip, min(usedLen, len(proper)))
                for i in range(0, common):
                    if used[i] != proper[i]:
                        common = i
                        break
                
                distance = self.__distance(proper, skip, len(proper), used, common, usedLen)
                
                if self.closestDistance > distance:
                    self.closestDistance = distance
                    self.corrections = [proper]
                elif self.closestDistance == distance:
                    self.corrections.append(proper)
                
                previous = proper;
                if distance >= 0x7FFFFF00:
                    prevLen = distance & 255
                else:
                    prevLen = len(proper)
    
    
    '''
    Calculate the distance between a correct word and a incorrect word
    
    @param   proper:str  The correct word
    @param   y0:int      The offset for `proper`
    @param   yn:int      The length, before applying `y0`, of `proper`
    @param   used:str    The incorrect word
    @param   x0:int      The offset for `used`
    @param   xn:int      The length, before applying `x0`, of `used`
    @return  :float      The distance between the words
    '''
    def __distance(self, proper, y0, yn, used, x0, xn):
        my = self.M[y0]
        for y in range(y0, yn):
            best = 0x7FFFFFFF
            p = proper[y]
            myy = self.M[y + 1] # only one array bound check, and at most one + ☺
            x = x0
            while x < xn:
                change = my[x]
                u = used[x]
                if p == u:
                    # commence black magick … twilight would be so disappointed
                    x += 1
                    myy[x] = change
                    best = min(best, change)
                remove = myy[x]
                add = my[x + 1]
                
                cw = 1
                if my[x] in self.weights:
                    if p in self.weights[u]:
                      cw = self.weights[u][p]
                x += 1
                
                myy[x] = min(cw + change, 1 + min(remove, add))
                if best > myy[x]:
                    best = myy[x]
            
            if best > self.closestDistance:
                return 0x7FFFFF00 | y
            my = myy
        return my[xn]



'''
Start the program from ponysay.__init__ if this is the executed file
'''
if __name__ == '__main__':
    isthink =  (len(__file__) >= len('think'))    and (__file__.endswith('think'))
    isthink = ((len(__file__) >= len('think.py')) and (__file__.endswith('think.py'))) or isthink
    
    usage_saythink = '\033[34;1m(ponysay | ponythink)\033[21;39m'
    usage_common   = '[-c] [-W\033[33mCOLUMN\033[39m] [-b\033[33mSTYLE\033[39m]'
    usage_listhelp = '(-l | -L | -B | +l | +L | -A | + A | -v | -h)'
    usage_file     = '[-f\033[33mPONY\033[39m]* [[--] \033[33mmessage\033[39m]'
    usage_xfile    = '(+f\033[33mPONY\033[39m)* [[--] \033[33mmessage\033[39m]'
    usage_quote    = '(-q\033[33mPONY\033[39m)*'
    
    usage = '%s %s\n%s %s %s\n%s %s %s\n%s %s %s' % (usage_saythink, usage_listhelp,
                                                     usage_saythink, usage_common, usage_file,
                                                     usage_saythink, usage_common, usage_xfile,
                                                     usage_saythink, usage_common, usage_quote)
    
    usage = usage.replace('\033[', '\0')
    for sym in ('[', ']', '(', ')', '|', '...', '*'):
        usage = usage.replace(sym, '\033[2m' + sym + '\033[22m')
    usage = usage.replace('\0', '\033[')
    
    '''
    Argument parsing
    '''
    opts = ArgParser(program     = 'ponythink' if isthink else 'ponysay',
                     description = 'cowsay reimplemention for ponies',
                     usage       = usage,
                     longdescription =
'''Ponysay displays an image of a pony saying some text provided by the user.
If \033[4mmessage\033[24m is not provided, it accepts standard input. For an extensive
documentation run `info ponysay`, or for just a little more help than this
run `man ponysay`. Ponysay has so much more to offer than described here.''')
    
    opts.add_argumentless(['--quoters'])
    opts.add_argumentless(['--onelist'])
    opts.add_argumentless(['++onelist'])
    
    opts.add_argumentless(['-X', '--256-colours', '--256colours', '--x-colours'])
    opts.add_argumentless(['-V', '--tty-colours', '--ttycolours', '--vt-colours'])
    opts.add_argumentless(['-K', '--kms-colours', '--kmscolours'])
    
    opts.add_argumentless(['-i', '--info'])
    opts.add_argumentless(['+i', '++info'])
    opts.add_argumented(  ['-r', '--restrict'], arg = 'RESTRICTION')
    
    opts.add_argumented(  ['+c', '--colour'],                      arg = 'COLOUR')
    opts.add_argumented(  ['--colour-bubble', '--colour-balloon'], arg = 'COLOUR')
    opts.add_argumented(  ['--colour-link'],                       arg = 'COLOUR')
    opts.add_argumented(  ['--colour-msg', '--colour-message'],    arg = 'COLOUR')
    opts.add_argumented(  ['--colour-pony'],                       arg = 'COLOUR')
    opts.add_argumented(  ['--colour-wrap', '--colour-hyphen'],    arg = 'COLOUR')
    
    opts.add_argumentless(['-h', '--help'],                                  help = 'Print this help message.')
    opts.add_argumentless(['-v', '--version'],                               help = 'Print the version of the program.')
    opts.add_argumentless(['-l', '--list'],                                  help = 'List pony names.')
    opts.add_argumentless(['-L', '--symlist', '--altlist'],                  help = 'List pony names with alternatives.')
    opts.add_argumentless(['+l', '++list'],                                  help = 'List non-MLP:FiM pony names.')
    opts.add_argumentless(['+L', '++symlist', '++altlist'],                  help = 'List non-MLP:FiM pony names with alternatives.')
    opts.add_argumentless(['-A', '--all'],                                   help = 'List all pony names.')
    opts.add_argumentless(['+A', '++all', '--symall', '--altall'],           help = 'List all pony names with alternatives.')
    opts.add_argumentless(['-B', '--bubblelist', '--balloonlist'],           help = 'List balloon styles.')
    opts.add_argumentless(['-c', '--compress', '--compact'],                 help = 'Compress messages.')
    opts.add_argumentless(['-o', '--pony-only', '--ponyonly'],               help = 'Print only the pony.')
    opts.add_argumented(  ['-W', '--wrap'],                  arg = 'COLUMN', help = 'Specify column where the message should be wrapped.')
    opts.add_argumented(  ['-b', '--bubble', '--balloon'],   arg = 'STYLE',  help = 'Select a balloon style.')
    opts.add_argumented(  ['-f', '--file', '--pony'],        arg = 'PONY',   help = 'Select a pony.\nEither a file name or a pony name.')
    opts.add_argumented(  ['+f', '++file', '++pony'],        arg = 'PONY',   help = 'Select a non-MLP:FiM pony.')
    opts.add_argumented(  ['-q', '--quote'],                 arg = 'PONY',   help = 'Select a pony which will quote herself.')
    opts.add_variadic(    ['--f', '--files', '--ponies'],    arg = 'PONY')
    opts.add_variadic(    ['++f', '++files', '++ponies'],    arg = 'PONY')
    opts.add_variadic(    ['--q', '--quotes'],               arg = 'PONY')
    
    '''
    Whether at least one unrecognised option was used
    '''
    unrecognised = not opts.parse()
    
    
    ## Start
    ponysay = Ponysay()
    ponysay.unrecognised = unrecognised
    ponysay.run(opts)
