#!/usr/bin/env bash


scrw=`(stty size <&2 || echo 0 0) | cut -d ' ' -f 2` # Screen width
scrh=`(stty size <&2 || echo 0 0) | cut -d ' ' -f 1` # Screen height

# KMS ponies extension
kmscmd=""
[ "$TERM" = "linux" ] && kmscmd=$(for c in $(echo $PATH":" | sed -e 's/:/\/ponysay2kmsponysay /g'); do if [ -f $c ]; then echo $c; break; fi done)
[ ! "$kmscmd" = "" ] && TERM="-linux-"


# Function for printing the ponies and the message
say() {
	# Set PONYSAY_SHELL_LINES to default if not specified
	[ "$PONYSAY_SHELL_LINES" = "" ] && PONYSAY_SHELL_LINES=2
	
	# Height trunction, show top
	function htrunchead {
		head --lines=$(( $scrh - $PONYSAY_SHELL_LINES ))
	}
	
	# Height trunction, show bottom
	function htrunctail {
		tail --lines=$(( $scrh - $PONYSAY_SHELL_LINES ))
	}
	
	# Simplification of customisation of cowsay
	if [ $customcmd = 0 ]; then
		function cowcmd {
			pcmd='#!/usr/bin/perl\nuse utf8;'
			ccmd=$(for c in $(echo $PATH":" | sed -e 's/:/\/'"$cmd"' /g'); do if [ -f $c ]; then echo $c; break; fi done)
			
			if [ ${0} == *ponythink ]; then
				cat <(echo -e $pcmd) $ccmd > "/tmp/ponythink"
				perl '/tmp/ponythink' "$@"
				rm '/tmp/ponythink'
			else
				perl <(cat <(echo -e $pcmd) $ccmd) "$@"
			fi
		}
	else
		function cowcmd	{
			$cmd "$@"
		}
	fi

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

	# Print the pony and the message
	if [ "$TERM" = "linux" ] || [ "$PONYSAY_TRUNCATE_HEIGHT" = 'yes' ] || [ "$PONYSAY_TRUNCATE_HEIGHT" = 'y' ] || [ "$PONYSAY_TRUNCATE_HEIGHT" = '1' ]; then
		if [ "$PONYSAY_BOTTOM" = 'yes' ] || [ "$PONYSAY_BOTTOM" = 'y' ] || [ "$PONYSAY_BOTTOM" = '1' ]; then
		        runcmd "${wrap:+-W$wrap}" | wtrunc | htrunctail
		else
		        runcmd "${wrap:+-W$wrap}" | wtrunc | htrunchead
		fi
	else
		runcmd "${wrap:+-W$wrap}" | wtrunc
	fi
}

# Check for cowsay
hash $cmd &>/dev/null; if [ $? -ne 0 ]; then
	cat >&2 <<EOF
You don't seem to have the $cmd program.
Please install it in order to use this wrapper.

Alternatively, symlink it to '$cmd' in anywhere in \$PATH
if it actually exists under a different filename.
EOF
	exit 1
fi
