# bash completion for ponysay            -*- shell-script -*-

_ponysay()
{
    local cur prev words cword
    _init_completion -n = || return
    
    options='-v -h -l -f -W -q'
    COMPREPLY=( $( compgen -W "$options" -- "$cur" ) )
    
    if [ $prev = "-f" ]; then
	ponies=$('/usr/bin/ponysay.py' --onelist)
	COMPREPLY=( $( compgen -W "$ponies" -- "$cur" ) )

    elif [ $prev = "-q" ]; then
	quoters=$('/usr/bin/ponysay.py' --quoters)
	COMPREPLY=( $( compgen -W "$quoters" -- "$cur" ) )

    elif [ $prev = "-W" ]; then
	cols=$(( `stty size | cut -d ' ' -f 2` - 10 ))
	COMPREPLY=( $cols  $(( $cols / 2 ))  100  60 )

    fi
}

complete -o default -F _ponysay ponysay

