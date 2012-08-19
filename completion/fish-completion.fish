# FISH completions for ponysay
# https://github.com/erkin/ponysay/
#
# Author: Elis Axelsson <etu AT elis DOT nu>

set -g ponies  ('/usr/bin/ponysay.py' --onelist)
set -g quoters ('/usr/bin/ponysay.py' --quoters)


complete -c ponysay -s h -l help                  --description "help of ponysay"
complete -c ponysay -s v -l version               --description "version of ponysay"
complete -c ponysay -s l -l list                  --description "list pony files"
complete -c ponysay -s L -l altlist               --description "list pony files with alternatives"
complete -c ponysay -s f -l pony    -a "$ponies"  --description "select a pony"
complete -c ponysay -s q -l quote   -a "$quoters" --description "select a pony which will quote herself"
complete -c ponysay -s W -l wrap    -a "Integer"  --description "specify the column when the message should be wrapped"


set -e ponies
set -e quoters

