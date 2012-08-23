#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from subprocess import Popen, PIPE


class Setup():
    def __init__(self):
        usage_script = '\033[34;1msetup.py\033[21;39m'
        usage_help   = '(--version | --help)'
        usage_proc   = '\033[4mconfigurations\033[24m ([build] | prebuilt | install | (uninstall|clean)[-old])'
        
        usage = '%s %s\n%s %s' % (usage_script, usage_help, usage_script, usage_proc)
        
        usage = usage.replace('\033[', '\0')
        for sym in ('[', ']', '(', ')', '|', '...'):
            usage = usage.replace(sym, '\033[2m' + sym + '\033[22m')
            usage = usage.replace('\0', '\033[')
        
        opts = ArgParser(program     = 'setup.py',
                         description = 'installer for ponysay',
                         usage       = usage)
        
        opts.add_argumentless(alternatives = ['-h', '--help'])
        opts.add_argumentless(alternatives = ['-v', '--version'])
        
        opts.add_argumentless(help = 'Install everything that is not explicity excluded',                              alternatives = ['--everything', '--with-everything'])
        opts.add_argumentless(help = 'Install only the essentials\nNote that this can vary depedning on version',      alternatives = ['--minimal'])
        opts.add_argumentless(help = 'Install nothing that is not explicity included',                                 alternatives = ['--nothing', '--with-nothing'])
        opts.add_argumentless(help = 'Do not install ponysay command',                                                 alternatives = ['--without-ponysay'])
        opts.add_argumentless(help = 'Install ponysay command',                                                        alternatives = ['--with-ponysay'])
        opts.add_argumentless(help = 'Do not install ponythink command',                                               alternatives = ['--without-ponythink'])
        opts.add_argumentless(help = 'Install ponythink command',                                                      alternatives = ['--with-ponythink'])
        
        opts.add_argumentless(help = 'Do not install a user shared cache',                                             alternatives = ['--without-shared-cache'])
        opts.add_argumented  (help = 'Install a user shared cache at CACHEDIR\nDefault = /var/cache/ponysay',          alternatives = [   '--with-shared-cache'], arg='CACHEDIR')
        
        opts.add_argumentless(help = 'Do not install completion for GNU Bash',                                         alternatives = ['--without-bash'])
        opts.add_argumented  (help = 'Set file name for the completion for ponysay in GNU Bash',                       alternatives = [   '--with-bash'], arg='PONYSAY_BASH_FILE')
        opts.add_argumentless(help = 'Do not install completion for Friendly interactive shell',                       alternatives = ['--without-fish'])
        opts.add_argumented  (help = 'Set file name for the completion for ponysay in Friendly interactive shell',     alternatives = [   '--with-fish'], arg='PONYSAY_FISH_FILE')
        opts.add_argumentless(help = 'Do not install completion for zsh',                                              alternatives = ['--without-zsh'])
        opts.add_argumented  (help = 'Set file name for the completion for ponysay in zsh',                            alternatives = [   '--with-zsh'], arg='PONYSAY_ZSH_FILE')
        opts.add_argumentless(help = 'Only install explicitly included shell completions',                             alternatives = ['--without-shells'])
        opts.add_argumented  (help = 'Set share/ directory used for shell completions\nDefault = $SHAREDIR',           alternatives = [   '--with-shells'], arg='SHAREDIR')
        
        opts.add_argumentless(help = 'Do not install PDF manual\nDefault',                                             alternatives = ['--without-pdf'])
        opts.add_argumented  (help = 'Set directory for PDF manual\nDefault = $PREFIX/doc',                            alternatives = [   '--with-pdf'], arg='DOCDIR')
        opts.add_argumentless(help = 'Do not compress PDF manual\nDefault',                                            alternatives = ['--without-pdf-compression'])
        opts.add_argumented  (help = 'Select compression for PDF manual\nDefault = gz, xz is also recognised',         alternatives = [   '--with-pdf-compression'], arg='COMPRESSION')
        opts.add_argumentless(help = 'Do not install info manual',                                                     alternatives = ['--without-info'])
        opts.add_argumented  (help = 'Set directory for info manual\nDefault = $SHARE/info',                           alternatives = [   '--with-info'], arg='INFODIR')
        opts.add_argumentless(help = 'Do not use install-info when installing info manual',                            alternatives = ['--without-info-install'])
        opts.add_argumentless(help = 'Use install-info when installing info manual\nDefault',                          alternatives = [   '--with-info-install'])
        opts.add_argumentless(help = 'Do not compress info manual',                                                    alternatives = ['--without-info-compression'])
        opts.add_argumented  (help = 'Select compression for info manual\nDefault = gz, xz is also recognised',        alternatives = [   '--with-info-compression'], arg='COMPRESSION')
        
        opts.add_argumentless(help = 'Do not install English manpage manual',                                          alternatives = ['--without-man-en'])
        opts.add_argumented  (help = 'Set directory for English manpage\nDefault = $SHARE/man',                        alternatives = [   '--with-man-en'], arg='MANDIR')
        opts.add_argumentless(help = 'Do not install Spanish manpage manual\nDefault.',                                alternatives = ['--without-man-es'])
        opts.add_argumented  (help = 'Set directory for Spanish manpage\nDefault = $SHARE/man',                        alternatives = [   '--with-man-es'], arg='MANDIR')
        opts.add_argumentless(help = 'Do not install any manpages',                                                    alternatives = ['--without-man'])
        opts.add_argumented  (help = 'Set directory for all man pages\nDefault = $SHARE/man',                          alternatives = [   '--with-man'], arg='MANDIR')
        opts.add_argumentless(help = 'Do not compress English manpage',                                                alternatives = ['--without-man-en-compression'])
        opts.add_argumented  (help = 'Select compression for English manpage\nDefault = gz, xz is also recognised',    alternatives = [   '--with-man-en-compression'], arg='COMPRESSION')
        opts.add_argumentless(help = 'Do not compress Spanish manpage',                                                alternatives = ['--without-man-es-compression'])
        opts.add_argumented  (help = 'Select compression for Spanish manpage\nDefault = gz, xz is also recognised',    alternatives = [   '--with-man-es-compression'], arg='COMPRESSION')
        opts.add_argumentless(help = 'Do not compress any installed manpage',                                          alternatives = ['--without-man-compression'])
        opts.add_argumented  (help = 'Select compression for installed manpages\nDefault = gz, xz is also recognised', alternatives = [   '--with-man-compression'], arg='COMPRESSION')
        
        opts.add_argumented  (help = 'Change the section for the ponysay manpage\nDefault = 6',                        alternatives = ['--man-section-ponysay'], arg='SECTION')
        opts.add_argumented  (help = 'Change the section for the cowsay manpage\nDefault = 1',                         alternatives = ['--man-section-cowsay'],  arg='SECTION')
        opts.add_argumented  (help = 'Change the section for the fortune manpage\nDefault = 6',                        alternatives = ['--man-section-fortune'], arg='SECTION')
        
        opts.add_argumentless(help = 'Do not install xterm ponies',                                                    alternatives = ['--without-ponies'])
        opts.add_argumented  (help = 'Set directory for xterm ponies\nDefault = $SHAREDIR/ponysay/ponies',             alternatives = [   '--with-ponies'], arg='PONYDIR')
        opts.add_argumentless(help = 'Do not install tty ponies',                                                      alternatives = ['--without-ttyponies'])
        opts.add_argumented  (help = 'Set directory for tty ponies\nDefault = $SHAREDIR/ponysay/ttyponies',            alternatives = [   '--with-ttyponies'], arg='TTYPONYDIR')
        opts.add_argumentless(help = 'Do not install extra xterm ponies',                                              alternatives = ['--without-extraponies'])
        opts.add_argumented  (help = 'Set directory for extra xterm ponies\nDefault = $SHAREDIR/ponysay/extraponies',  alternatives = [   '--with-extraponies'], arg='XPONYDIR')
        opts.add_argumentless(help = 'Do not install extra tty ponies',                                                alternatives = ['--without-extrattyponies'])
        opts.add_argumented  (help = 'Set directory for extra tty ponies\nDefault = $SHAREDIR/ponysay/extrattyponies', alternatives = [   '--with-extrattyponies'], arg='XTTYPONYDIR')
        opts.add_argumentless(help = 'Do not install pony quotes',                                                     alternatives = ['--without-quotes'])
        opts.add_argumented  (help = 'Set directory for pony quotes\nDefault = $SHAREDIR/ponysay/quotes',              alternatives = [   '--with-quotes'], arg='QUOTEDIR')
        opts.add_argumentless(help = 'Do not install balloon styles',                                                  alternatives = ['--without-balloons'])
        opts.add_argumented  (help = 'Set directory for balloon styles\nDefault = $SHAREDIR/ponysay/balloons',         alternatives = [   '--with-balloons'], arg='BALLOONDIR')
        opts.add_argumentless(help = 'Do not install UCS pony name map',                                               alternatives = ['--without-ucs'])
        opts.add_argumented  (help = 'Set file for the UCS pony name map\nDefault = $SHAREDIR/ponysay/ucsmap',         alternatives = [   '--with-ucs'], arg='UCSFILE')
        
        opts.add_argumentless(help = 'Let the installer set the env name for python in ponysay\nDefault',                         alternatives = ['--without-custom-env-python'])
        opts.add_argumented  (help = 'Set the env name for python in ponysay',                                                    alternatives = ['--with-custom-env-python'], arg='PYTHON')
        opts.add_argumented  (help = 'Set a prefix to all implicit directories\nDefault = /usr',                                  alternatives = ['--prefix'], arg='PREFIX')
        opts.add_argumentless(help = 'Change all implicit configurations to fit local user a installation for the current user',  alternatives = ['--private'])
        opts.add_argumentless(help = 'Change all implicit directories to fit installation to /opt',                               alternatives = ['--opt'])
        opts.add_argumented  (help = 'Set the system\'s directory for command executables\nDefault = $PREFIX/bin',                alternatives = ['--bin-dir'], arg='BINDIR')
        opts.add_argumented  (help = 'Set the system\'s directory for non-command executables\nDefault = $PREFIX/lib\nNot used.', alternatives = ['--lib-dir'], arg='LIBDIR')
        opts.add_argumented  (help = 'Set the system\'s directory for resource files\nDefault = $PREFIX/share',                   alternatives = ['--share-dir'], arg='SHAREDIR')
        opts.add_argumented  (help = 'Set the system\'s directory for cache directories\nDefault = /var/cache',                   alternatives = ['--cache-dir'], arg='CACHEDIR')
        
        opts.parse()
        opts.help()
        pass




ARGUMENTLESS = 0
ARGUMENTED = 1
'''
Simple argument parser, a strip down of the one in ponysay and slitly modified
'''
class ArgParser():
    '''
    Constructor.
    The short description is printed on same line as the program name
    '''
    def __init__(self, program, description, usage, longdescription = None):
        self.__program = program
        self.__description = description
        self.__usage = usage
        self.__longdescription = longdescription
        self.__arguments = []
        (self.opts, self.optmap) = ({}, {})
    
    '''
    Add option that takes no arguments
    '''
    def add_argumentless(self, alternatives, help = None):
        ARGUMENTLESS
        self.__arguments.append((ARGUMENTLESS, alternatives, None, help))
        (stdalt, self.opts[stdalt]) = (alternatives[0], None)
        for alt in alternatives:  self.optmap[alt] = (stdalt, ARGUMENTLESS)
    
    '''
    Add option that takes one argument
    '''
    def add_argumented(self, alternatives, arg, help = None):
        self.__arguments.append((ARGUMENTED, alternatives, arg, help))
        (stdalt, self.opts[stdalt]) = (alternatives[0], None)
        for alt in alternatives:  self.optmap[alt] = (stdalt, ARGUMENTED)
    
    '''
    Parse arguments
    '''
    def parse(self, argv = sys.argv):
        self.argcount = len(argv) - 1
        self.files = []
        (dashed, get, dontget) = (False, 0, 0)
        (argqueue, optqueue, deque) = ([], [], [])
        for arg in argv[1:]:
            deque.append(arg)
        
        def unrecognised(arg):
            sys.stderr.write('%s: fatal: unrecognised option %s. see --help or the manual\n' % (self.__program, arg))
            exit(-1)
        
        while len(deque) != 0:
            (arg, deque) = (deque[0], deque[1:]) 
            if (get > 0) and (dontget == 0):
                get -= 1
                argqueue.append(arg)
            elif dashed:       self.files.append(arg)
            elif arg == '--':  dashed = True
            elif (len(arg) > 1) and ((arg[0] == '-') or (arg[0] == '+')):
                if (len(arg) > 2) and ((arg[:2] == '--') or (arg[:2] == '++')):
                    if dontget > 0:
                        dontget -= 1
                    elif (arg in self.optmap) and (self.optmap[arg][1] == ARGUMENTLESS):
                        optqueue.append(arg)
                        argqueue.append(None)
                    elif '=' in arg:
                        arg_opt = arg[:arg.index('=')]
                        if (arg_opt in self.optmap) and (self.optmap[arg_opt][1] == ARGUMENTED):
                            optqueue.append(arg_opt)
                            argqueue.append(arg[arg.index('=') + 1:])
                        else:
                            unrecognised(arg)
                    elif (arg in self.optmap) and (self.optmap[arg][1] == ARGUMENTED):
                        optqueue.append(arg)
                        get += 1
                    else:
                        unrecognised(arg)
                else:
                    (i, n, sign) = (1, len(arg), arg[0])
                    while i < n:
                        (narg, i) = (sign + arg[i], i + 1)
                        if narg in self.optmap:
                            optqueue.append(narg)
                            if self.optmap[narg][1] == ARGUMENTLESS:
                                argqueue.append(None)
                            else:
                                nargarg = arg[i:]
                                if len(nargarg) == 0:  get += 1
                                else:                  argqueue.append(nargarg)
                                break
                        else:
                            unrecognised(arg)
            else:
                self.files.append(arg)
        
        (i, n) = (0, len(optqueue))
        while i < n:
            (opt, arg, i) = (optqueue[i], argqueue[i], i + 1)
            opt = self.optmap[opt][0]
            if (opt not in self.opts) or (self.opts[opt] is None):
                self.opts[opt] = []
            self.opts[opt].append(arg)
        self.message = ' '.join(self.files) if len(self.files) > 0 else None
    
    
    '''
    Prints a colourful help message
    '''
    def help(self):
        print('\033[1m%s\033[21m - %s\n' % (self.__program, self.__description))
        if self.__longdescription is not None:
            print(self.__longdescription)
            print()
        print('\n\033[1mUSAGE:\033[21m', end='')
        first = True
        for line in self.__usage.split('\n'):
            if first:  first = False
            else:      print('    or', end='')
            print('\t%s' % (line))
        print('\n\033[1mCONFIGURATIONS:\033[21m\n')
        for opt in self.__arguments:
            (opt_type, opt_alts, opt_arg, opt_help) = opt[0:4]
            if opt_help is not None:
                for opt_alt in opt_alts:
                    if opt_alt is opt_alts[-1]:
                        print('\t%s \033[4m%s\033[24m' % (opt_alt, opt_arg) if opt_type == ARGUMENTED else '\t' + opt_alt)
                    else:
                        print('\t\033[2m' + opt_alt + '\033[22m')
                first = True
                for line in opt_help.split('\n'):
                    print(('\t\t\033[32;1m%s\033[21;39m' if first else '\t\t%s') % (line))
                    first = False
                print()
        print()



if __name__ == '__main__':
    Setup()

