#!/usr/bin/env bash


# KMS ponies extension
kmscmd=""
[ "$TERM" = "linux" ] && kmscmd=$(for c in $(echo $PATH":" | sed -e 's/:/\/ponysay2kmsponysay /g'); do if [ -f $c ]; then echo $c; break; fi done)
[ ! "$kmscmd" = "" ] && TERM="-linux-"


# Function for printing the ponies and the message
say() {
	# KMS ponies support
	if [ "$kmscmd" = "" ]; then
		function runcmd {
			cowcmd -f "$pony" "$@"
		}
	else
		function runcmd {
			cowcmd -f <($kmscmd "$pony") "$@"
		}
	fi

}
