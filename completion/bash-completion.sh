#!/usr/bin/env bash

_ponysay()
{
  local cur prev
  cur=${COMP_WORDS[COMP_CWORD]}
  prev=${COMP_WORDS[COMP_CWORD-1]}

  declare -ga _ponysay_ponies _ponysay_balloons _ponythink_balloons
  [[ 0 < "${#_ponysay_ponies}" ]] || _ponysay_ponies=( $(ponysay -p list) )
  [[ 0 < "${#_ponysay_balloons}" ]] || _ponysay_balloons=( $(ponysay -b list) )
  [[ 0 < "${#_ponythink_balloons}" ]] || _ponythink_balloons=( $(ponythink -b list) )

  if [[ "$cur" = -* ]]
  then COMPREPLY=( $( compgen -W "-h --help --pony -p --quote -q --center -c --center-text -C --width -w --balloon -b" -- "$cur" ) )
	return 0
  fi

  if [[ "$prev" =~ -[^-]*p$ || "$prev" = "--pony" ]]
  then COMPREPLY=( $( compgen -W "${_ponysay_ponies[*]}" -- "$cur" ) )
	return 0
  fi

  if [[ "$prev" =~ -[^-]*b$ || "$prev" = "--balloon" ]]
  then
	if [[ "$COMP_LINE" == ponythink* ]]
	then COMPREPLY=( $( compgen -W "${_ponythink_balloons[*]}" -- "$cur" ) )
	else COMPREPLY=( $( compgen -W "${_ponysay_balloons[*]}" -- "$cur" ) )
	fi
	return 0
  fi
}

complete -F _ponysay -o default ponysay
complete -F _ponysay -o default ponythink
