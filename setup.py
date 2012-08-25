#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from subprocess import Popen, PIPE



PONYSAY_VERSION = '2.5'




#'en' must be first for manpages
#'ponies' must be first for sharedirs

manpages = [('en', 'English'), ('es', 'Spanish')]
sharedirs = [('ponies', 'xterm ponies', 'PONYDIR'), ('ttyponies', 'tty ponies', 'TTYPONYDIR'),
             ('extraponies', 'extra xterm ponies', 'XPONYDIR'), ('extrattyponies', 'extra tty ponies', 'XTTYPONYDIR'),
             ('quotes', 'pony quotes', 'QUOTEDIR'), ('balloons', 'balloon styles', 'BALLOONDIR')]
sharefiles = [('ucs', 'ucsmap')]
commands = ['ponysay', 'ponythink']
shells = [('bash', '/usr/share/bash-completion/completions/ponysay', 'GNU Bash'),
          ('fish', '/usr/share/fish/completions/ponysay.fish', 'Friendly interactive shell'),
          ('zsh', '/usr/share/zsh/site-functions/_ponysay', 'zsh')]
mansections = [('ponysay', '6'), ('cowsay', '1'), ('fortune', '6')]



class Setup():
    def __init__(self):
        usage_script = '\033[34;1msetup.py\033[21;39m'
        usage_help   = '(version | help)'
        usage_proc   = '[\033[4mconfigurations\033[24m] ([build] | prebuilt | install | (uninstall|clean)[-old])'
        
        usage = '%s %s\n%s %s' % (usage_script, usage_help, usage_script, usage_proc)
        
        usage = usage.replace('\033[', '\0')
        for sym in ('[', ']', '(', ')', '|', '...'):
            usage = usage.replace(sym, '\033[2m' + sym + '\033[22m')
            usage = usage.replace('\0', '\033[')
        
        opts = ArgParser(program     = 'setup.py',
                         description = 'installer for ponysay',
                         usage       = usage)
        
        
        opts.add_argumentless(alternatives = ['--help'])
        opts.add_argumentless(alternatives = ['--version'])
        
        opts.add_argumentless(help = 'Install everything that is not explicity excluded',                              alternatives = ['--everything', '--with-everything'])
        opts.add_argumentless(help = 'Install only the essentials\nNote that this can vary depending on version',      alternatives = ['--minimal'])
        opts.add_argumentless(help = 'Install nothing that is not explicity included',                                 alternatives = ['--nothing', '--with-nothing'])
        
        for command in commands:
            opts.add_argumentless(help = 'Do not install the %s command' % (command),                                              alternatives = ['--without-' + command])
            opts.add_argumented  (help = 'Install the %s command, and set file name\nDefualt = /usr/bin/%s' % (command, command),  alternatives = ['--with-' + command], arg='EXEC')
        
        opts.add_argumentless(help = 'Do not install a user shared cache',                                             alternatives = ['--without-shared-cache'])
        opts.add_argumented  (help = 'Install a user shared cache at CACHEDIR\nDefault = /var/cache/ponysay',          alternatives = [   '--with-shared-cache'], arg='CACHEDIR')
        
        for shell in shells:
            opts.add_argumentless(help = 'Do not install completion for ' + shell[2],                           alternatives = ['--without-' + shell[0]])
            opts.add_argumented  (help = 'Set file name for the completion for ponysay in' + shell[2],          alternatives = [   '--with-' + shell[0]], arg='PONYSAY_%s_FILE' % (shell[0].upper()))
        opts.add_argumentless(help = 'Only install explicitly included shell completions',                             alternatives = ['--without-shell'])
        opts.add_argumented  (help = 'Set share/ directory used for shell completions\nDefault = $SHAREDIR',           alternatives = [   '--with-shell'], arg='SHAREDIR')
        
        opts.add_argumentless(help = 'Do not install PDF manual\nDefault',                                             alternatives = ['--without-pdf'])
        opts.add_argumented  (help = 'Set directory for PDF manual\nDefault = $PREFIX/doc',                            alternatives = [   '--with-pdf'], arg='DOCDIR')
        opts.add_argumentless(help = 'Do not compress PDF manual\nDefault',                                            alternatives = ['--without-pdf-compression'])
        opts.add_argumented  (help = 'Select compression for PDF manual\nDefault = gz, xz is also recognised',         alternatives = [   '--with-pdf-compression'], arg='COMPRESSION')
        opts.add_argumentless(help = 'Do not install info manual',                                                     alternatives = ['--without-info'])
        opts.add_argumented  (help = 'Set directory for info manual\nDefault = $SHARE/info',                           alternatives = [   '--with-info'], arg='INFODIR')
        opts.add_argumentless(help = 'Do not use install-info when installing info manual',                            alternatives = ['--without-info-install'])
        opts.add_argumented  (help = 'Use install-info when installing info manual, and set description\nDefault',     alternatives = [   '--with-info-install'], arg='DESCIPTION')
        opts.add_argumentless(help = 'Do not compress info manual',                                                    alternatives = ['--without-info-compression'])
        opts.add_argumented  (help = 'Select compression for info manual\nDefault = gz, xz is also recognised',        alternatives = [   '--with-info-compression'], arg='COMPRESSION')
        
        for man in manpages:
            opts.add_argumentless(help = 'Do not install %s manpage manual' % (man[1]),                                alternatives = ['--without-man-' + man[0]])
            opts.add_argumented  (help = 'Set directory for %s manpage\nDefault = $SHARE/man' % (man[1]),              alternatives = [   '--with-man-' + man[0]], arg='MANDIR')
        opts.add_argumentless(help = 'Do not install any manpages',                                                    alternatives = ['--without-man'])
        opts.add_argumented  (help = 'Set directory for all man pages\nDefault = $SHARE/man',                          alternatives = [   '--with-man'], arg='MANDIR')
        for man in manpages:
            opts.add_argumentless(help = 'Do not compress %s manpage' % (man[1]),                                      alternatives = ['--without-man-%s-compression' % (man[0])])
            opts.add_argumented  (help = 'Select compression for %s manpage\nDefault = gz, xz is also recognised' % (man[1]),
                                                                                                                     alternatives = [   '--with-man-%s-compression' % (man[0])], arg='COMPRESSION')
        opts.add_argumentless(help = 'Do not compress any installed manpage',                                          alternatives = ['--without-man-compression'])
        opts.add_argumented  (help = 'Select compression for installed manpages\nDefault = gz, xz is also recognised', alternatives = [   '--with-man-compression'], arg='COMPRESSION')
        
        for man in mansections:
            opts.add_argumented  (help = 'Change the section for the %s manpage\nDefault = %s' % man,                  alternatives = ['--man-section-' + man[0]], arg='SECTION')
        
        for dir in sharedirs:
            opts.add_argumentless(help = 'Do not install ' + dir[0],                                                   alternatives = ['--without-' + dir[0]])
            opts.add_argumented  (help = 'Set directory for %s\nDefault = $SHAREDIR/ponysay/%s' % (dir[1], dir[0]),    alternatives = [   '--with-' + dir[0]], arg=dir[2])
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
        
        opts.add_argumented  (help = 'Set off environment for installation\nEmpty by default',                                    alternatives = ['--dest-dir'], arg='DESTDIR')
        
        
        opts.parse()
        
        
        if (len(opts.files) > 1) or (opts.opts['--help'] is not None) or ((len(opts.files) == 1) and (opts.files[0] == 'help')):
            opts.help()
        elif (opts.opts['--version'] is not None) or ((len(opts.files) == 1) and (opts.files[0] == 'version')):
            print('Ponysay %s installer' % (PONYSAY_VERSION))
        else:
            if len(opts.files) == 0:
                opts.files = ['build']
            method = opts.files[0]
            if   method == 'clean':      self.clean()
            elif method == 'clean-old':  self.cleanOld()
            else:
                conf = self.configure(opts.opts)
                self.viewconf(conf)
                if   method == 'build':          self.build       (conf)
                elif method == 'prebuilt':       self.install     (conf)
                elif method == 'install':        self.build       (conf); self.install(conf); self.clean()
                elif method == 'uninstall':      self.uninstall   (conf)
                elif method == 'uninstall-old':  self.uninstallOld(conf)
                else:
                    opts.help()
    
    
    '''
    Display configurations
    '''
    def viewconf(self, conf):
        RED = '\033[31m%s\033[39m'
        GREEN = '%s\033[32m%s\033[39m'
        YELLOW = '\033[33m%s\033[39m'
        
        for command in commands:
            if conf[command]:                      print(GREEN  % ('Installing command ' + command + ' as ', conf[command]))
            else:                                  print(RED    % ('Skipping installion of command ' + command))
        if conf['shared-cache'] is not None:       print(GREEN  % ('Installing shared cache at ', conf['shared-cache']))
        else:                                      print(RED    % ('Skipping installation of shared cache'))
        for shell in [item[0] for item in shells]:
            if conf[shell] is not None:            print(GREEN  % ('Installing auto-completion for ' + shell + ' as ', conf[shell]))
            else:                                  print(RED    % ('Skipping installation of auto-completion for ' + shell))
        if conf['pdf'] is not None:                print(GREEN  % ('Installing PDF manual to ', conf['pdf']))
        else:                                      print(RED    % ('Skipping installation of PDF manual'))
        if conf['pdf-compression'] is not None:    print(GREEN  % ('Compressing PDF manual with ', conf['pdf-compression']))
        else:                                      print(RED    % ('Skipping compression of PDF manual'))
        if conf['info'] is not None:               print(GREEN  % ('Installing info manual to ', conf['info']))
        else:                                      print(RED    % ('Skipping installation of info manual'))
        if conf['info-install'] is not None:       print(GREEN  % ('Installing info manual with install-info with description: ', conf['info-install']))
        else:                                      print(RED    % ('Skipping installation of info manual with install-info'))
        if conf['info-compression'] is not None:   print(GREEN  % ('Compressing info manual with ', conf['info-compression']))
        else:                                      print(RED    % ('Skipping compression of info manual'))
        for man in manpages:
            key = 'man-' + man[0]
            if conf[key] is not None:              print(GREEN  % ('Installing ' + man[1] + ' manpage to ', conf[key]))
            else:                                  print(RED    % ('Skipping installation of ' + man[1] + ' manpage'))
            key += '-compression'
            if conf[key] is not None:              print(GREEN  % ('Compressing ' + man[1] + ' manpage with ', conf[key]))
            else:                                  print(RED    % ('Skipping compression of ' + man[1] + ' manpage'))
        for man in mansections:                    print(GREEN  % ('References to manpage for ' + man[1] + ' points to section ', conf['man-section-' + man[0]]))
        for dir in sharedirs:
            if conf[dir[0]] is not None:           print(GREEN  % ('Installing ' + dir[1] + ' to ', conf[dir[0]]))
            else:                                  print(RED    % ('Skipping installation of ' + dir[1]))
        for file in sharefiles:
            if conf[file[0]] is not None:          print(GREEN  % ('Installing ' + file[1] + ' as ', conf[file[0]]))
            else:                                  print(RED    % ('Skipping installation of ' + file[1]))
        if conf['custom-env-python'] is not None:  print(GREEN  % ('Using custom env reference in python script shebang: ', conf['custom-env-python']))
        else:                                      print(YELLOW % ('Looking for best env reference in python script shebang'))
        
        print()
    
    
    '''
    Compile ponysay
    '''
    def build(self, conf):
        print('\033[1;34m::\033[39mCompiling...\033[21m')
        
        pass
    
    
    '''
    Install compiled ponysay
    '''
    def install(self, conf):
        print('\033[1;34m::\033[39mInstalling...\033[21m')
        
        pass
    
    
    '''
    Uninstall ponysay
    '''
    def uninstall(self, conf):
        print('\033[1;34m::\033[39mUninstalling...\033[21m')
        
        pass
    
    
    '''
    Uninstall file ponysay no longer uses
    '''
    def uninstallOld(self, conf):
        print('\033[1;34m::\033[39mUninstalling old files...\033[21m')
        
        instdir = conf['~prefix~'] + '/usr'
        files = [instdir + f for f in ['bin/ponysaylist.pl', 'bin/ponysaytruncater', 'bin/ponysay.py', 'bin/ponythink.py']]
        dirs = [instdir + d for d in ['lib/ponysay', 'share/ponies', 'share/ttyponies']]
        #$(instdir)/lib/ponysay/truncater
        #$(instdir)/lib/ponysay/list.pl
        #$(instdir)/lib/ponysay/linklist.pl
        #$(instdir)/lib/ponysay/pq4ps
        #$(instdir)/lib/ponysay/pq4ps.pl
        #$(instdir)/lib/ponysay/pq4ps-list
        #$(instdir)/lib/ponysay/pq4ps-list.pl
        
        self.removeLists(files, dirs)
    
    
    '''
    Remove compiled files
    '''
    def clean(self):
        print('\033[1;34m::\033[39mCleaning...\033[21m')
        
        files = ['ponysay.info', 'ponysay.info.gz', 'ponysay.info.xz', 'ponysay.install']
        dirs = ['quotes']
        for comp in ['gz', 'xz']:
            for man in manpages:
                if man is manpages[0]:  man = ''
                else:                   man = '.' + man[0]
                files.append('manuals/manpage.0' + man + '.' + comp)
        for shell in [item[0] for item in shells]:
            files.append('completion/%s-completion.%s.install' % (shell, 'is' if shell == 'bash' else shell))
            files.append('completion/%s-completion-think.%s'   % (shell, 'is' if shell == 'bash' else shell))
        
        self.removeLists(files, dirs)
    
    
    '''
    Remove compiled files ponysay is no longer compiling
    '''
    def cleanOld(self):
        print('\033[1;34m::\033[39mCleaning old files...\033[21m')
        
        files = ['truncater', 'ponysaytruncater', 'ponysay.py.install', 'ponysay.install~']
        dirs = []
        
        self.removeLists(files, dirs)
    
    
    '''
    Removes listed files and directories
    '''
    def removeLists(self, files, dirs):
        pass ## TODO not implemented
    
    
    '''
    Parses configurations
    '''
    def configure(self, opts):
        (defaults, conf) = ({}, {})
        
        for command in commands:
            conf[command] = '/usr/bin/' + command
        conf['shared-cache'] = '/var/cache/ponysay'
        for shell in shells:
            conf[shell[0]] = shell[1]
        conf['pdf'] = '/usr/doc'
        conf['pdf-compression'] = 'gz'
        conf['info'] = '/usr/share/info'
        conf['info-install'] = 'My Little Ponies for your terminal'
        conf['info-compression'] = 'gz'
        for manpage in manpages:
            conf['man-' + manpage[0]] = '/usr/share/man'
            conf['man-' + manpage[0] + '-compression'] = 'gz'
        for sharedir in sharedirs:
            conf[sharedir[0]] = '/usr/share/ponysay/' + sharedir[0]
        for sharefile in sharefiles:
            conf[sharefile[0]] = '/usr/share/ponysay/' + sharefile[1]
        conf['custom-env-python'] = 'python3'
        
        
        if opts['--private'] is not None:
            if opts['--prefix'] is None:
                opts['--prefix'] = [os.environ['HOME'] + '/.local']
        
        prefix = '/usr'
        if opts['--prefix'] is not None:
            prefix = opts['--prefix'][0]
            for key in conf:
                if conf[key] not in (None, False, True):
                    if conf[key].startswith('/usr'):
                        conf[key] = prefix + conf[key][4:]
        conf['~prefix~'] = prefix
        
        if opts['--opt'] is not None:
            if opts['--bin-dir']           is None:  opts['--bin-dir']           = ['/opt/ponysay/bin']
            if opts['--lib-dir']           is None:  opts['--lib-dir']           = ['/opt/ponysay/lib']
            if opts['--share-dir']         is None:  opts['--share-dir']         = ['/opt/ponysay/share']
            if opts['--with-shared-cache'] is None:  opts['--with-shared-cache'] = ['/var/opt/ponysay/cache']
        
        for dir in ['bin', 'lib', 'share']:
            if opts['--' + dir + '-dir'] is not None:
                d = opts['--' + dir + '-dir'][0]
                for key in conf:
                    if conf[key] not in [None, True, False]:
                        if conf[key].startswith(prefix + '/' + dir):
                            conf[key] = d + conf[key][5 + len(dir):]
        if opts['--cache-dir'] is not None:
            dir = opts['--cache-dir'][0]
            for key in conf:
                if conf[key] not in (None, False, True):
                    if conf[key].startswith('/var/cache'):
                        conf[key] = dir + conf[key][10:]
        
        
        for key in conf:
            defaults[key] = conf[key]
        
        
        if opts['--nothing'] is not None:
            opts['--minimal'] = opts['--nothing']
        
        for key in ['custom-env-python']:
            conf[key] = None
        
        
        if opts['--everything'] is None:
            for key in ['pdf', 'pdf-compression']:
                conf[key] = None
            
            nomanen = opts['--minimal'] is not None
            for manpage in manpages:
                if (manpage is not manpages[0]) or nomanen:
                    for key in ['man-' + manpage[0]]:
                        conf[key] = None
        
        if (opts['--private'] is not None) or (opts['--minimal'] is not None):
            for key in ['info-install', 'shared-cache']:
                conf[key] = None
        
        if opts['--minimal'] is not None:
            for key in ['info', 'info-compression'] + [item[0] for item in shells]:
                conf[key] = None
            for sharedir in sharedirs:
                if sharedir is not sharedirs[0]:
                    conf[sharedir[0]] = None
            for sharefile in sharefiles:
                conf[sharefile[0]] = None
        
        if opts['--nothing'] is not None:
            for command in commands:
                conf[command] = False
            conf[sharedirs[0][0]] = None
        
        
        for coll in [['shell', '/usr/share', [item[0] for item in shells]],
                     ['man', '/usr/share/man', ['man-' + item[0] for item in manpages]],
                     ['man-compression', 'gz', ['man-' + item[0] + '-compression' for item in manpages]]
                    ]:
            if opts['--without-' + coll[0]] is not None:
                for item in coll[2]:
                    conf[item] = None
            if opts['--with-' + coll[0]] is not None:
                for item in coll[2]:
                    defaults[item] = conf[item] = defaults[item].replace(coll[1], coll[1] if opts['--with-' + coll[0]][0] is None else opts['--with-' + coll[0]][0]);
        
        
        for key in conf:
            if opts['--with-' + key] is not None:
                if defaults[key] in (False, True):
                    conf[key] = True
                else:
                    conf[key] = defaults[key] if opts['--with-' + key][0] is None else opts['--with-' + key][0]
            if opts['--without-' + key] is not None:
                conf[key] = False if defaults[key] in (False, True) else None
        
        for mansection in mansections:
            if opts['--man-section-' + mansection[0]] is not None:
                conf['man-section-' + mansection[0]] = opts['--man-section-' + mansection[0]]
            else:
                conf['man-section-' + mansection[0]] = mansection[1]
        
        
        if opts['--dest-dir'] is not None:
            destdir = opts['--dest-dir'][0]
            for key in conf:
                if conf[key] not in (None, False, True):
                    if conf.startswith('/'):
                        conf[key] = destdir + conf[key]
        
        return conf



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
        (argqueue, optqueue, get) = ([], [], False)
        
        for arg in argv[1:]:
            if get:
                get = False
                if (len(arg) > 2) and (arg[:2] in ('--', '++')):
                    argqueue.append(None)
                else:
                    argqueue.append(arg)
                    continue
            if (len(arg) > 2) and (arg[:2] in ('--', '++')):
                if (arg in self.optmap) and (self.optmap[arg][1] == ARGUMENTLESS):
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
                    get = True
                else:
                    sys.stderr.write('%s: fatal: unrecognised option %s. see --help or the manual\n' % (self.__program, arg))
                    exit(-1)
            else:
                self.files.append(arg)
        
        (i, n) = (0, len(optqueue))
        if len(argqueue) < n:
            argqueue.append(None)
        while i < n:
            (opt, arg, i) = (optqueue[i], argqueue[i], i + 1)
            opt = self.optmap[opt][0]
            if (opt not in self.opts) or (self.opts[opt] is None):
                self.opts[opt] = []
            self.opts[opt].append(arg)
    
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

