# bash completion for ponysay            -*- shell-script -*-

_ponysay()
{
    local cur prev words cword
    _init_completion -n = || return
    
    COMPREPLY=( $( compgen -W '-v -h -l -f -W' -- "$cur" ) )
    
    if [[ $prev = "-f" ]]; then
	COMPREPLY=()
	
	sysponies=/usr/share/ponysay/ponies/
	usrponies=~/.ponies/
	if [[ $TERM = "linux" ]]; then
	    sysponies=/usr/share/ponysay/ttyponies/
	    usrponies=~/.ttyponies/
	fi
	
	if [[ -d $sysponies ]]; then
	    COMPREPLY+=( $( compgen -W "$(ls --color=no $sysponies | sed -e 's/.pony//g')" -- "$cur" ) )
	fi
	if [[ -d $usrponies ]]; then
	    COMPREPLY+=( $( compgen -W "$(ls --color=no $usrponies | sed -e 's/.pony//g')" -- "$cur" ) )
	fi
    elif [[ $prev = "-W" ]]; then
	cols=$( echo `tput cols` - 10 | bc )
	COMPREPLY=( $cols   $( echo $cols / 2 | bc )  100  60 )
    fi
}

complete -o default -F _ponysay ponysay

