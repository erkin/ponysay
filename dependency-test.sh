#!/bin/sh

br=0
bs=0
bo=0
rr=0
ro=0

(hash make         2>/dev/null) || (br=1 ; echo 'Missing make, install make [build required]')
(hash sed          2>/dev/null) || (br=1 ; echo 'Missing sed, install sed [build required]')
(hash install      2>/dev/null) || (br=1 ; echo 'Missing install, install coreutils [build required]')
(hash unlink       2>/dev/null) || (br=1 ; echo 'Missing uninstall, install coreutils [build required]')
(hash rm           2>/dev/null) || (br=1 ; echo 'Missing rm, install coreutils [build required]')
(hash ln           2>/dev/null) || (br=1 ; echo 'Missing ln, install coreutils [build required]')
(hash mkdir        2>/dev/null) || (br=1 ; echo 'Missing mkdir, install coreutils [build required]')
(hash cp           2>/dev/null) || (br=1 ; echo 'Missing cp, install coreutils [build required]')
(hash cut          2>/dev/null) || (br=1 ; echo 'Missing cut, install coreutils [build required]')

(hash bash         2>/dev/null) || (bs=1 ; echo 'Missing bash, install bash [build recommended]')

(hash gzip         2>/dev/null) || (bo=1 ; echo 'Missing gzip, install gzip [build optional]')
(hash makeinfo     2>/dev/null) || (bo=1 ; echo 'Missing makeinfo, install texinfo [build optional]')
(hash install-info 2>/dev/null) || (bo=1 ; echo 'Missing install-info, install info [build optional]')

(hash stty         2>/dev/null) || (rr=1 ; echo 'Missing stty, install coreutils [runtime required]')
(hash python       2>/dev/null) || (rr=1 ; echo 'Missing python, install python>=3 [runtime required]')

(hash cut 2>/dev/null) && (hash python 2>/dev/null) &&
    (test ! $(env python --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1) = 3) && (
	(hash python3 2>/dev/null) ||
	    (rr=1 ; echo 'Missing python>=3, install python (may be named python3) [runtime required]'))

(hash tty2colourfultty   2>/dev/null) || (ro=1 ; echo 'Missing tty2colourfultty, install util-say [runtime optional]')
(hash ponysay2ttyponysay 2>/dev/null) || (ro=1 ; echo 'Missing ponysay2ttyponysay, install util-say [runtime optional]')

( (test $br = 1) || (test $rr = 1) || (test $ro = 1) ) && echo

(test $br = 1) && echo 'You will not be able to build and install ponysay.'
(test $rr = 1) && echo 'You will not be able to run ponysay.'
(test $br = 1) && (test $rr = 0) && echo 'Unable to verify version of python.'

(test $br = 0) && (test $bs = 0) && (test $bo = 0) && (test $rr = 0) && (test $ro = 0) &&
    echo && echo 'Everything appears to be in order, enjoy ponysay!'

echo
