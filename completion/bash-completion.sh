# bash completion for ponysay            -*- shell-script -*-

_ponysay()
{
    local cur prev words cword
    _init_completion -n = || return
    
    options="--version --help --list --altlist --pony --wrap --quote --balloonlist --balloon --file ++file ++pony ++list ++altlist --all ++all"
    options="$options --256-colours --tty-colours --kms-colours"
    COMPREPLY=( $( compgen -W "$options" -- "$cur" ) )
    
    if [ $prev = "-f" ] || [ $prev = "--pony" ] || [ $prev = "--file" ]; then
	ponies=$('/usr/bin/ponysay' --onelist)
	COMPREPLY=( $( compgen -W "$ponies" -- "$cur" ) )

    elif [ $prev = "+f" ] || [ $prev = "++pony" ] || [ $prev = "++file" ]; then
	extraponies=$('/usr/bin/ponysay' ++onelist)
	COMPREPLY=( $( compgen -W "$extraponies" -- "$cur" ) )

    elif [ $prev = "-q" ] || [ $prev = "--quote" ]; then
	quoters=$('/usr/bin/ponysay' --quoters)
	COMPREPLY=( $( compgen -W "$quoters" -- "$cur" ) )

    elif [ $prev = "-b" ] || [ $prev = "--balloon" ] || [ $prev = "--bubble" ]; then
        balloons=$('/usr/bin/ponysay' --balloonlist)
	COMPREPLY=( $( compgen -W "$balloons" -- "$cur" ) )

    elif [ $prev = "-W" ] || [ $prev = "--wrap" ]; then
	cols=$(( `stty size | cut -d ' ' -f 2` - 10 ))
	COMPREPLY=( $cols  $(( $cols / 2 ))  100  60  none  inherit )

    fi
}

complete -o default -F _ponysay ponysay

