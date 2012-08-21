# bash completion for ponysay            -*- shell-script -*-

_ponysay()
{
    local cur prev words cword
    _init_completion -n = || return
    
    options='--version --help --list --altlist --pony --wrap --quote --balloonlist --balloon'
    COMPREPLY=( $( compgen -W "$options" -- "$cur" ) )
    
    if [ $prev = "-f" ] || [ $prev = "--pony" ]; then
	ponies=$('/usr/bin/ponysay' --onelist)
	COMPREPLY=( $( compgen -W "$ponies" -- "$cur" ) )

    elif [ $prev = "-q" ] || [ $prev = "--quote" ]; then
	quoters=$('/usr/bin/ponysay' --quoters)
	COMPREPLY=( $( compgen -W "$quoters" -- "$cur" ) )

    elif [ $prev = "-b" ] || [ $prev = "--balloon" ]; then
        balloons=$('/usr/bin/ponysay' --balloonlist)
	COMPREPLY=( $( compgen -W "$balloons" -- "$cur" ) )

    elif [ $prev = "-W" ] || [ $prev = "--wrap" ]; then
	cols=$(( `stty size | cut -d ' ' -f 2` - 10 ))
	COMPREPLY=( $cols  $(( $cols / 2 ))  100  60 )

    fi
}

complete -o default -F _ponysay ponysay

