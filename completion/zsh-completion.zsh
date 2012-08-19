#compdef ponysay
_shortopts=(
    '-v[Show version and exit]'
    '-h[Show this help and exit]'
    '-l[list ponyfiles]'
    '-L[list ponyfiles with alternatives]'
    '-f[Select a pony (either a filename or a ponyname]: :_path_files -W '/usr/share/ponysay/ponies' -g "*(\:r)"'
    '-q[Select ponies for MLP:FiM quotes]'
    '-W[The screen column where the message should be wrapped]'
    )
_arguments -s : \
    "$_shortopts[@]"

