#!/usr/bin/env bash


ttyponies()
{
    mkdir -p "ttyponies"
    for pony in $(ls --color=no "ponies/"); do
	if [ ! "$pony" = '.info' ]; then
	    echo "building ttypony: $pony"
	    if [ "`readlink "ponies/$pony"`" = '' ]; then
	        ponysay2ttyponysay < "ponies/$pony" | tty2colourfultty -c 1 > "ttyponies/$pony"
	        git add "ttyponies/$pony"
	    else
		ln -sf `readlink "ponies/$pony"` "ttyponies/$pony"
		git add "ttyponies/$pony"
	    fi
	fi
    done
    mkdir -p "extrattyponies"
    for pony in $(ls --color=no "extraponies/"); do
	if [ ! "$pony" = '.info' ]; then
	    echo "building extrattypony: $pony"
	    if [ "`readlink "extraponies/$pony"`" = '' ]; then
	        ponysay2ttyponysay < "extraponies/$pony" | tty2colourfultty -c 1 > "extrattyponies/$pony"
	        git add "extrattyponies/$pony"
	    else
                ln -sf `readlink "extraponies/$pony"` "extrattyponies/$pony"
		git add "extrattyponies/$pony"
	    fi
	fi
    done
}


pdfmanual()
{
	texi2pdf "manuals/ponysay.texinfo"
	git add  "manuals/ponysay.texinfo" "ponysay.pdf"
	for ext in `echo aux cp cps fn ky log pg toc tp vr`; do
	    if [ -f "ponysay.\$\$ext" ]; then
		unlink "ponysay.$ext"
	    fi
	done
	if [ -d "ponysay.t2d" ]; then
	    rm -r "ponysay.t2d";
	fi
}


[ "$1" = './dist.sh' ] && cd ..
"$@"
