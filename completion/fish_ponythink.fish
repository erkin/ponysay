
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

complete -c ponythink -s h --description "Help of ponythink"
complete -c ponythink -s v --description "Version of ponythink"
complete -c ponythink -s l --description "List pony files"
complete -c ponythink -s f -a "$systemponies $homeponies" --description "Select a pony, either a filename or pony name"
complete -c ponythink -s W -a "Integer" --description "The screen column where the message should be wrapped"

set -e systemponies
set -e homeponies

