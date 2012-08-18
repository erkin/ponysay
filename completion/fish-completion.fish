# Completions for ponysay
# https://github.com/erkin/ponysay/
#
# Author: Elis Axelsson <etu AT elis DOT nu>


set -g ponies  ('/usr/bin/ponysay.pl' --onelist)
set -g quoters ('/usr/bin/ponysay.pl' --quoters)


complete -c ponysay -s h --description "Help of ponysay"
complete -c ponysay -s v --description "Version of ponysay"
complete -c ponysay -s l --description "List pony files"
complete -c ponysay -s L --description "List pony files with alternatives"
complete -c ponysay -s f -a "$ponies" --description "Select a pony"
complete -c ponysay -s q -a "$quoters" --description "Select ponies for MLP:FiM quotes"
complete -c ponysay -s W -a "Integer" --description "The screen column where the message should be wrapped"


set -e ponies
set -e quoters

