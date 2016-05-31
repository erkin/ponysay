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
'''
from common import *
from backend import *
from balloon import *
from spellocorrecter import *
from ucs import *
from kms import *
import lists
from metadata import *



class Ponysay():
    '''
    This is the mane class of ponysay
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        
        # The user's home directory
        self.HOME = os.environ['HOME'] if 'HOME' in os.environ else ''
        if len(self.HOME) == 0:
            os.environ['HOME'] = self.HOME = os.path.expanduser('~')
        
        
        ## Load extension and configurations via ponysayrc
        for file in ('$XDG_CONFIG_HOME/ponysay/ponysayrc', '$HOME/.config/ponysay/ponysayrc', '$HOME/.ponysayrc', '/etc/ponysayrc'):
            file = self.__parseFile(file)
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
        
        
        # Whether any unrecognised options was parsed, this should be set by the invoker before run()
        self.unrecognised = False
        
        
        # Whether the program is execute in Linux VT (TTY)
        self.linuxvt = ('TERM' in os.environ) and (os.environ['TERM'] == 'linux')
        
        # Whether the script is executed as ponythink
        self.isthink = self.__isPonythink()
        
        
        # Whether stdin is piped
        self.pipelinein = not sys.stdin.isatty()
        
        # Whether stdout is piped
        self.pipelineout = not sys.stdout.isatty()
        
        # Whether stderr is piped
        self.pipelineerr = not sys.stderr.isatty()
        
        
        # Whether KMS is used
        self.usekms = KMS.usingKMS(self.linuxvt)
        
        
        # Mode string that modifies or adds $ variables in the pony image
        self.mode = ''
        
        
        # The directories where pony files are stored, ttyponies/ are used if the terminal is Linux VT (also known as TTY) and not with KMS
        self.xponydirs = self.__getShareDirectories('ponies/')
        self.vtponydirs = self.__getShareDirectories('ttyponies/')
        
        # The directories where pony files are stored, extrattyponies/ are used if the terminal is Linux VT (also known as TTY) and not with KMS
        self.extraxponydirs = self.__getShareDirectories('extraponies/')
        self.extravtponydirs = self.__getShareDirectories('extrattyponies/')
        
        # The directories where quotes files are stored
        self.quotedirs = self.__getShareDirectories('quotes/')
        
        # The directories where balloon style files are stored
        self.balloondirs = self.__getShareDirectories('balloons/')
        
        # ucsmap files
        self.ucsmaps = self.__getShareDirectories('ucsmap/')
    
    
    @classmethod
    def __parseFile(cls, file):
        '''
        Parse a file name encoded with environment variables
        
        @param   file  The encoded file name
        @return        The target file name, None if the environment variables are not declared
        '''
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

    
    @classmethod
    def __getShareDirectories(cls, directory):
        '''
        Gets existing unique /share directories
        
        @param   directory:str  The directory base name
        @return  :list<str>     Absolute directory names
        '''
        appendset = set()
        rc = []
        _ponydirs = cls.__share(directory)
        for ponydir in _ponydirs:
            if (ponydir is not None) and os.path.isdir(ponydir) and (ponydir not in appendset):
                rc.append(ponydir)
                appendset.add(ponydir)
        return rc
    
    
    @classmethod
    def __share(cls, file):
        '''
        Gets /share files
        
        @param   file:str    The file base name
        @return  :list<str>  Absolute file names
        '''
        def cat(a, b):
            if a is None:
                return None
            return a + b
        # TODO use only ./ in development mode
        return [cat(cls.__parseFile(item), file) for item in [
                '$XDG_DATA_HOME/ponysay/',
                '$HOME/.local/share/ponysay/',
                '/usr/share/ponysay/'
               ]]
    
    
    @classmethod
    def __isPonythink(cls):
        '''
        Check if ponythink is executed
        '''
        isthink = sys.argv[0]
        if os.sep in isthink:
            isthink = isthink[isthink.rfind(os.sep) + 1:]
        if os.extsep in isthink:
            isthink = isthink[:isthink.find(os.extsep)]
        isthink = isthink.endswith('think')
        return isthink
    
    
    
    def run(self, args):
        '''
        Starts the part of the program the arguments indicate
        
        @param  args:ArgParser  Parsed command line arguments
        '''
        if (args.argcount == 0) and not self.pipelinein:
            args.help()
            exit(254)
            return
        self.args = args;
        
        ## Emulate termial capabilities
        if   self.__test_nfdnf('-X'):  (self.linuxvt, self.usekms) = (False, False)
        elif self.__test_nfdnf('-V'):  (self.linuxvt, self.usekms) = (True, False)
        elif self.__test_nfdnf('-K'):  (self.linuxvt, self.usekms) = (True, True)
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
        self.usingstandard = self.__test_nfdnf('-f', '-F', '-q') # -Q
        self.usingextra    = self.__test_nfdnf('+f', '-F') # +q -Q
        
        ## Run modes
        if   self.__test_nfdnf('-h'):                                     args.help()
        elif self.__test_nfdnf('+h'):                                     args.help(True)
        elif self.__test_nfdnf('-v'):                                     self.version()
        elif self.__test_nfdnf('--quoters'):                              self.quoters(True, False)
        elif self.__test_nfdnf('--Onelist', ('--onelist', '++onelist')):  self.onelist(True, True)
        elif self.__test_nfdnf('--onelist'):                              self.onelist(True, False)
        elif self.__test_nfdnf('++onelist'):                              self.onelist(False, True)
        elif self.__test_nfdnf('+A', ('-L', '+L')):                       self.linklist(); self.__extraponies(); self.linklist()
        elif self.__test_nfdnf('-A', ('-l', '+l')):                       self.list(); self.__extraponies(); self.list()
        elif self.__test_nfdnf('-L'):                                     self.linklist()
        elif self.__test_nfdnf('-l'):                                     self.list()
        elif self.__test_nfdnf('+L'):                                     self.__extraponies(); self.linklist()
        elif self.__test_nfdnf('+l'):                                     self.__extraponies(); self.list()
        elif self.__test_nfdnf('-B'):                                     self.balloonlist()
        else:
            self.__run()
    
    
    def __test_nfdnf(self, *keys):
        '''
        Test arguments written in negation-free disjunctive normal form
        
        @param   keys:*(str|itr<str>)  A list of keys and set of keys, any of which must exists, a set of keys only passes if all of those exists
        @return  :bool                 Whether the check passed
        '''
        for key in keys:
            if isinstance(key, str):
                if self.args.opts[key] is not None:
                    return True
            else:
                for skey in key:
                    if self.args.opts[skey] is None:
                        return False
                return True
        return False
    
    
    def __run(self):
        '''
        Run the important part of the program, the pony
        '''
        ## Colouring features
        if self.__test_nfdnf('--colour-pony'):
            self.mode += '\033[' + ';'.join(self.args.opts['--colour-pony']) + 'm'
        else:
            self.mode += '\033[0m'
        if self.__test_nfdnf('+c'):
            for part in ('msg', 'link', 'bubble'):
                if self.args.opts['--colour-' + part] is None:
                    self.args.opts['--colour-' + part] = self.args.opts['+c']
        
        ## Other extra features
        self.__bestpony(self.args)
        self.__ucsremap(self.args)
        if self.__test_nfdnf('-o'):
            self.mode += '$/= $$\\= $'
            self.args.message = ''
            self.ponyonly = True
        else:
            self.ponyonly = False
        if self.__test_nfdnf('-i', '+i'):
            self.args.message = ''
        self.restriction = self.args.opts['-r']
        
        ## The stuff
        if not self.unrecognised:
            self.printPony(self.args)
        else:
            self.args.help()
            exit(255)
    
    
    
    ##############################################
    ## Methods that run before the mane methods ##
    ##############################################
    
    def __extraponies(self):
        '''
        Use extra ponies
        '''
        ## Change ponydir to extraponydir
        self.ponydirs[:] = self.extraponydirs
        self.quotedirs[:] = [] ## TODO +q
    
    
    def __bestpony(self, args):
        '''
        Use best.pony if nothing else is set
        
        @param  args:ArgParser     Parsed command line arguments
        '''
        ## Set best.pony as the pony to display if none is selected
        def test(keys, strict):
            if strict:
                for key in keys:
                    if (args.opts[key] is not None) and (len(args.opts[key]) != 0):
                        return False
            else:
                for key in keys:
                    if args.opts[key] is not None:
                        return False
            return True
        keys = ['-f', '+f', '-F', '-q'] ## TODO +q -Q
        if test(keys, False):
            for ponydir in self.ponydirs:
                if os.path.isfile(ponydir + 'best.pony') or os.path.islink(ponydir + 'best.pony'):
                    pony = os.path.realpath(ponydir + 'best.pony') # Canonical path
                    if test(keys, True):
                        args.opts['-f'] = [pony]
                    else:
                        for key in keys:
                            if test(key, True):
                                args.opts[key] = [pony]
                    break
    
    
    def __ucsremap(self, args):
        '''
        Apply pony name remapping to args according to UCS settings
        
        @param  args:ArgParser  Parsed command line arguments
        '''
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
        
        ## Apply UCS → ASCII mapping to -f, +f, -F and -q arguments
        for flag in ('-f', '+f', '-F', '-q'): ## TODO +q -Q
            if args.opts[flag] is not None:
                for i in range(0, len(args.opts[flag])):
                    if args.opts[flag][i] in map:
                        args.opts[flag][i] = map[args.opts[flag][i]]
    
    
    #######################
    ## Auxiliary methods ##
    #######################
    
    def __ucsise(self, ponies, links = None):
        '''
        Apply UCS:ise pony names according to UCS settings
        
        @param  ponies:list<str>      List of all ponies (of interrest)
        @param  links:map<str, str>?  Map to fill with simulated symlink ponies, may be `None`
        '''
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
        
        ## Apply UCS → ASCII mapping to ponies, by alias if weak settings
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
    
    
    def __getPony(self, selection, args, alt = False):
        '''
        Returns one file with full path and ponyquote that should be used, names is filter for names, also accepts filepaths
        
        @param   selection:(name:str, dirfiles:itr<str>, quote:bool)?  Parsed command line arguments as name–directories–quoting tubles:
                                                                           name:      The pony name
                                                                           dirfiles:  Files, with the directory, in the pony directories
                                                                           quote:     Whether to use ponyquotes
        @param   args:ArgParser                                        Parsed command line arguments
        @param   alt:bool                                              For method internal use...
        @return  (path, quote):(str, str?)                             The file name of a pony, and the ponyquote that should be used if any
        '''
        ## If there is no selected ponies, choose all of them
        if (selection is None) or (len(selection) == 0):
            selection = [self.__selectAnypony(args)]
        
        ## Select a random pony of the choosen ones
        pony = selection[random.randrange(0, len(selection))]
        if os.path.exists(pony[0]):
            ponyname = pony[0].split(os.sep)[-1]
            if os.extsep in ponyname:
                ponyname = ponyname[:ponyname.rfind(os.extsep)]
            return (pony[0], self.__getQuote(ponyname, pony[0]) if pony[2] else None)
        else:
            possibilities = [f.split(os.sep)[-1][:-5] for f in pony[1]]
            if pony[0] not in possibilities:
                if not alt:
                    autocorrect = SpelloCorrecter(possibilities)
                    (alternatives, dist) = autocorrect.correct(pony[0])
                    limit = os.environ['PONYSAY_TYPO_LIMIT'] if 'PONYSAY_TYPO_LIMIT' in os.environ else ''
                    limit = 5 if len(limit) == 0 else int(limit)
                    if (len(alternatives) > 0) and (dist <= limit):
                        (_, files, quote) = pony
                        return self.__getPony([(a, files, quote) for a in alternatives], True)
                printerr('I have never heard of anypony named %s' % pony[0]);
                if not self.usingstandard:
                    printerr('Use -f/-q or -F if it a MLP:FiM pony');
                if not self.usingextra:
                    printerr('Have you tested +f or -F?');
                exit(252)
            else:
                file = pony[1][possibilities.index(pony[0])]
                return (file, self.__getQuote(pony[0], file) if pony[2] else None)
    
    
    def __selectAnypony(self, args):
        '''
        Randomly select a pony from all installed ponies
        
        @param   args:ArgParser                                 Parsed command line arguments
        @return  (name, dirfile, quote):(str, list<str>, bool)  The pony name, pony file with the directory, and whether to use ponyquotes
        '''
        quote    =  args.opts['-q'] is not None ## TODO +q -Q
        standard = (args.opts['-f'] is not None) or (args.opts['-F'] is not None) or (args.opts['-q'] is not None) ## TODO -Q
        extra    = (args.opts['+f'] is not None) or (args.opts['-F'] is not None) ## TODO +q -Q
        if not (standard or extra):
            standard = True
        ponydirs = (self.ponydirs if standard else []) + (self.extraponydirs if extra else []);
        quoters  = self.__quoters() if standard and quote else None ## TODO +q -Q
        if (quoters is not None) and (len(quoters) == 0):
            printerr('Princess Celestia! All the ponies are mute!')
            exit(250)
        
        ## Get all ponies, with quotes
        oldponies = {}
        self.__getAllPonies(standard, extra, oldponies, quoters)
        
        ## Apply restriction
        ponies = self.__applyRestriction(oldponies, ponydirs)
        
        ## Select one pony and set all information
        names = list(ponies.keys())
        if len(names) == 0:
            printerr('All the ponies are missing, call the Princess!')
            exit(249)
        pony = names[random.randrange(0, len(names))]
        return (pony, [ponies[pony]], quote)
    
    
    def __getAllPonies(self, standard, extra, collection, quoters):
        '''
        Get ponies for a set of directories
        
        @param  standard:bool              Whether to include standard ponies
        @parma  extra:bool                 Whether to include extra ponies
        @param  collection:dict<str, str>  Collection of already found ponies, and collection for new ponies, maps to the pony file
        @param  quoters:set<str>?          Ponies to limit to, or `None` to include all ponies
        '''
        if standard:
            self.__getPonies(self.ponydirs, collection, quoters)
        if extra:
            self.__getPonies(self.extraponydirs, collection, quoters)
    
    
    def __getPonies(self, directories, collection, quoters):
        '''
        Get ponies for a set of directories
        
        @param  directories:list<str>      Directories with ponies
        @param  collection:dict<str, str>  Collection of already found ponies, and collection for new ponies, maps to the pony file
        @param  quoters:set<str>?          Ponies to limit to, or `None` to include all ponies
        '''
        for ponydir in directories:
            for ponyfile in os.listdir(ponydir):
                if endswith(ponyfile, '.pony'):
                    pony = ponyfile[:-5]
                    if (pony not in collection) and ((quoters is None) or (pony in quoters)):
                        collection[pony] = ponydir + ponyfile
    
    
    def __applyRestriction(self, oldponies, ponydirs):
        '''
        Restrict ponies
        
        @param   oldponies:dict<str, str>  Collection of original ponies, maps to pony file
        @param   ponydirs:list<sr>         List of pony directories
        @return  :dict<str, str>           Map from restricted ponies to pony files
        '''
        ## Apply metadata restriction
        if self.restriction is not None:
            ponies = {}
            self.__applyMetadataRestriction(ponies, oldponies, ponydirs)
            if len(ponies) > 0:
                oldponies = ponies
            
        ## Apply dimension restriction
        ponies = {}
        self.__applyDimensionRestriction(ponies, oldponies, ponydirs)
        if len(ponies) > 0:
            oldponies = ponies
        
        return oldponies
    
    
    def __applyMetadataRestriction(self, ponies, oldponies, ponydirs):
        '''
        Restrict to ponies by metadata
        
        @param  ponies:dict<str, str>     Collection to fill with restricted ponies, mapped to pony file
        @param  oldponies:dict<str, str>  Collection of original ponies, maps to pony file
        @param  ponydirs:list<sr>         List of pony directories
        '''
        logic = Metadata.makeRestrictionLogic(self.restriction)
        for ponydir in ponydirs:
            for pony in Metadata.restrictedPonies(ponydir, logic):
                if (pony in oldponies) and not (pony in ponies):
                    ponies[pony] = ponydir + pony + '.pony'
    
    
    def __applyDimensionRestriction(self, ponies, oldponies, ponydirs):
        '''
        Restrict to ponies by dimension
        
        @param  ponies:dict<str, str>     Collection to fill with restricted ponies, mapped to pony file
        @param  oldponies:dict<str, str>  Collection of original ponies, maps to pony file
        @param  ponydirs:list<sr>         List of pony directories
        '''
        (termh, termw) = gettermsize()
        for ponydir in ponydirs:
            (fitw, fith) = (None, None)
            if os.path.exists(ponydir + 'widths'):
                fitw = set()
                with open(ponydir + 'widths', 'rb') as file:
                    Metadata.getFitting(fitw, termw, file)
            if os.path.exists(ponydir + ('onlyheights' if self.ponyonly else 'heights')):
                fith = set()
                with open(ponydir + ('onlyheights' if self.ponyonly else 'heights'), 'rb') as file:
                    Metadata.getFitting(fith, termh, file)
            for ponyfile in oldponies.values():
                if ponyfile.startswith(ponydir):
                    pony = ponyfile[len(ponydir) : -5]
                    if (fitw is None) or (pony in fitw):
                        if (fith is None) or (pony in fith):
                            ponies[pony] = ponyfile
    
    
    def __getQuote(self, pony, file):
        '''
        Select a quote for a pony
        
        @param   pony:str  The pony name
        @param   file:str  The pony's file name
        @return  :str      A quote from the pony, with a failure fall back message
        '''
        quote = []
        if (os.path.dirname(file) + os.sep).replace(os.sep + os.sep, os.sep) in self.ponydirs:
            realpony = pony
            if os.path.islink(file):
                realpony = os.path.basename(os.path.realpath(file))
                if os.extsep in realpony:
                    realpony = realpony[:realpony.rfind(os.extsep)]
            quote = self.__quotes(ponies = [realpony])
        if len(quote) == 0:
            quote = 'Zecora! Help me, I am mute!'
        else:
            quote = quote[random.randrange(0, len(quote))][1]
            printinfo('quote file: ' + quote)
            with open(quote, 'rb') as qfile:
                quote = qfile.read().decode('utf8', 'replace').strip()
        return quote
    
    
    def __quoters(self, ponydirs = None, quotedirs = None):
        '''
        Returns a set with all ponies that have quotes and are displayable
        
        @param   ponydirs:itr<str>?   The pony directories to use
        @param   quotedirs:itr<str>?  The quote directories to use
        @return  :set<str>            All ponies that have quotes and are displayable
        '''
        if ponydirs  is None:  ponydirs  = self.ponydirs
        if quotedirs is None:  quotedirs = self.quotedirs
        
        ## List all unique quote files
        quotes = []
        quoteshash = set()
        _quotes = []
        for quotedir in quotedirs:
            _quotes += [item[:item.index('.')] for item in os.listdir(quotedir)]
        for quote in _quotes:
            if not quote == '':
                if not quote in quoteshash:
                    quoteshash.add(quote)
                    quotes.append(quote)
        
        ## Create a set of all ponies that have quotes
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
    
    
    def __quotes(self, ponydirs = None, quotedirs = None, ponies = None):
        '''
        Returns a list with all (pony, quote file) pairs
        
        @param   ponydirs:itr<str>?        The pony directories to use
        @param   quotedirs:itr<str>?       The quote directories to use
        @param   ponies:itr<str>?          The ponies to use
        @return  (pony, quote):(str, str)  All ponies–quote file-pairs
        '''
        if ponydirs  is None:  ponydirs  = self.ponydirs
        if quotedirs is None:  quotedirs = self.quotedirs
        
        ## Get all ponyquote files
        quotes = []
        for quotedir in quotedirs:
            quotes += [quotedir + item for item in os.listdir(quotedir)]
        
        ## Create list of all pony–quote file-pairs
        rc = []
        if ponies is None:
            for ponydir in ponydirs:
                for pony in os.listdir(ponydir):
                    if endswith(pony, '.pony'):
                        p = pony[:-5] # remove .pony
                        for quote in quotes:
                            q = quote[quote.rindex('/') + 1:]
                            q = q[:q.rindex('.')]
                            if ('+' + p + '+') in ('+' + q + '+'):
                                rc.append((p, quote))
        else:
            for p in ponies:
                for quote in quotes:
                    q = quote[quote.rindex('/') + 1:]
                    q = q[:q.rindex('.')]
                    if ('+' + p + '+') in ('+' + q + '+'):
                        rc.append((p, quote))
        
        return rc
    
    
    
    #####################
    ## Listing methods ##
    #####################
    
    def list(self, ponydirs = None):
        '''
        Lists the available ponies
        
        @param  ponydirs:itr<str>?  The pony directories to use
        '''
        lists.simplelist(self.ponydirs if ponydirs is None else ponydirs,
                        self.__quoters(), lambda x : self.__ucsise(x))
    
    
    def linklist(self, ponydirs = None):
        '''
        Lists the available ponies with alternatives inside brackets
        
        @param  ponydirs:itr<str>  The pony directories to use
        '''
        lists.linklist(self.ponydirs if ponydirs is None else ponydirs,
                      self.__quoters(), lambda x, y : self.__ucsise(x, y))
    
    
    def onelist(self, standard = True, extra = False):
        '''
        Lists the available ponies on one column without anything bold or otherwise formated
        
        @param  standard:bool  Include standard ponies
        @param  extra:bool     Include extra ponies
        '''
        
        pony_dirs = (self.ponydirs if standard else []) + (self.extraponydirs if extra else [])
        
        lists.onelist(pony_dirs, self.__ucsise)
    
    
    def quoters(self, standard = True, extra = False):
        '''
        Lists with all ponies that have quotes and are displayable, on one column without anything bold or otherwise formated
        
        @param  standard:bool  Include standard ponies
        @param  extra:bool     Include extra ponies
        '''
        ## Get all quoters
        ponies = list(self.__quoters()) if standard else []
        
        ## And now the extra ponies
        if extra:
            self.__extraponies()
            ponies += list(self.__quoters())
        
        ## UCS:ise here
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
    
    def balloonlist(self):
        '''
        Prints a list of all balloons
        '''
        lists.balloonlist(self.balloondirs, self.isthink)
    
    
    def __getBalloonPath(self, names, alt = False):
        '''
        Returns one file with full path, names is filter for style names, also accepts filepaths
        
        @param  names:list<str>  Balloons to choose from, may be `None`
        @param  alt:bool         For method internal use
        @param  :str             The file name of the balloon, will be `None` iff `names` is `None`
        '''
        ## Stop if there is no choosen balloon
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
                limit = 5 if len(limit) == 0 else int(limit)
                if (len(alternatives) > 0) and (dist <= limit):
                    return self.__getBalloonPath(alternatives, True)
            printerr('That balloon style %s does not exist' % balloon)
            exit(251)
        else:
            return balloons[balloon]
    
    
    def __getBalloon(self, balloonfile):
        '''
        Creates the balloon style object
        
        @param   balloonfile:str  The file with the balloon style, may be `None`
        @return  :Balloon         Instance describing the balloon's style
        '''
        return Balloon.fromFile(balloonfile, self.isthink)
    
    
    
    ########################
    ## Displaying methods ##
    ########################
    
    def version(self):
        '''
        Prints the name of the program and the version of the program
        '''
        ## Prints the "ponysay $VERSION", if this is modified, ./dev/dist.sh must be modified accordingly
        print('%s %s' % ('ponysay', VERSION))
    
    
    def printPony(self, args):
        '''
        Print the pony with a speech or though bubble. message, pony and wrap from args are used.
        
        @param  args:ArgParser  Parsed command line arguments
        '''
        ## Get the pony
        selection = []
        self.__getSelectedPonies(args, selection)
        (pony, quote) = self.__getPony(selection, args)
        
        ## Get message and manipulate it
        msg = self.__getMessage(args, quote)
        msg = self.__colouriseMessage(args, msg)
        msg = self.__compressMessage(args, msg)
        
        ## Print info
        printinfo('pony file: ' + pony)
        
        ## Use PNG file as pony file
        pony = self.__useImage(pony)
        
        ## If KMS is utilies, select a KMS pony file and create it if necessary
        pony = KMS.kms(pony, self.HOME, self.linuxvt)
        
        ## If in Linux VT clean the terminal (See info/pdf-manual [Printing in TTY with KMS])
        if self.linuxvt:
            print('\033[H\033[2J', end='')
        
        ## Get width truncation and wrapping
        widthtruncation = self.__getWidthTruncation()
        messagewrap = self.__getMessageWrap(args)
        
        ## Get balloon object
        balloonfile = self.__getBalloonPath(args.opts['-b'] if args.opts['-b'] is not None else None)
        printinfo('balloon style file: ' + str(balloonfile))
        balloon = self.__getBalloon(balloonfile) if args.opts['-o'] is None else None
        
        ## Get hyphen style
        hyphen = self.__getHyphen(args)
        
        ## Link and balloon colouring
        linkcolour = self.__getLinkColour(args)
        ballooncolour = self.__getBalloonColour(args)
        
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
        
        ## Print the output, truncated on the height
        self.__printOutput(output)
    
    
    def __getSelectedPonies(self, args, selection):
        '''
        Get all selected ponies
        
        @param  args:ArgParser                                     Command line options
        @param  selection:list<(name:str, file:str, quotes:bool)>  List to fill with tuples of selected pony names, pony files and whether quotes are used
        '''
        (standard, extra) = ([], [])
        for ponydir in self.ponydirs:
            for pony in os.listdir(ponydir):
                if endswith(pony, '.pony'):
                    standard.append(ponydir + pony)
        for ponydir in self.extraponydirs:
            for pony in os.listdir(ponydir):
                if endswith(pony, '.pony'):
                    extra.append(ponydir + pony)
        both = standard + extra
        for (opt, ponies, quotes) in [('-f', standard, False), ('+f', extra, False), ('-F', both, False), ('-q', standard, True)]: ## TODO +q -Q
            if args.opts[opt] is not None:
                for pony in args.opts[opt]:
                    selection.append((pony, ponies, quotes))
    
    
    def __getMessage(self, args, quote):
        '''
        Get message and remove tailing whitespace from stdin (but not for each line)
        
        @param   args:ArgParser  Command line options
        @param   quote:str?      The quote, or `None` if none
        @return  :str            The message
        '''
        if quote is not None:
            return quote
        if args.message is None:
            return ''.join(sys.stdin.readlines()).rstrip()
        return args.message
    
    
    def __colouriseMessage(self, args, msg):
        '''
        Colourise message if option is set
        
        @param   args:ArgParser  Command line options
        @param   msg:str         The message
        @return  :str            The message colourised
        '''
        if args.opts['--colour-msg'] is not None:
            msg = '\033[' + ';'.join(args.opts['--colour-msg']) + 'm' + msg
        return msg
    
    
    def __compressMessage(self, args, msg):
        '''
        This algorithm should give some result as cowsay's, if option is set
        
        @param   args:ArgParser  Command line options
        @param   msg:str         The message
        @return  :str            The message compressed
        '''
        if args.opts['-c'] is None:
            return msg
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
        return buf.replace('\n', '\n\n')
    
    
    def __useImage(self, pony):
        '''
        Convert image to the ponysay format if it is a regular image
        
        @param   pony:str  The pony file
        @return  :str      The new pony file, or the old if it was already in the ponysay format
        '''
        if endswith(pony.lower(), '.png'):
            pony = '\'' + pony.replace('\'', '\'\\\'\'') + '\''
            pngcmd = 'ponytool --import image --file %s --balloon n --export ponysay --platform %s --balloon y'
            pngcmd %= (pony, ('linux' if self.linuxvt else 'xterm')) # XXX xterm should be haiku in Haiku
            pngpipe = os.pipe()
            Popen(pngcmd, stdout=os.fdopen(pngpipe[1], 'w'), shell=True).wait()
            pony = '/proc/' + str(os.getpid()) + '/fd/' + str(pngpipe[0])
        return pony
    
    
    def __getWidthTruncation(self):
        '''
        Gets the width trunction setting
        
        @return  :int?  The column the truncate the output at, or `None` to not truncate it
        '''
        env_width = os.environ['PONYSAY_FULL_WIDTH'] if 'PONYSAY_FULL_WIDTH' in os.environ else None
        if env_width is None:  env_width = 'auto'
        return gettermsize()[1] if env_width not in ('yes', 'y', '1') else None
    
    
    def __getMessageWrap(self, args):
        '''
        Gets the message balloon wrapping column
        
        @param   args:ArgParser  Command line options
        @return  :int?           The message balloon wrapping column, or `None` if disabled
        '''
        messagewrap = 65
        if (args.opts['-W'] is not None) and (len(args.opts['-W'][0]) > 0):
            messagewrap = args.opts['-W'][0]
            if messagewrap[0] in 'nmsNMS': # m is left to n on QWERTY and s is left to n on Dvorak
                messagewrap = None
            elif messagewrap[0] in 'iouIOU': # o is left to i on QWERTY and u is right to i on Dvorak
                messagewrap = gettermsize()[1]
            else:
                messagewrap = int(args.opts['-W'][0])
        return messagewrap
    
    
    def __getHyphen(self, args):
        '''
        Gets the hyphen to use a at hyphenation
        
        @param   args:ArgParser  Command line options
        @return  :str            The hyphen string to use at hyphenation
        '''
        hyphen = os.environ['PONYSAY_WRAP_HYPHEN'] if 'PONYSAY_WRAP_HYPHEN' in os.environ else None
        if (hyphen is None) or (len(hyphen) == 0):
            hyphen = '-'
        hyphencolour = ''
        if args.opts['--colour-wrap'] is not None:
            hyphencolour = '\033[' + ';'.join(args.opts['--colour-wrap']) + 'm'
        return '\033[31m' + hyphencolour + hyphen
    
    
    def __getLinkColour(self, args):
        '''
        Gets the colour of balloon links
        
        @param   args:ArgParser  Command line options
        @return  :str            The colour of balloon links
        '''
        linkcolour = ''
        if args.opts['--colour-link'] is not None:
            linkcolour = '\033[' + ';'.join(args.opts['--colour-link']) + 'm'
        return linkcolour
    
    
    def __getBalloonColour(self, args):
        '''
        Gets the colour of balloons
        
        @param   args:ArgParser  Command line options
        @return  :str            The colour of balloons
        '''
        ballooncolour = ''
        if args.opts['--colour-bubble'] is not None:
            ballooncolour = '\033[' + ';'.join(args.opts['--colour-bubble']) + 'm'
        return ballooncolour
    
    
    def __printOutput(self, output):
        '''
        Print the output, but truncate it on the height
        
        @param  output:str  The output truncated on the width but not on the height
        '''
        ## Load height trunction settings
        env_bottom = os.environ['PONYSAY_BOTTOM'] if 'PONYSAY_BOTTOM' in os.environ else None
        if env_bottom is None:  env_bottom = ''
        
        env_height = os.environ['PONYSAY_TRUNCATE_HEIGHT'] if 'PONYSAY_TRUNCATE_HEIGHT' in os.environ else None
        if env_height is None:  env_height = ''
        
        env_lines = os.environ['PONYSAY_SHELL_LINES'] if 'PONYSAY_SHELL_LINES' in os.environ else None
        if (env_lines is None) or (env_lines == ''):  env_lines = '2'
        
        ## Print the output, truncated on height if so set
        lines = gettermsize()[0] - int(env_lines)
        if self.linuxvt or (env_height in ('yes', 'y', '1')):
            if env_bottom in ('yes', 'y', '1'):
                for line in output.split('\n')[: -lines]:
                    print(line)
            else:
                for line in output.split('\n')[: lines]:
                    print(line)
        else:
            print(output)

