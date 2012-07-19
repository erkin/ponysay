
# Completions for ponysay & ponythink
# https://github.com/erkin/ponysay/
#
# Author: Elis Axelsson <etu AT elis DOT nu>


if test -d /usr/share/ponysay/ponies/
	set -g systemponies (ls --color=no /usr/share/ponysay/ponies/ | sed 's/\.pony/\t Pony from \/usr\/share\/ponysay\/ponies\//')
end

if test -d ~/.local/share/ponysay/ponies/
	set -g homeponies (ls --color=no ~/.local/share/ponysay/ponies/ | sed 's/\.pony/\t Pony from ~\/.local\/share\/ponysay\/ponies\//')
end

complete -c ponysay -s h --description "Help of ponysay"
complete -c ponysay -s v --description "Version of ponysay"
complete -c ponysay -s l --description "List pony files"
complete -c ponysay -s f -a "$systemponies $homeponies" --description "Select a pony, either a filename or pony name"
complete -c ponysay -s W -a "Integer" --description "The screen column where the message should be wrapped"

set -e systemponies
set -e homeponies

