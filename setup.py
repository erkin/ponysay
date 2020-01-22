#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
from zipfile import ZipFile
from subprocess import Popen, PIPE

PONYSAY_VERSION = '3.0.4'

project_dir = os.path.dirname(__file__)

manpages = [('en', 'English'),  # must be first
            ('es', 'Spanish'),
            ('sv', 'Swedish'),
            ('tr', 'Turkish')]

sharedirs = [('ponies', 'xterm ponies', 'PONYDIR', True),  # must be first
             ('ttyponies', 'tty ponies', 'TTYPONYDIR', True),
             ('extraponies', 'extra xterm ponies', 'XPONYDIR', True),
             ('extrattyponies', 'extra tty ponies', 'XTTYPONYDIR', True),
             ('quotes', 'pony quotes', 'QUOTEDIR', False),
             ('balloons', 'balloon styles', 'BALLOONDIR', False)]

sharefiles = [('ucs', 'ucsmap')]

commands = ['ponysay', 'ponythink', 'ponysay-tool']

shells = [('bash', '/usr/share/bash-completion/completions/ponysay', 'GNU Bash'),
          ('fish', '/usr/share/fish/vendor_completions.d/ponysay.fish', 'Friendly interactive shell'),
          ('zsh', '/usr/share/zsh/site-functions/_ponysay', 'zsh')]

mansections = [('ponysay', '6'),
               ('cowsay', '1'),
               ('fortune', '6'),
               ('ponysay-tool', '6')]

miscfiles = [('COPYING', '/usr/share/licenses/ponysay/COPYING'),
             ('LICENSE', '/usr/share/licenses/ponysay/LICENSE'),
             ('CREDITS', '/usr/share/licenses/ponysay/CREDITS')]

ponysaysrc = [i for i in os.listdir(os.path.join(project_dir, 'src')) if i.endswith('.py') and not i.startswith('.')]

COPY = 'copy'
HARD = 'hard'
SYMBOLIC = 'symbolic'

class Setup():
    def __init__(self):
        usage_script = '\033[34;1msetup.py\033[21;39m'
        usage_help   = '(--version | --help)'
        usage_proc   = '[\033[4mconfigurations\033[24m] ([build] | prebuilt | install | (uninstall|clean)[-old] | view)'

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
        opts.add_argumented  (alternatives = ['---DESTDIR'], arg="DESTDIR")
        opts.add_argumented  (alternatives = ['---PREFIX'], arg="PREFIX")

        opts.add_argumentless(help = 'Install everything that is not explicitly excluded',
                              alternatives = ['--everything', '--with-everything'])

        opts.add_argumentless(help = 'Install only the essentials\nNote that this can vary depending on the version',
                              alternatives = ['--minimal'])

        opts.add_argumentless(help = 'Install nothing (except legal documents) that is not explicitly included',
                              alternatives = ['--nothing', '--with-nothing'])

        for command in commands:
            opts.add_argumentless(help = 'Do not install the %s command' % (command),
                                  alternatives = ['--without-' + command, '--without-' + command + '-command'])

            opts.add_argumented  (help = 'Install the %s command, and set file name\nDefault = /usr/bin/%s' % (command, command),
                                  alternatives = ['--with-' + command, '--with-' + command + '-command'], arg='EXEC')

        opts.add_argumentless(help = 'Do not install a user shared cache',
                              alternatives = ['--without-shared-cache'])

        opts.add_argumented  (help = 'Install a user shared cache at CACHEDIR\nDefault = /var/cache/ponysay',
                              alternatives = [   '--with-shared-cache'], arg='CACHEDIR')

        for shell in shells:
            opts.add_argumentless(help = 'Do not install completion for ' + shell[2],
                                  alternatives = ['--without-' + shell[0], '--without-' + shell[0] + '-completion'])

            opts.add_argumented  (help = 'Set file name for the completion for ponysay in' + shell[2],
                                  alternatives = ['--with-' + shell[0], '--with-' + shell[0] + '-completion'], arg='PONYSAY_%s_FILE' % (shell[0].upper()))

        opts.add_argumentless(help = 'Only install explicitly included shell completions',
                              alternatives = ['--without-shell', '--without-shell-completion'])

        opts.add_argumented  (help = 'Set share/ directory used for shell completions\nDefault = $SHAREDIR',
                              alternatives = ['--with-shell', '--with-shell-completion'], arg='SHAREDIR')

        opts.add_argumentless(help = 'Do not install PDF manual\nDefault',
                              alternatives = ['--without-pdf', '--without-pdf-manual'])

        opts.add_argumented  (help = 'Set directory for PDF manual\nDefault = $PREFIX/doc',
                              alternatives = ['--with-pdf', '--with-pdf-manual'], arg='DOCDIR')

        opts.add_argumentless(help = 'Do not compress PDF manual\nDefault',
                              alternatives = ['--without-pdf-compression', '--without-pdf-manual-compression'])

        opts.add_argumented  (help = 'Select compression for PDF manual\nDefault = gz, xz is also recognised',
                              alternatives = ['--with-pdf-compression', '--with-pdf-manual-compression'], arg='COMPRESSION')

        opts.add_argumentless(help = 'Do not install info manual',
                              alternatives = ['--without-info', '--without-info-manual'])

        opts.add_argumented  (help = 'Set directory for info manual\nDefault = $SHARE/info',
                              alternatives = ['--with-info', '--with-info-manual'], arg='INFODIR')

        opts.add_argumentless(help = 'Do not use install-info when installing info manual',
                              alternatives = ['--without-info-install', '--without-info-manual-install'])

        opts.add_argumented  (help = 'Use install-info when installing info manual, and set description\nDefault',
                              alternatives = ['--with-info-install', '--with-info-manual-install'], arg='DESCRIPTION')

        opts.add_argumentless(help = 'Do not compress info manual',
                              alternatives = ['--without-info-compression', '--without-info-manual-compression'])

        opts.add_argumented  (help = 'Select compression for info manual\nDefault = gz, xz is also recognised',
                              alternatives = ['--with-info-compression', '--with-info-manual-compression'], arg='COMPRESSION')

        for man in manpages:
            opts.add_argumentless(help = 'Do not install %s manpage manual' % (man[1]),
                                  alternatives = ['--without-man-%s' % (man[0]), '--without-manpage-%s' % (man[0]), '--without-man-manual-%s' % (man[0]),
                                                  '--without-%s-man' % (man[0]), '--without-%s-manpage' % (man[0]), '--without-%s-man-manual' % (man[0])])

            opts.add_argumented  (help = 'Set directory for %s manpage\nDefault = $SHARE/man' % (man[1]),
                                  alternatives = ['--with-man-%s' % (man[0]), '--with-manpage-%s' % (man[0]), '--with-man-manual-%s' % (man[0]),
                                                  '--with-%s-man' % (man[0]), '--with-%s-manpage' % (man[0]), '--with-%s-man-manual' % (man[0])], arg='MANDIR')

        opts.add_argumentless(help = 'Do not install any manpages',
                              alternatives = ['--without-man', '--without-manpage', '--without-man-manual'])

        opts.add_argumented  (help = 'Set directory for all man pages\nDefault = $SHARE/man',
                              alternatives = ['--with-man', '--with-manpage', '--with-man-manual'], arg='MANDIR')

        for man in manpages:
            opts.add_argumentless(help = 'Do not compress %s manpage' % (man[1]),
                                  alternatives = ['--without-man-%s-compression' % (man[0]), '--without-manpage-%s-compression' % (man[0]), '--without-man-manual-%s-compression' % (man[0]),
                                                  '--without-%s-man-compression' % (man[0]), '--without-%s-manpage-compression' % (man[0]), '--without-%s-man-manual-compression' % (man[0])])

            opts.add_argumented  (help = 'Select compression for %s manpage\nDefault = gz, xz is also recognised' % (man[1]),
                                  alternatives = ['--with-man-%s-compression' % (man[0]), '--with-manpage-%s-compression' % (man[0]), '--with-man-manual-%s-compression' % (man[0]),
                                                  '--with-%s-man-compression' % (man[0]), '--with-%s-manpage-compression' % (man[0]), '--with-%s-man-manual-compression' % (man[0])],
                                  arg='COMPRESSION')

        opts.add_argumentless(help = 'Do not compress any installed manpage',
                              alternatives = ['--without-man-compression', '--without-manpage-compression', '--without-man-manual-compression'])

        opts.add_argumented  (help = 'Select compression for installed manpages\nDefault = gz, xz is also recognised',
                              alternatives = ['--with-man-compression', '--with-manpage-compression', '--with-man-manual-compression'], arg='COMPRESSION')

        for man in mansections:
            opts.add_argumented  (help = 'Change the section for the %s manpage\nDefault = %s' % man,
                                  alternatives = ['--man-section-%s' % (man[0]), '--%s-manpage-section' % (man[0]),
                                                  '--man-section-%s' % (man[0]), '--%s-manpage-section' % (man[0])], arg='SECTION')

        for dir in sharedirs:
            opts.add_argumentless(help = 'Do not install ' + dir[1],
                                  alternatives = ['--without-' + dir[0]])

            opts.add_argumentless(help = 'Install %s\nDefault' % dir[1],
                                  alternatives = [   '--with-' + dir[0]])

        opts.add_argumentless(help = 'Do not install UCS pony name map',
                              alternatives = ['--without-ucs', '--without-ucs-names'])

        opts.add_argumentless(help = 'Install UCS pony name map\nDefault',
                              alternatives = ['--with-ucs', '--with-ucs-names'])

        opts.add_argumentless(help = 'Let the installer set the env name for python in ponysay\nDefault',
                              alternatives = ['--without-custom-env-python'])

        opts.add_argumented  (help = 'Set the env name for python in ponysay',
                              alternatives = ['--with-custom-env-python'], arg='PYTHON')

        opts.add_argumented  (help = 'Set a prefix to all implicit directories\nDefault = /usr',
                              alternatives = ['--prefix'], arg='PREFIX')

        opts.add_argumentless(help = 'Change all implicit configurations to fit local user a installation for the current user',
                              alternatives = ['--private'])

        opts.add_argumentless(help = 'Change all implicit directories to fit installation to /opt',
                              alternatives = ['--opt'])

        opts.add_argumented  (help = 'Set the system\'s directory for command executables\nDefault = $PREFIX/bin',
                              alternatives = ['--bin-dir', '--bindir'], arg='BINDIR')

        opts.add_argumented  (alternatives = ['--sbin-dir', '--sbindir'], arg='SBINDIR')

        opts.add_argumented  (help = 'Set the system\'s directory for non-executable libraries\nDefault = $PREFIX/lib/ponysay\nNot used.',
                              alternatives = ['--lib-dir', '--libdir'], arg='LIBDIR')

        opts.add_argumented  (help = 'Set the system\'s directory for non-command executables\nDefault = $PREFIX/libexec/ponysay\nNot used.',
                              alternatives = ['--libexec-dir', '--libexecdir'], arg='LIBEXECDIR')

        opts.add_argumented  (help = 'Set the system\'s directory for resource files\nDefault = $PREFIX/share',
                              alternatives = ['--share-dir', '--sharedir'], arg='SHAREDIR')

        opts.add_argumented  (help = 'Set the system\'s local specific configuration directory\nDefault = /etc',
                              alternatives = ['--sysconf-dir', '--sysconfdir'], arg='SYSCONFDIR')

        opts.add_argumented  (help = 'Set the system\'s directory for cache directories\nDefault = /var/cache',
                              alternatives = ['--cache-dir', '--cachedir'], arg='CACHEDIR')

        opts.add_argumented  (help = 'Set off environment for installation\nEmpty by default',
                              alternatives = ['--dest-dir', '--destdir'], arg='DESTDIR')

        opts.add_argumented  (help = 'Set how to link identical files\nDefault = symbolic, copy and hard are also recognised',
                              alternatives = ['--linking'], arg='TYPE')

        opts.add_argumented  (help = 'Install all ponies or only the completely free ponies\nThis option is manditory, use strict, full, true or yes ' +
                                      'for only free ponies,\nand partial, sloppy, false or no for all ponies',
                              alternatives = ['--freedom'], arg='FREEDOM')

        opts.parse()

        self.linking = SYMBOLIC
        if opts.opts['--linking'] is not None:
            self.linking = opts.opts['--linking'][0]
        
        self.free = None
        if opts.opts['--freedom'] is not None:
            if opts.opts['--freedom'][0].lower() in ('strict', 'full', 'true', 'yes'):
                self.free = True
            elif opts.opts['--freedom'][0].lower() in ('partial', 'sloppy', 'false', 'no'):
                self.free = False
        def checkFreedom():
            if self.free is None:
                print()
                print('You need to select your freedom, add --freedom=strict or --freedom=partial.')
                print()
                print('--freedom=strict   will install only ponies that are completely free.')
                print('--freedom=partial  will install all ponies, even if they are not free.')
                print()
                print()
                exit(255)
        
        def setup_config():
            self.viewconf(conf)
            os.umask(0o022)
        
        if (opts.opts['---DESTDIR'] is not None) and (opts.opts['--dest-dir'] is None):
            destdir = opts.opts['---DESTDIR'][0]
            if len(destdir) > 0:
                opts.opts['--dest-dir'] = [destdir]

        if (opts.opts['---PREFIX'] is not None) and (opts.opts['--prefix'] is None):
            prefix = opts.opts['---PREFIX'][0]
            if len(prefix) > 0:
                opts.opts['--prefix'] = [prefix]
        
        if opts.opts['--help'] is not None:
            opts.help()
        elif opts.opts['--version'] is not None:
            print('Ponysay %s installer' % (PONYSAY_VERSION))
        elif len(opts.files) != 1:
            opts.print_fatal('A single command is expected on the command line.')
            opts.usage()
        else:
            method = opts.files[0]
            if   method == 'clean':      self.clean()
            elif method == 'clean-old':  self.cleanOld()
            else:
                conf = self.configure(opts.opts)

                if method == 'build':
                    checkFreedom()
                    setup_config()
                    self.build(conf)

                elif method == 'prebuilt':
                    checkFreedom()
                    setup_config()
                    self.applyDestDir(conf)
                    self.install(conf)

                elif method == 'install':
                    checkFreedom()
                    setup_config()
                    self.build(conf)
                    self.applyDestDir(conf)
                    self.install(conf)
                    self.clean()

                elif method == 'uninstall':
                    setup_config()
                    self.uninstall(conf)

                elif method == 'uninstall-old':
                    setup_config()
                    self.uninstallOld(conf)

                elif method == 'view':
                    setup_config()
                else:
                    opts.print_fatal('Unknown command: {}', method)
                    opts.usage()
    
    def viewconf(self, conf):
        '''
        Display configurations
        '''
        
        RED = '\033[31m%s\033[39m'
        GREEN = '%s\033[32m%s\033[39m'
        YELLOW = '\033[33m%s\033[39m'

        for command in commands:
            if conf[command] is not None:          print(GREEN  % ('Installing command ' + command + ' as ', conf[command]))
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
        for man in mansections:                    print(GREEN  % ('References to manpage for ' + man[0] + ' points to section ', conf['man-section-' + man[0]]))
        for dir in sharedirs:
            if conf[dir[0]] is not None:           print(GREEN  % ('Installing ' + dir[1] + ' to ', conf['share-dir'] + '/' + dir[0]))
            else:                                  print(RED    % ('Skipping installation of ' + dir[1]))
        for file in sharefiles:
            if conf[file[0]] is not None:          print(GREEN  % ('Installing ' + file[1] + ' as ', conf['share-dir'] + '/' + file[0]))
            else:                                  print(RED    % ('Skipping installation of ' + file[1]))
        if conf['custom-env-python'] is not None:  print(GREEN  % ('Using custom env reference in python script shebang: ', conf['custom-env-python']))
        else:                                      print(YELLOW % ('Looking for best env reference in python script shebang'))
        for miscfile in miscfiles:                 print(GREEN  % ('Installing ' + miscfile[0] + ' to ', conf[miscfile[0]]))
        print('Using system configuration directory: ' + conf['sysconf-dir'])
        print('Prefered linking style: ' + self.linking)
        print('Using umask: 022 (only owner can do modifications)')
        if self.free is None:                      print(YELLOW % ('\033[01m--freedom is manditory and has not be specified\033[21m'))
        elif self.free:                            print(GREEN  % ('', 'Installing only fully free parts of the package'))
        else:                                      print(RED    % ('Installing \033[1mnot\033[21m only fully free parts of the package'))

        print()
    
    def build(self, conf):
        '''
        Compile ponysay
        '''
        
        print('\033[1;34m::\033[39mCompiling...\033[21m')

        def compressCommand(ext):
            if ext == 'gz':  return 'gzip -9 -f'
            if ext == 'xz':  return 'xz -9e -f'

        def compress(source, destination, ext):
            print('%s < %s > %s' % (compressCommand(ext), source, destination))
            (fileout, filein) = (None, None)
            try:
                fileout = open(destination, 'w+')
                filein = open(source, 'r')
                Popen(compressCommand(ext).split(' '), stdout=fileout, stdin=filein).communicate()
            finally:
                if fileout is not None:  fileout.close()
                if filein  is not None:  filein .close()

        (fileout, filein) = (None, None)

        env = conf['custom-env-python']
        if env is None:
            try:
                (out, err) = Popen(['env', 'python', '--version'], stdout=PIPE, stderr=PIPE).communicate()
                out = out.decode('utf8', 'replace') + err.decode('utf8', 'replace')
                out = out.replace('\n', '')
                env = out.split(' ')[1].split('.')[0]
                if int(env) < 3:  env = 'python3'
                else:             env = 'python'
            except:
                env = 'python3'
        mane = False
        for command in commands:
            if conf[command] is not None:
                mane = True
                break
        if mane:
            for src in ponysaysrc:
                try:
                    fileout = open('src/%s.install' % src, 'wb+')
                    filein = open('src/%s' % src, 'rb')
                    data = filein.read().decode('utf-8', 'replace')

                    if '#!/usr/bin/env python3' in data:
                        data = data.replace('#!/usr/bin/env python3', '#!/usr/bin/env ' + env)
                    else:
                        data = data.replace('#!/usr/bin/env python', '#!/usr/bin/env ' + env)
                    data = data.replace('/usr/share/ponysay/', conf['share-dir'] + ('' if conf['share-dir'].endswith('/') else '/'))
                    data = data.replace('/etc/', conf['sysconf-dir'] + ('' if conf['sysconf-dir'].endswith('/') else '/'))
                    data = data.replace('\nVERSION = \'dev\'', '\nVERSION = \'%s\'' % (PONYSAY_VERSION))

                    fileout.write(data.encode('utf-8'))
                finally:
                    if fileout is not None:  fileout.close()
                    if filein  is not None:  filein .close()
            print('Creating uncompressed zip file ponysay.zip with files from src: ' + ' '.join(ponysaysrc))
            myzip = None
            try:
                myzip = ZipFile('ponysay.zip', 'w')
                for src in ponysaysrc:
                    myzip.write('src/%s.install' % src, src)
            finally:
                myzip.close()
            os.chmod('ponysay.zip', 0o755)
            try:
                fileout = open('ponysay.install', 'wb+')
                filein = open('ponysay.zip', 'rb')
                fileout.write(('#!/usr/bin/env %s\n' % env).encode('utf-8'))
                fileout.write(filein.read())
            finally:
                if fileout is not None:  fileout.close()
                if filein  is not None:  filein .close()

        for man in manpages:
            key = 'man-' + man[0]
            section = conf['man-section-ponysay']
            if man is manpages[0]:  lang = ''
            else:                   lang = '.' + man[0]
            if conf[key] is not None:
                src = 'manuals/manpage' + lang + '.6'
                dest = src + '.install'
                (fileout, filein) = (None, None)
                try:
                    fileout = open(dest, 'wb+')
                    filein = open(src, 'rb')
                    data = filein.read().decode('utf-8', 'replace')

                    data = data.replace('\n.TH PONYSAY 0', '\n.TH PONYSAY ' + conf['man-section-ponysay'])
                    for section in [item[0] for item in mansections]:
                        data = data.replace('\n.BR %s (0)' % (section), '\n.BR %s (%s)' % (section, conf['man-section-' + section]))

                    fileout.write(data.encode('utf-8'))
                finally:
                    if fileout is not None:  fileout.close()
                    if filein  is not None:  filein .close()
                src = dest
                ext = conf[key + '-compression']
                if ext is not None:
                    dest = 'manuals/manpage' + lang + '.6.' + ext
                    compress(src, dest, ext)

        if conf['info'] is not None:
            print('makeinfo manuals/ponysay.texinfo')
            os.system('makeinfo manuals/ponysay.texinfo')
            ext = conf['info-compression']
            if ext is not None:
                compress('ponysay.info', 'ponysay.info.' + ext, ext)

        if conf['pdf-compression'] is not None:
            ext = conf['pdf-compression']
            if ext is not None:
                compress('ponysay.pdf', 'ponysay.pdf.' + ext, ext)

        for command in commands:
            source = 'completion/ponysay'
            sourceed = 'completion/ponysay.%s' % (command)
            try:
                fileout = open(sourceed, 'wb+')
                filein = open(source, 'rb')
                data = filein.read().decode('utf-8', 'replace')

                if data.startswith('(ponysay\n'):
                    data = ('(%s ' % command) + data[len('(ponysay\n'):]
                elif data.startswith('(ponysay '):
                    data = ('(%s ' % command) + data[len('(ponysay '):]
                elif '\n(ponysay\n' in data:
                    edpos = data.find('\n(ponysay\n')
                    data = data[:edpos] + ('\n(%s\n' % command) + data[edpas + len('\n(ponysay\n'):]
                elif '\n(ponysay ' in data:
                    data = data[:edpos] + ('\n(%s ' % command) + data[edpas + len('\n(ponysay '):]
                else:
                    raise Exception('File %s does not look like expected' % source)

                fileout.write(data.encode('utf-8'))
            finally:
                if fileout is not None:  fileout.close()
                if filein  is not None:  filein .close()

        for shell in [item[0] for item in shells]:
            if conf[shell] is not None:
                for command in commands:
                    sourceed = 'completion/ponysay.%s' % (command)
                    generated = 'completion/%s-completion.%s' % (shell, command)
                    generatorcmd = './completion/auto-auto-complete.py %s --output %s --source %s' % (shell, generated, sourceed)
                    Popen(generatorcmd.split(' ')).communicate()
                    if conf[command] is not None:
                        dest = generated + '.install'
                        (fileout, filein) = (None, None)
                        try:
                            fileout = open(dest, 'wb+')
                            filein = open(generated, 'rb')
                            data = filein.read().decode('utf-8', 'replace')

                            data = data.replace('/usr/bin/ponysay', conf[command])
                            data = data.replace('/ponysay', '\0')
                            data = data.replace('ponysay', command)
                            data = data.replace('/usr/share/ponysay/', conf['share-dir'] if conf['share-dir'].endswith('/') else (conf['share-dir'] + '/'))
                            data = data.replace('\0', '/ponysay')

                            fileout.write(data.encode('utf-8'))
                        finally:
                            if fileout is not None:  fileout.close()
                            if filein  is not None:  filein .close()

        if conf['quotes'] is not None:
            self.removeLists([], ['quotes'])
            os.mkdir('quotes')
            ponymap = None
            try:
                ponymap = open('ponyquotes/ponies', 'rb')
                ponies = [line for line in ponymap.read().decode('utf-8', 'replace').split('\n')]
                for _ponies in ponies:
                    for pony in _ponies.split('+'):
                        if len(pony) > 0:
                            print('Generating quote files for \033[34m' + pony + '\033[39m')
                            for file in os.listdir('ponyquotes'):
                                if file.startswith(pony + '.'):
                                    if os.path.isfile('ponyquotes/' + file):
                                        shutil.copy('ponyquotes/' + file, 'quotes/' + _ponies + file[file.find('.'):])
            finally:
                if ponymap is not None:
                    ponymap.close()

        for (sharedir, hasponies) in [(sharedir[0], sharedir[3]) for sharedir in sharedirs]:
            if hasponies and os.path.isdir(sharedir):
                for toolcommand in ('--dimensions', '--metadata'):
                    if not self.free:
                        print('%s, %s, %s' % ('./src/ponysaytool.py', toolcommand, sharedir))
                        Popen(['./src/ponysaytool.py', toolcommand, sharedir], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
                    else:
                        params = ['./src/ponysaytool.py', toolcommand, sharedir, '--']
                        for sharefile in os.listdir(sharedir):
                            if sharefile.endswith('.pony') and (sharefile != '.pony'):
                                if not Setup.validateFreedom(sharedir + '/' + sharefile):
                                    print('Skipping metadata correction for %s/%s, did not pass validation process made by setup settings' % (sharedir, sharefile))
                                else:
                                    params.append(sharefile)
                        print('%s, %s, %s (with files)' % ('./src/ponysaytool.py', toolcommand, sharedir))
                        Popen(params, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()

        print()
    
    def install(self, conf):
        '''
        Install compiled ponysay
        '''
        
        print('\033[1;34m::\033[39mInstalling...\033[21m')

        dests = []
        for command in commands:
            if conf[command] is not None:
                dests.append(conf[command])
        if len(dests) > 0:
            self.cp(False, 'ponysay.install', dests)
            print('Setting mode for ponysay.install copies to 755')
            if self.linking == COPY:
                for dest in dests:
                    os.chmod(dest, 0o755)
            else:
                os.chmod(dests[0], 0o755)
        if conf['shared-cache'] is not None:
            dir = conf['shared-cache']
            if not os.path.exists(dir):
                pdir = dir[:dir.rfind('/') + 1]
                if not os.path.exists(pdir):
                    print('Creating intermediate-level directories needed for ' + dir)
                    os.makedirs(pdir)
                print('Creating directory ' + dir)
                os.mkdir(dir)
                print('Setting permission mode mask for ' + dir + ' to 7777')
                Popen('chmod -R 7777 -- \'' + dir.replace('\'', '\'\\\'\'') + '\'', shell=True).wait()
                print('Setting group for ' + dir + ' users')
                Popen('chown -R :users -- \'' + dir.replace('\'', '\'\\\'\'') + '\'', shell=True).wait()
        for shell in [item[0] for item in shells]:
            if conf[shell] is not None:
                for command in commands:
                    if conf[command] is not None:
                        src = 'completion/%s-completion.%s.install' % (shell, command)
                        dest = os.path.join(
                            os.path.dirname(conf[shell]),
                            os.path.basename(conf[shell]).replace('ponysay', command))
                        self.cp(False, src, [dest])
        if conf['pdf'] is not None:
            src = 'ponysay.pdf' + ('' if conf['pdf-compression'] is None else '.' + conf['pdf-compression'])
            dest = conf['pdf'] + '/' + src
            self.cp(False, src, [dest])
        if conf['info'] is not None:
            installinfo = []
            dests = []
            ext = ('' if conf['info-compression'] is None else '.' + conf['info-compression'])
            src = 'ponysay.info' + ext
            for command in commands:
                if conf[command] is not None:
                    dest = conf['info'] + '/' + command + '.info' + ext
                    dests.append(dest)
                    if conf['info-install'] is not None:
                        cmdarr = ['install-info', '--entry=Miscellaneous', '--description=' + conf['info-install'], '--dir-file=' + conf['info'] + '/dir', dest]
                        cmd = ' '.join(['\'%s\'' % (elem.replace('\'', '\'\\\'\'')) for elem in cmdarr])
                        installinfo.append((cmd, 'Installing info manual ' + dest + ' with install-info'))
            self.cp(False, src, dests)
            for pair in installinfo:
                print(pair[1])
                os.system(pair[0])
        for man in manpages:
            key = 'man-' + man[0]
            section = conf['man-section-ponysay']
            if man is manpages[0]:  sub = 'man' + section
            else:                   sub = man[0] + '/man' + section
            if man is manpages[0]:  lang = ''
            else:                   lang = '.' + man[0]
            if conf[key] is not None:
                src = 'manuals/manpage' + lang + '.6.' + ('install' if conf[key + '-compression'] is None else conf[key + '-compression'])
                dests = []
                for command in commands:
                    if conf[command] is not None:
                        dest = '%s/%s/%s.%s%s' % (conf[key], sub, command, section, '' if conf[key + '-compression'] is None else '.' + conf[key + '-compression'])
                        dests.append(dest)
                self.cp(False, src, dests)
        ponyshare = conf['share-dir']
        if not ponyshare.endswith('/'):
            ponyshare += '/'
        for dir in sharedirs:
            if conf[dir[0]] is not None:
                self.cp(True, dir[0], [ponyshare + dir[0]], Setup.validateFreedom if self.free else None)
        for file in sharefiles:
            if conf[file[0]] is not None:
                self.cp(False, 'share/' + file[1], [ponyshare + file[0]], Setup.validateFreedom if self.free else None)
        for file in miscfiles:
            self.cp(False, file[0], [conf[file[0]]], Setup.validateFreedom if self.free else None)
        print()
    
    def uninstall(self, conf):
        '''
        Uninstall ponysay
        '''
        
        print('\033[1;34m::\033[39mUninstalling...\033[21m')

        (files, dirs, infos) = ([], [], [])

        for command in commands:
            if conf[command] is not None:
                files.append(conf[command])
        if conf['shared-cache'] is not None:
            dirs.append(conf['shared-cache'])
        for shell in [item[0] for item in shells]:
            if conf[shell] is not None:
                for command in commands:
                    if conf[command] is not None:
                        files.append(conf[shell].replace('ponysay', command))
        if conf['pdf'] is not None:
            files.append(conf['pdf'] + '/ponysay.pdf' + ('' if conf['pdf-compression'] is None else '.' + conf['pdf-compression']))
        if conf['info'] is not None:
            for command in commands:
                if conf[command] is not None:
                    file = conf['info'] + '/' + command + '.info' + ('' if conf['info-compression'] is None else '.' + conf['info-compression'])
                    files.append(file)
                    if conf['info-install'] is not None:
                        infos.append(file)
        for man in [item[0] for item in manpages]:
            key = 'man-' + man
            section = conf['man-section-ponysay']
            if man is manpages[0]:  sub = 'man' + section
            else:                   sub = man[0] + '/man' + section
            if conf[key] is not None:
                for command in commands:
                    if conf[command] is not None:
                        files.append('%s/%s/%s.%s%s' % (conf[key], sub, command, section, '' if conf[key + '-compression'] is None else '.' + conf[key + '-compression']))
        ponyshare = conf['share-dir']
        if not ponyshare.endswith('/'):
            ponyshare += '/'
        for dir in sharedirs:
            if conf[dir[0]] is not None:
                dirs.append(ponyshare + dir[0])
        for file in sharefiles:
            if conf[file[0]] is not None:
                files.append(ponyshare + file[0])
        for file in miscfiles:
            files.append(conf[file[0]])

        for info in infos:
            cmdarr = ['install-info', '--delete', '--dir-file=' + conf['info'] + '/dir', info]
            cmd = ' '.join(['\'%s\'' % (elem.replace('\'', '\'\\\'\'')) for elem in cmdarr])
            print('Uninstalling info manual ' + info + ' with install-info')
            os.system(cmd)

        self.removeLists(files, dirs)
        print()
    
    def uninstallOld(self, conf):
        '''
        Uninstall file ponysay no longer uses
        '''
        
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
        print()
    
    def clean(self):
        '''
        Remove compiled files
        '''
        
        print('\033[1;34m::\033[39mCleaning...\033[21m')

        files = ['ponysay.info', 'ponysay.info.gz', 'ponysay.info.xz',  'ponysay.pdf.gz', 'ponysay.pdf.xz', 'ponysay.install', 'ponysay.zip']
        files += ['src/%s.install' % file for file in ponysaysrc]
        dirs = ['quotes']
        for comp in ['install', 'gz', 'xz']:
            for man in manpages:
                if man is manpages[0]:  man = ''
                else:                   man = '.' + man[0]
                for sec in range(0, 9):
                    files.append('manuals/manpage%s.%s.%s' % (man, str(sec), comp))
        for shell in [item[0] for item in shells]:
            for command in commands:
                files.append('completion/%s-completion.%s' % (shell, command))
                files.append('completion/%s-completion.%s.install' % (shell, command))
        for sharedir in [sharedir[0] for sharedir in sharedirs]:
            for dimfile in ('widths', 'heights', 'onlyheights'):
                files.append(sharedir + '/' + dimfile)

        self.removeLists(files, dirs)
        print()

    def cleanOld(self):
        '''
        Remove compiled files ponysay is no longer compiling
        '''
        
        print('\033[1;34m::\033[39mCleaning old files...\033[21m')

        files = ['truncater', 'ponysaytruncater', 'ponysay.py.install', 'ponysay.install~', 'ponysay.zip']
        dirs = []
        for shell in [item[0] for item in shells]:
            files.append('completion/%s-completion.%s.install' % (shell, 'sh' if shell == 'bash' else shell))
            files.append('completion/%s-completion-think.%s'   % (shell, 'sh' if shell == 'bash' else shell))
        for shell in [item[0] for item in shells]:
            for command in commands:
                files.append('completion/%s-completion.%s.%s' % (shell, 'sh' if shell == 'bash' else shell, command))

        self.removeLists(files, dirs)
        print()
    
    def removeLists(self, files, dirs):
        '''
        Removes listed files and directories
        '''
        
        for file in files:
            if os.path.isfile(file) or os.path.islink(file):
                print('Unlinking file %s' % (file))
                os.unlink(file)
                dir = file
                while True:
                    dir = dir[:dir.rfind('/')]
                    if ('/ponysay/' in (dir + '/')) and (len(os.listdir(dir)) == 0):
                        print('Removing newly empty directory %s' % (dir))
                        os.rmdir(dir)
                    else:
                        break;
        for dir in dirs:
            if os.path.isdir(dir) or os.path.islink(dir):
                print('Cascadingly removing directory %s' % (dir))
                if os.path.islink(dir):  os.unlink(dir)
                else:                    shutil.rmtree(dir)
                while True:
                    dir = dir[:dir.rfind('/')]
                    if ('/ponysay/' in (dir + '/')) and (len(os.listdir(dir)) == 0):
                        print('Removing newly empty directory %s' % (dir))
                        os.rmdir(dir)
                    else:
                        break;
    
    @staticmethod
    def validateFreedom(filename):
        '''
        Check whether a file is fully free
        '''
        
        if not os.path.isdir(filename):
            if filename.endswith('.pony') and (filename != '.pony') and not filename.endswith('/.pony'):
                with open(filename, 'rb') as file:
                    data = file.read().decode('utf8', 'replace')
                    if data.startswith('$$$\n') and ('\n$$$\n' in data) and not data.startswith('$$$\n$$$\n'):
                        data = data[4 : data.find('\n$$$\n')].split('\n')
                        for line in data:
                            if ':' not in line:
                                continue
                            line = [item.strip() for item in line.split(':')]
                            if (len(line) == 2) and (line[0] == 'FREE'):
                                return line[1].lower() == 'yes'
                return False
        return True
    
    def cp(self, recursive, source, destinations, validatehook = None):
        '''
        Copys a files or directory to multiple destinations
        '''
        
        if validatehook is not None:
            if not validatehook(source):
                print('Ignoring installation of file %s (did not pass validation process made by setup settings)' % source)
                return
        if os.path.islink(source) and (self.linking != COPY) and os.path.isdir(os.path.realpath(source)):
            target = os.readlink(source)
            for dest in destinations:
                print('Creating symbolic link %s with target directory %s' % (dest, target))
                if os.path.exists(dest):
                    self.removeLists([], [dest])
                self.symlink(target, dest)
        if os.path.islink(source) and (self.linking != COPY) and os.path.isfile(os.path.realpath(source)):
            target = os.readlink(source)
            if self.linking == HARD:
                for dest in destinations:
                    print('Creating hard link %s with target file %s' % (dest, target))
                    if os.path.exists(dest):
                        self.removeLists([], [dest])
                    mytarget = os.path.abspath(os.path.join(os.path.dirname(dest), target))
                    if os.path.exists(mytarget):
                        os.link(mytarget, dest)
                    else:
                        print('\033[31mTarget did not exists, using symlink instead\033[39m')
                        self.symlink(target, dest)
            else:
                for dest in destinations:
                    print('Creating symbolic link %s with target file %s' % (dest, target))
                    if os.path.exists(dest):
                        self.removeLists([], [dest])
                    self.symlink(target, dest)
        for dest in destinations:
            dir = dest[:dest.rfind('/') + 1]
            if not os.path.exists(dir):
                print('Making directory ' + dir + ' with parents')
                os.makedirs(dir)
        if recursive:
            target = destinations[0]
            for dest in destinations if self.linking == COPY else [target]:
                print('Copying directory %s to %s' % (source, dest))
                if not os.path.exists(dest):
                    os.mkdir(dest)
                links = []
                for file in os.listdir(source):
                    src = source + '/' + file
                    if os.path.exists(src) and os.path.islink(src):
                        links.append((os.path.isdir(src), src, [dest + '/' + file]))
                    else:
                        self.cp(os.path.isdir(src), src, [dest + '/' + file], validatehook)
                for link in links:
                    self.cp(link[0], link[1], link[2], validatehook)
            if self.linking != COPY:
                for dest in destinations[1:]:
                    print('Creating symbolic link %s with target directory %s' % (dest, target))
                    if os.path.exists(dest):
                        self.removeLists([], [dest])
                    self.symlink(target, dest)
        else:
            target = destinations[0]
            for dest in destinations if self.linking == COPY else [target]:
                print('Copying file %s to %s' % (source, dest))
                shutil.copyfile(source, dest)
            if self.linking == HARD:
                for dest in destinations[1:]:
                    print('Creating hard link %s with target file %s' % (dest, target))
                    if os.path.exists(dest):
                        os.unlink(dest)
                    os.link(target, dest)
            elif self.linking == SYMBOLIC:
                for dest in destinations[1:]:
                    print('Creating symbolic link %s with target file %s' % (dest, target))
                    if os.path.exists(dest):
                        os.unlink(dest)
                    self.symlink(target, dest)
    
    def symlink(self, target, dest):
        '''
        Create a symlink with a relative path
        '''
        
        if target.startswith('./') or target.startswith('../'):
            os.symlink(target, dest)
        elif '/' not in target:
            try:
                os.symlink('./' + target, dest)
            except OSError as e:
                if e.errno != 17:
                    raise
        else:
            targets = target.split('/')
            dests = dest.split('/')

            while (len(targets) > 1) and (len(dests) > 1) and (targets[0] == dests[0]):
                targets = targets[1:]
                dests = dests[1:]

            if (len(dests) == 1):
                targets = ['.'] + targets
            else:
                targets = (['..'] * (len(dests) - 1)) + targets

            os.symlink('/'.join(targets), dest)

    def configure(self, opts):
        '''
        Parses configurations
        '''
        
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
        conf['custom-env-python'] = 'python3'
        for sharedir in sharedirs:
            conf[sharedir[0]] = True
        for sharefile in sharefiles:
            conf[sharefile[0]] = True
        for miscfile in miscfiles:
            conf[miscfile[0]] = miscfile[1]
        conf['sysconf-dir'] = '/etc'
        conf['bin-dir'] = '/usr/bin'
        conf['lib-dir'] = '/usr/lib/ponysay'
        conf['libexec-dir'] = '/usr/libexec/ponysay'
        conf['share-dir'] = '/usr/share'

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
            if opts['--bin-dir']           is None:  opts['--bin-dir']           = ['/opt/ponysay']
            if opts['--lib-dir']           is None:  opts['--lib-dir']           = ['/opt/ponysay']
            if opts['--libexec-dir']       is None:  opts['--libexec-dir']       = ['/opt/ponysay']
            if opts['--share-dir']         is None:  opts['--share-dir']         = ['/opt/ponysay']
            if opts['--with-shared-cache'] is None:  opts['--with-shared-cache'] = ['/var/opt/ponysay/cache']

        for dir in ['bin', 'lib', 'libexec', 'share']:
            key = dir + '-dir'
            if opts['--' + key] is not None:
                conf[key] = opts['--' + key][0]
            if (dir == 'share') and (opts['--opt'] is None):
                conf[key] += '/ponysay'
            if conf[key].startswith('usr/'):
                conf[key] = prefix + conf[key][3:]
        if opts['--cache-dir'] is not None:
            dir = opts['--cache-dir'][0]
            for key in conf:
                if conf[key] not in (None, False, True):
                    if conf[key].startswith('/var/cache'):
                        conf[key] = dir + conf[key][10:]

        if opts['--sysconf-dir'] is not None:
            conf['sysconf-dir'] = opts['--sysconf-dir'][0]

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
            for key in ['info'] + [item[0] for item in shells]:
                conf[key] = None
            for sharedir in sharedirs:
                if sharedir is not sharedirs[0]:
                    conf[sharedir[0]] = None
            for sharefile in sharefiles:
                conf[sharefile[0]] = None

        if opts['--nothing'] is not None:
            for command in commands:
                conf[command] = None
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
            if '--with-' + key not in opts:
                continue
            if opts['--with-' + key] is not None:
                if defaults[key] in (False, True):
                    conf[key] = True
                else:
                    conf[key] = defaults[key] if opts['--with-' + key][0] is None else opts['--with-' + key][0]
            if opts['--without-' + key] is not None:
                conf[key] = False if defaults[key] in (False, True) else None

        for mansection in mansections:
            if opts['--man-section-' + mansection[0]] is not None:
                conf['man-section-' + mansection[0]] = opts['--man-section-' + mansection[0]][0]
            else:
                conf['man-section-' + mansection[0]] = mansection[1]

        self.destDir = None if opts['--dest-dir'] is None else opts['--dest-dir'][0]

        return conf

    def applyDestDir(self, conf):
        if self.destDir is not None:
            for key in conf:
                if conf[key] not in (None, False, True):
                    if conf[key].startswith('/'):
                        conf[key] = self.destDir + conf[key]

    def unapplyDestDir(self, conf):
        if self.destDir is not None:
            for key in conf:
                if conf[key] not in (None, False, True):
                    if conf[key].startswith(self.destDir):
                        conf[key] = conf[key][len(self.destDir):]


ARGUMENTLESS = 0
ARGUMENTED = 1

class ArgParser():
    '''
    Simple argument parser, a strip down of the one in ponysay and slitly modified
    '''
    
    def __init__(self, program, description, usage, longdescription = None):
        '''
        Constructor.
        The short description is printed on same line as the program name
        '''
        
        self.__program = program
        self.__description = description
        self.__usage = usage
        self.__longdescription = longdescription
        self.__arguments = []
        (self.opts, self.optmap) = ({}, {})

    def add_argumentless(self, alternatives, help = None):
        '''
        Add option that takes no arguments
        '''
        
        ARGUMENTLESS
        self.__arguments.append((ARGUMENTLESS, alternatives, None, help))
        (stdalt, self.opts[stdalt]) = (alternatives[0], None)
        for alt in alternatives:  self.optmap[alt] = (stdalt, ARGUMENTLESS)

    def add_argumented(self, alternatives, arg, help = None):
        '''
        Add option that takes one argument
        '''
        
        self.__arguments.append((ARGUMENTED, alternatives, arg, help))
        (stdalt, self.opts[stdalt]) = (alternatives[0], None)
        for alt in alternatives:  self.optmap[alt] = (stdalt, ARGUMENTED)

    def parse(self, argv = sys.argv):
        '''
        Parse arguments
        '''
        
        self.argcount = len(argv) - 1
        self.files = []
        (argqueue, optqueue, get) = ([], [], False)

        for arg in argv[1:]:
            if get:
                get = False
                if (arg is argv[-1]) or ((len(arg) > 2) and (arg[:2] in ('--', '++'))):
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
                        self.print_fatal('Unrecognized option {}. Use --help or consult the manual.', arg)
                        exit(-1)
                elif (arg in self.optmap) and (self.optmap[arg][1] == ARGUMENTED):
                    optqueue.append(arg)
                    get = True
                else:
                    self.print_fatal('Unrecognized option {}. Use --help or consult the manual.', arg)
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
                self.opts[opt] = [arg]
            else:
                self.print_fatal('duplicate option {}', arg)
                exit(-1)
    
    def print_fatal(self, message, *args):
        sys.stderr.write('{}: fatal: {}\n'.format(self.__program, message.format(*args)))
    
    def usage(self):
        '''
        Print a short usage message.
        '''
        
        if self.__longdescription is not None:
            print(self.__longdescription)
            print()
        print('\n\033[1mUSAGE:\033[21m', end='')
        first = True
        for line in self.__usage.split('\n'):
            if first:  first = False
            else:      print('    or', end='')
            print('\t{}'.format(line))
        
        print()
    
    def help(self):
        '''
        Prints a colourful help message.
        '''
        
        # The usage should be terse so this header is only included in the help command.
        print('\033[1m{}\033[21m - {}\n'.format(self.__program, self.__description))
        
        self.usage()
        
        print('\033[1mCONFIGURATIONS:\033[21m\n')
        for opt in self.__arguments:
            (opt_type, opt_alts, opt_arg, opt_help) = opt[0:4]
            if opt_help is not None:
                for opt_alt in opt_alts:
                    if opt_alt is opt_alts[-1]:
                        print('\t%s=\033[4m%s\033[24m' % (opt_alt, opt_arg) if opt_type == ARGUMENTED else '\t' + opt_alt)
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
