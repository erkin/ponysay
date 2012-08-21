# FISH completions for ponysay
# https://github.com/erkin/ponysay/
#
# Author: Elis Axelsson <etu AT elis DOT nu>

set -g ponies  ('/usr/bin/ponysay' --onelist)
set -g quoters ('/usr/bin/ponysay' --quoters)
set -g balloons ('/usr/bin/ponysay' --balloonlist)


complete --command ponysay --short-option h --long-option help                                      --description 'help of ponysay'
complete --command ponysay --short-option v --long-option version                                   --description 'version of ponysay'
complete --command ponysay --short-option l --long-option list                                      --description 'list pony names'
complete --command ponysay --short-option L --long-option altlist                                   --description 'list pony names with alternatives'
complete --command ponysay --short-option B --long-option balloonlist                               --description 'list balloon style names'
complete --command ponysay --short-option f --long-option pony    --arguments "$ponies"             --description 'pony'
complete --command ponysay --short-option q --long-option quote   --arguments "$quoters" --no-files --description 'pony'
complete --command ponysay --short-option b --long-option balloon --arguments "$balloons"           --description 'balloon style'
complete --command ponysay --short-option W --long-option wrap    --arguments 'Integer'             --description 'specify the column when the message should be wrapped'
complete --command ponysay                                        --arguments 'MESSAGE'

set -e ponies
set -e quoters
set -e balloons
