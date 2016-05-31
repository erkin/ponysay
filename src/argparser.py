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



ARGUMENTLESS = 0
'''
Option takes no arguments
'''

ARGUMENTED = 1
'''
Option takes one argument per instance
'''

VARIADIC = 2
'''
Option consumes all following arguments
'''



class ArgParser():
    '''
    Simple argument parser
    '''
    
    def __init__(self, program, description, usage, longdescription = None):
        '''
        Constructor.
        The short description is printed on same line as the program name
        
        @param  program:str          The name of the program
        @param  description:str      Short, single-line, description of the program
        @param  usage:str            Formated, multi-line, usage text
        @param  longdescription:str  Long, multi-line, description of the program, may be `None`
        '''
        self.linuxvt = ('TERM' in os.environ) and (os.environ['TERM'] == 'linux')
        self.__program = program
        self.__description = description
        self.__usage = usage
        self.__longdescription = longdescription
        self.__arguments = []
        self.opts = {}
        self.optmap = {}
    
    
    def add_argumentless(self, alternatives, help = None):
        '''
        Add option that takes no arguments
        
        @param  alternatives:list<str>  Option names
        @param  help:str                Short description, use `None` to hide the option
        '''
        self.__arguments.append((ARGUMENTLESS, alternatives, None, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, ARGUMENTLESS)
    
    def add_argumented(self, alternatives, arg, help = None):
        '''
        Add option that takes one argument
        
        @param  alternatives:list<str>  Option names
        @param  arg:str                 The name of the takes argument, one word
        @param  help:str                Short description, use `None` to hide the option
        '''
        self.__arguments.append((ARGUMENTED, alternatives, arg, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, ARGUMENTED)
    
    def add_variadic(self, alternatives, arg, help = None):
        '''
        Add option that takes all following argument
        
        @param  alternatives:list<str>  Option names
        @param  arg:str                 The name of the takes arguments, one word
        @param  help:str                Short description, use `None` to hide the option
        '''
        self.__arguments.append((VARIADIC, alternatives, arg, help))
        stdalt = alternatives[0]
        self.opts[stdalt] = None
        for alt in alternatives:
            self.optmap[alt] = (stdalt, VARIADIC)
    
    
    def parse(self, argv = sys.argv):
        '''
        Parse arguments
        
        @param   args:list<str>  The command line arguments, should include the execute file at index 0, `sys.argv` is default
        @return  :bool           Whether no unrecognised option is used
        '''
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
    
    
    def help(self, use_colours = None):
        '''
        Prints a colourful help message
        
        @param  use_colours:bool?  Whether to use colours, `None` if stdout is not piped
        '''
        if use_colours is None:
            use_colours = sys.stdout.isatty()
        
        print(('\033[1m%s\033[21m %s %s' if use_colours else '%s %s %s') % (self.__program, '-' if self.linuxvt else '—', self.__description))
        print()
        if self.__longdescription is not None:
            desc = self.__longdescription
            if not use_colours:
                while '\033' in desc:
                    esc = desc.find('\033')
                    desc = desc[:esc] + desc[desc.find('m', esc) + 1:]
            print(desc)
        print()
        
        print('\033[1mUSAGE:\033[21m' if use_colours else 'USAGE:', end='')
        first = True
        for line in self.__usage.split('\n'):
            if first:
                first = False
            else:
                print('    or', end='')
            if not use_colours:
                while '\033' in line:
                    esc = line.find('\033')
                    line = line[:esc] + line[line.find('m', esc) + 1:]
            print('\t%s' % line)
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
        
        print('\033[1mSYNOPSIS:\033[21m' if use_colours else 'SYNOPSIS')
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
                    if use_colours:
                        if   opt_type == ARGUMENTED:  line += ' \033[4m%s\033[24m'      % (opt_arg);  l += len(opt_arg) + 1
                        elif opt_type == VARIADIC:    line += ' [\033[4m%s\033[24m...]' % (opt_arg);  l += len(opt_arg) + 6
                    else:
                        if   opt_type == ARGUMENTED:  line += ' %s'      % (opt_arg);  l += len(opt_arg) + 1
                        elif opt_type == VARIADIC:    line += ' [%s...]' % (opt_arg);  l += len(opt_arg) + 6
                else:
                    if use_colours:
                        line += '    \033[2m%s\033[22m  ' % (opt_alt)
                    else:
                        line += '    %s  ' % (opt_alt)
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
            colour = ('36' if (index & 1) == 0 else '34') if use_colours else ''
            print(lines[index].replace('%colour%', ('\033[%s;1m' % colour) if use_colours else ''), end=' ' * (col - lens[index]))
            for line in opt_help.split('\n'):
                if first:
                    first = False
                    print('%s' % (line), end='\033[21;39m\n' if use_colours else '\n')
                else:
                    print(('%s\033[%sm%s\033[39m' if use_colours else '%s%s%s') % (' ' * col, colour, line))
            index += 1
        
        print()

