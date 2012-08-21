#compdef ponysay
_shortopts=(
    '-v[Show version and exit]'
    '-h[Show this help and exit]'
    '-l[list pony names]'
    '-L[list pony names with alternatives]'
    '-B[list balloon style names]'
    '-f[Select a pony (either a file name or a pony name]: :_path_files -W '/usr/share/ponysay/ponies' -g "*(\:r)"'
    '-q[Select ponies for MLP:FiM quotes]'
    '-b[Selecy a balloon style]'
    '-W[The screen column where the message should be wrapped]'
    )
_arguments -s : \
    "$_shortopts[@]"

