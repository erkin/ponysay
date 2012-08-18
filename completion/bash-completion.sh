# bash completion for ponysay            -*- shell-script -*-

_ponysay()
{
    local cur prev words cword
    _init_completion -n = || return
    
    options='-v -h -l -f -W -q'
    COMPREPLY=( $( compgen -W "$options" -- "$cur" ) )
    
    if [ $prev = "-f"  ]; then
	COMPREPLY=()
	
	sysponies=/usr/share/ponysay/ponies/
	usrponies=~/.local/share/ponysay/ponies/
	if [[ $TERM = "linux" ]]; then
	    sysponies=/usr/share/ponysay/ttyponies/
	    usrponies=~/.local/share/ponysay/ttyponies/
	fi
	
	[ -d $sysponies ] &&  COMPREPLY+=( $( compgen -W "$(ls --color=no $sysponies | sed -e 's/.pony//g')" -- "$cur" ) )
	[ -d $usrponies ] &&  COMPREPLY+=( $( compgen -W "$(ls --color=no $usrponies | sed -e 's/.pony//g')" -- "$cur" ) )

    elif [ $prev = "-W" ]; then
	cols=$(( `stty size | cut -d ' ' -f 2` - 10 ))
	COMPREPLY=( $cols  $(( $cols / 2 ))  100  60 )

    elif [ $prev = "-q" ]; then
	qcmd=/usr/lib/ponysay/pq4ps
	quoters=$($qcmd -l)
	COMPREPLY=( $( compgen -W "$quoters" -- "$cur" ) )

    fi
}

complete -o default -F _ponysay ponysay

