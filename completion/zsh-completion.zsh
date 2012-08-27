#compdef ponysay ponythink
_opts=(
    '(--version -v)'{-v,--version}'[Show version and exit]'
    '(-h --help)'{-h,--help}'[Show this help and exit]'
    '(-l --list)'{-l,--list}'[list pony names]'
    '(-L --altlist)'{-L,--altlist}'[list pony names with alternatives]'
    '(+l ++list)'{+l,++list}'[list extra pony names]'
    '(+L ++altlist)'{+L,++altlist}'[list extra pony names with alternatives]'
    '(-B --balloonlist)'{-B,--balloonlist}'[list balloon style names]'
    '(-b --ballon)'{-b,--balloon}'[Selecy a balloon style]: :_path_files -W '/usr/share/ponysay/balloons' -g "*(\:r)"'
    '(-c --compact)'{-c,--compat}'[Compress messages.]'
    '(-W --wrap)'{-W,--wrap}'[The screen column where the message should be wrapped]'
    )
_tty_select=(
    '(-q --quite)'{-q,--quote}'[Select ponies for MLP:FiM quotes]: :_path_files -W '/usr/share/ponysay/ttyponies' -g "*(\:r)"'
    '(-f --pony)'{-f,--pony}'[select pony]: :_path_files -W '/usr/share/ponysay/ttyponies/' -g "*(\:r)"'
    '(-F ++pony)'{-F,++pony}'[Select a extra pony]: :_path_files -W '/usr/share/ponysay/extrattyponies' -g "*(\:r)"'
    )
_select=(
    '(-q --quite)'{-q,--quote}'[Select ponies for MLP:FiM quotes]: :_path_files -W '/usr/share/ponysay/ponies' -g "*(\:r)"'
    '(-f --pony)'{-f,--pony}'[select pony]: :_path_files -W '/usr/share/ponysay/ponies/' -g "*(\:r)"'
    '(-F ++pony)'{-F,++pony}'[Select a extra pony]: :_path_files -W '/usr/share/ponysay/extraponies' -g "*(\:r)"'
    )
if [[ "${(f)"$(tty)"##*/}" == "tty*" ]]; then
    _arguments \
        "$_opts[@]" \
        "$_tty_select[@]"
else
    _arguments \
        "$_opts[@]" \
        "$_select[@]"
fi
