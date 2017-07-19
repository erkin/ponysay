#!/usr/bin/env sh

# Compatible with  bash  dash  zsh   mksh  ksh    ksh93
# but not with     fish  powershell
# problematic with tcsh  csh
#
# Therefor to ensure it work always this shebang to standard POSIX shell


br=0 # build required
bs=0 # build recommended
bo=0 # build optional
rr=0 # runtime required
ro=0 # runtime optional
pv=0 # python version


(hash chmod        2>/dev/null) || (br=1 ; ro=1 ; echo 'Missing chmod, install coreutils [build+runtime required]')

(hash gzip         2>/dev/null) || (bo=1 ;        echo 'Missing gzip, install gzip [build optional]')
(hash makeinfo     2>/dev/null) || (bo=1 ;        echo 'Missing makeinfo, install texinfo [build optional]')
(hash install-info 2>/dev/null) || (bo=1 ;        echo 'Missing install-info, install info [build optional]')

(hash python       2>/dev/null) || (br=1 ; rr=1 ; echo 'Missing python, install python>=3 [build+runtime required]')

(hash cut 2>/dev/null) && (hash python 2>/dev/null) &&
    (test ! $(env python --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1) = 3) && (
        (hash python3 2>/dev/null) ||
            (br=1 ; rr=1 ; pv=1 ;                 echo 'Missing python>=3, install python (may be named python3) [build+runtime required]'))

(hash stty         2>/dev/null) || (rr=1 ;        echo 'Missing stty, install coreutils [runtime required]')

(hash ponytool     2>/dev/null) || (ro=1 ;        echo 'Missing ponytool, install util-say [runtime optional]')
(hash chmod        2>/dev/null) || (rr=1 ;        echo 'Missing chmod, install coreutils [runtime optional]')

( (test $br = 1) || (test $rr = 1) || (test $ro = 1) || (test $pv = 1) ) && echo

(test $br = 1) && echo 'You will not be able to build and install ponysay.'
(test $rr = 1) && echo 'You will not be able to run ponysay.'
(test $pv = 1) && echo 'Unable to verify version of python.'

(test $br = 0) && (test $bs = 0) && (test $bo = 0) && (test $rr = 0) && (test $ro = 0) &&
    echo && echo 'Everything appears to be in order, enjoy ponysay!'

echo

