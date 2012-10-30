#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies
Copyright (C) 2012  Erkin Batu Altunbaş et al.

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.
'''

import os
import sys
from subprocess import Popen, PIPE

from ponysay import *


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



'''
This is the mane class of ponysay-tool
'''
class PonysayTool():
    '''
    Starts the part of the program the arguments indicate
    
    @param  args:ArgParser  Parsed command line arguments
    '''
    def __init__(self, args):
        if args.argcount == 0:
            args.help()
            exit(255)
            return
        
        opts = args.opts
        
        if unrecognised or (opts['-h'] is not None):
            args.help()
            if unrecognised:
                exit(254)
        
        elif opts['-v'] is not None:
            print('%s %s' % ('ponysay', VERSION))
        
        elif (opts['--edit'] is not None) and (len(opts['--edit']) == 1):
            pony = opts['--edit'][0]
            if not os.path.isfile(pony):
                printerr('%s is not an existing regular file' % pony)
                exit(252)
            linuxvt = ('TERM' in os.environ) and (os.environ['TERM'] == 'linux')
            try:
                print('\033[?1049h', end='') # initialise terminal
                if linuxvt: print('\033[?8c', end='') # use full block for cursor (_ is used by default in linux vt)
                cmd = 'stty %s < %s > /dev/null 2> /dev/null'
                cmd %= ('-echo -icanon -isig', os.path.realpath('/dev/stdout'))
                Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).wait()
                self.editmeta(pony)
            finally:
                cmd = 'stty %s < %s > /dev/null 2> /dev/null'
                cmd %= ('echo icanon isig', os.path.realpath('/dev/stdout'))
                Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).wait()
                if linuxvt: print('\033[?0c', end='') # restore cursor
                print('\033[?1049l', end='') # terminate terminal
        
        else:
            exit(253)
    
    
    '''
    Edit a pony file's meta data
    
    @param  ponyfile:str  A pony file to edit
    '''
    def editmeta(self, ponyfile):
        (data, meta, image) = 3 * [None]
        
        with open(ponyfile, 'rb') as file:
            data = file.read().decode('utf8', 'replace')
            data = [line.replace('\n', '') for line in data.split('\n')]
        
        if data[0] != '$$$':
            image = data
            meta = []
        else:
            sep = 1
            while data[sep] != '$$$':
                sep += 1
            meta = data[1:][:sep]
            image = data[sep + 1:]
        
        class PhonyArgParser:
            def __init__(self):
                self.argcount = 3
                self.message = ponyfile
                self.opts = self
            def __getitem__(self, key):
                return [ponyfile] if key == '-f' else None
        
        
        data = {}
        comment = []
        for line in data:
            if ': ' in line:
                key = line.replace('\t', ' ')
                key = key[:key.find(': ')]
                key = key.strip(' ')
                if key == key.upper():
                    value = line.replace('\t', ' ')
                    value = keyvalue[key.find(': ') + 2:]
                    data[key] = value.strip(' ')
                else:
                    comment.append(line)
        
        cut = 0
        while (len(comment) > cut) and (len(comment[cut]) == 0):
            cut += 1
        comment = comment[cut:]
        
        
        stdout = sys.stdout
        class StringInputStream:
            def __init__(self):
                self.buf = ''
                class Buffer:
                    def __init__(self, parent):
                        self.parent = parent
                    def write(self, data):
                        self.parent.buf += data.decode('utf8', 'replace')
                    def flush(self):
                        pass
                self.buffer = Buffer(self)
            def flush(self):
                pass
            def isatty(self):
                return True
        sys.stdout = StringInputStream()
        ponysay = Ponysay()
        ponysay.run(PhonyArgParser())
        printpony = sys.stdout.buf[:-1].split('\n')
        sys.stdout = stdout
        
        preprint = '\033[H\033[2J'
        if printpony[0].startswith(preprint):
            printpony[0] = printpony[0][len(preprint):]
        ponyheight = len(printpony)
        ponywidth = Backend.len(max(printpony, key = Backend.len))
        
        ## Call `stty` to determine the size of the terminal, this way is better then using python's ncurses
        termsize = None
        for channel in (sys.stdout, sys.stdin, sys.stderr):
            termsize = Popen(['stty', 'size'], stdout=PIPE, stdin=channel, stderr=PIPE).communicate()[0]
            if len(termsize) > 0:
                termsize = termsize.decode('utf8', 'replace')[:-1].split(' ') # [:-1] removes a \n
                termsize = [int(item) for item in termsize]
                break
        
        AUTO_PUSH = '\033[01010~'
        AUTO_POP  = '\033[10101~'
        modprintpony = '\n'.join(printpony).replace('\n', AUTO_PUSH + '\n' + AUTO_POP)
        colourstack = ColourStack(AUTO_PUSH, AUTO_POP)
        buf = ''
        for c in modprintpony:
            buf += c + colourstack.feed(c)
        modprintpony = buf.replace(AUTO_PUSH, '').replace(AUTO_POP, '')
        
        printpony = [('\033[21;39;49;0m%s%s\033[21;39;49;0m' % (' ' * (termsize[1] - ponywidth), line)) for line in modprintpony.split('\n')]
        
        
        print(preprint, end='')
        print('\n'.join(printpony), end='')
        print('\033[H', end='')
        print('Please see the info manual for details on how to fill out this form')
        print()
        
        
        if 'WIDTH'  in data:  del data['WIDTH']
        if 'HEIGHT' in data:  del data['HEIGHT']
        data['comment'] = '\n'.join(comment)
        fields = [key for key in data]
        fields.sort()
        standardfields = ['GROUP NAME', 'NAME', 'OTHER NAMES', 'APPEARANCE', 'KIND',
                          'GROUP', 'BALLOON', 'LINK', 'LINK ON', 'COAT', 'MANE', 'EYE',
                          'AURA', 'DISPLAY', 'MASTER', 'SOURCE', 'MEDIA', 'comment']
        for standard in standardfields:
            if standard in fields:
                del fields[fields.index(standard)]
            if standard not in data:
                data[standard] = ''
        
        fields = standardfields[:-1] + fields + [standardfields[-1]]
        
        
        for key in fields:
            print('\033[34m%s:\033[39m' % key)
        
        input()
        
        comment = data['comment']
        del data['comment']
        comment = ('\n' + comment + '\n').replace('\n$$$\n', '\n\\$$$\n')[:-1]



'''
Start the program from ponysay.__init__ if this is the executed file
'''
if __name__ == '__main__':
    '''
    The user's home directory
    '''
    HOME = os.environ['HOME'] if 'HOME' in os.environ else os.path.expanduser('~')
    
    '''
    Whether stdin is piped
    '''
    pipelinein = not sys.stdin.isatty()
    
    '''
    Whether stdout is piped
    '''
    pipelineout = not sys.stdout.isatty()
    
    '''
    Whether stderr is piped
    '''
    pipelineerr = not sys.stderr.isatty()
    
    
    usage_program = '\033[34;1mponysay-tool\033[21;39m'
    
    usage = '\n'.join(['%s %s' % (usage_program, '(--help | --version)'),
                       '%s %s' % (usage_program, '--edit \033[4mPONY-FILE\033[24m'),])
    
    usage = usage.replace('\033[', '\0')
    for sym in ('[', ']', '(', ')', '|', '...', '*'):
        usage = usage.replace(sym, '\033[2m' + sym + '\033[22m')
    usage = usage.replace('\0', '\033[')
    
    '''
    Argument parsing
    '''
    opts = ArgParser(program     = 'ponysay-tool',
                     description = 'Tool chest for ponysay',
                     usage       = usage,
                     longdescription = None)
    
    opts.add_argumentless(['-h', '--help'],                         help = 'Print this help message.')
    opts.add_argumentless(['-v', '--version'],                      help = 'Print the version of the program.')
    opts.add_argumented(  ['--edit'],           arg = 'PONY-FILE',  help = 'Edit a pony file\'s meta data')
    
    '''
    Whether at least one unrecognised option was used
    '''
    unrecognised = not opts.parse()
    
    PonysayTool(args = opts)

