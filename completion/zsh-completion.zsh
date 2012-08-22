#compdef ponysay
_shortopts=(
    '-v[Show version and exit]'
    '-h[Show this help and exit]'
    '-l[list pony names]'
    '-L[list pony names with alternatives]'
    '+l[list extra pony names]'
    '+L[list extra pony names with alternatives]'
    '-B[list balloon style names]'
    '-f[Select a pony (either a file name or a pony name)]: :_path_files -W '/usr/share/ponysay/ponies' -g "*(\:r)"'
    '-F[Select a extra pony]: :_path_files -W '/usr/share/ponysay/extraponies' -g "*(\:r)"'
    '-q[Select ponies for MLP:FiM quotes]'
    '-b[Selecy a balloon style]'
    '-W[The screen column where the message should be wrapped]'
    )
_arguments -s : \
    "$_shortopts[@]"

