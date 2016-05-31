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


Authors:

         Erkin Batu Altunbaş:              Project leader, helped write the first implementation
         Mattias "maandree" Andrée:        Major contributor of both implementions
         Elis "etu" Axelsson:              Major contributor of current implemention and patcher of the first implementation
         Sven-Hendrik "svenstaro" Haase:   Major contributor of the first implementation
         Jan Alexander "heftig" Steffens:  Major contributor of the first implementation
         Kyah "L-four" Rindlisbacher:      Patched the first implementation
'''
from common import *
from argparser import *
from ponysay import *



'''
Start the program
'''
if __name__ == '__main__':
    istool = sys.argv[0]
    if os.sep in istool:
        istool = istool[istool.rfind(os.sep) + 1:]
    if os.extsep in istool:
        istool = istool[:istool.find(os.extsep)]
    istool = istool.endswith('-tool')
    if istool:
        from ponysaytool import * ## will start ponysay-tool
        exit(0)
    
    isthink = sys.argv[0]
    if os.sep in isthink:
        isthink = isthink[isthink.rfind(os.sep) + 1:]
    if os.extsep in isthink:
        isthink = isthink[:isthink.find(os.extsep)]
    isthink = isthink.endswith('think')
    
    usage_saythink = '\033[34;1m(ponysay | ponythink)\033[21;39m'
    usage_common   = '[-c] [-W\033[33mCOLUMN\033[39m] [-b\033[33mSTYLE\033[39m]'
    usage_listhelp = '(-l | -L | -B | +l | +L | -A | + A | -v | -h)'
    usage_file     = '[-f\033[33mPONY\033[39m]* [[--] \033[33mmessage\033[39m]'
    usage_xfile    = '(+f\033[33mPONY\033[39m)* [[--] \033[33mmessage\033[39m]'
    usage_afile    = '(-F\033[33mPONY\033[39m)* [[--] \033[33mmessage\033[39m]'
    usage_quote    = '(-q\033[33mPONY\033[39m)*'
    
    usage = ('%s %s' + 4 * '\n%s %s %s') % (usage_saythink, usage_listhelp,
                                            usage_saythink, usage_common, usage_file,
                                            usage_saythink, usage_common, usage_xfile,
                                            usage_saythink, usage_common, usage_afile,
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
    opts.add_argumentless(['--Onelist'])
    
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
    
    _F = ['--any-file', '--anyfile', '--any-pony', '--anypony']
    __F = [_.replace("pony", "ponie") + 's' for _ in _F]
    opts.add_argumentless(['-h', '--help'],                                        help = 'Print this help message.')
    opts.add_argumentless(['+h', '++help', '--help-colour'],                       help = 'Print this help message with colours even if piped.')
    opts.add_argumentless(['-v', '--version'],                                     help = 'Print the version of the program.')
    opts.add_argumentless(['-l', '--list'],                                        help = 'List pony names.')
    opts.add_argumentless(['-L', '--symlist', '--altlist'],                        help = 'List pony names with alternatives.')
    opts.add_argumentless(['+l', '++list'],                                        help = 'List non-MLP:FiM pony names.')
    opts.add_argumentless(['+L', '++symlist', '++altlist'],                        help = 'List non-MLP:FiM pony names with alternatives.')
    opts.add_argumentless(['-A', '--all'],                                         help = 'List all pony names.')
    opts.add_argumentless(['+A', '++all', '--symall', '--altall'],                 help = 'List all pony names with alternatives.')
    opts.add_argumentless(['-B', '--bubblelist', '--balloonlist'],                 help = 'List balloon styles.')
    opts.add_argumentless(['-c', '--compress', '--compact'],                       help = 'Compress messages.')
    opts.add_argumentless(['-o', '--pony-only', '--ponyonly'],                     help = 'Print only the pony.')
    opts.add_argumented(  ['-W', '--wrap'],                        arg = 'COLUMN', help = 'Specify column where the message should be wrapped.')
    opts.add_argumented(  ['-b', '--bubble', '--balloon'],         arg = 'STYLE',  help = 'Select a balloon style.')
    opts.add_argumented(  ['-f', '--file', '--pony'],              arg = 'PONY',   help = 'Select a pony.\nEither a file name or a pony name.')
    opts.add_argumented(  ['+f', '++file', '++pony'],              arg = 'PONY',   help = 'Select a non-MLP:FiM pony.')
    opts.add_argumented(  ['-F'] + _F,                             arg = 'PONY',   help = 'Select a pony, that can be a non-MLP:FiM pony.')
    opts.add_argumented(  ['-q', '--quote'],                       arg = 'PONY',   help = 'Select a pony which will quote herself.')
    opts.add_variadic(    ['--f', '--files', '--ponies'],          arg = 'PONY')
    opts.add_variadic(    ['++f', '++files', '++ponies'],          arg = 'PONY')
    opts.add_variadic(    ['--F'] + __F,                           arg = 'PONY')
    opts.add_variadic(    ['--q', '--quotes'],                     arg = 'PONY')
    
    '''
    Whether at least one unrecognised option was used
    '''
    unrecognised = not opts.parse()
    
    
    ## Start
    ponysay = Ponysay()
    ponysay.unrecognised = unrecognised
    ponysay.run(opts)
