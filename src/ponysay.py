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
'''
from common import *
from backend import *
from balloon import *
from spellocorrecter import *
from ucs import *



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
                    './',
                    '$XDG_DATA_HOME/ponysay/',
                    '$HOME/.local/share/ponysay/',
                    '/usr/share/ponysay/'
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
        
        ## Save whether standard or extra ponies are used
        self.usingstandard = (args.opts['-f'] is not None) or (args.opts['-F'] is not None) or (args.opts['-q'] is not None) #or (args.opts['-Q'] is not None)
        self.usingextra    = (args.opts['+f'] is not None) or (args.opts['-F'] is not None) #or (args.opts['+q'] is not None) or (args.opts['-Q'] is not None)
        
        ## Run modes
        if   args.opts['-h']        is not None:  args.help()
        elif args.opts['--quoters'] is not None:  self.quoters()
        elif args.opts['--onelist'] is not None:  self.onelist()
        elif args.opts['--Onelist'] is not None:  self.fullonelist()
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
            if not self.usingstandard:
                sys.stderr.write('Use -f/-q or -F if it a MLP:FiM pony');
            if not self.usingexta:
                sys.stderr.write('Have you tested +f or -F?');
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
    
    
    '''
    Lists the available ponies on one column without anything bold or otherwise formated, both standard ponies and extra ponies
    '''
    def fullonelist(self):
        ## Get all pony files
        _ponies = []
        for ponydir in self.ponydirs: # Loop ponydirs
            _ponies += os.listdir(ponydir)
        
        ## Remove .pony from all files and skip those that does not have .pony
        ponies = []
        for pony in _ponies:
            if endswith(pony, '.pony'):
                ponies.append(pony[:-5])
        
        ## UCS:ise
        self.__ucsise(ponies)
        
        ## Swap to extra ponies
        self.__extraponies()
        
        ## Get all pony files
        _ponies = []
        for ponydir in self.ponydirs: # Loop ponydirs
            _ponies += os.listdir(ponydir)
        
        ## Remove .pony from all files and skip those that does not have .pony
        xponies = []
        for pony in _ponies:
            if endswith(pony, '.pony'):
                xponies.append(pony[:-5])
        
        ## UCS:ise
        self.__ucsise(xponies)
        
        ## Print each one on a seperate line, but skip duplicates
        last = ''
        ponies += xponies
        ponies.sort()
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
            pngcmd = 'ponytool --import image --file %s --export ponysay --platform %s --balloon y'
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
            ponytoolcmd = 'ponytool --import ponysay --file %s --export ponysay --file %s --platform linux '
            ponytoolcmd += '--balloon n --colourful y --fullcolour y --left - --right - --top - --bottom - --palette %s'
            if not os.system(ponytoolcmd % (_pony, _kmspony, palette)) == 0:
                sys.stderr.write('Unable to run ponytool successfully, you need util-say>=3 for KMS support\n')
                exit(1)
            if shared:
                Popen('chmod 666 -- ' + _kmspony, shell=True).wait()
        
        return kmspony

