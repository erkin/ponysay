#!/usr/bin/env bash

# USAGE:  dev/dist.sh ttyponies
#     or  dev/dist.sh pdfmanual
#     or  dev/dist.sh tag VERSION [OTHER OPTIONS FOR `git tag`]


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
	if [ -f "ponysay.$ext" ]; then
	    unlink "ponysay.$ext"
	fi
    done
    if [ -d "ponysay.t2d" ]; then
	rm -r "ponysay.t2d";
    fi
}


pdf()
{
    pdfmanual "$@"
}


tag()
{
    version=`./setup.py version`
    if [ "version" = 'Ponysay '"$1"' installer' ]; then
	git tag -a "$@" && git checkout "$1" && git push -u origin "$1"
    else
	echo 'Setup script reports. '"$version"
	echo 'This is not consistent with desired tag version: '"$1"
	echo 'Make sure the version is correct in setup.py and that all change logs are up to date'
    fi
}


[ "$1" = './dist.sh' ] && cd ..
"$@"
