#!/usr/bin/env bash

# USAGE:  dev/dist.sh ttyponies
#     or  dev/dist.sh pdfmanual
#     or  dev/dist.sh tag VERSION [OTHER OPTIONS FOR `git tag`]
#     or  dev/dist.sh beigepdf
#     or  dev/dist.sh remaster


ttyponies()
{
    defaultinparams="--left - --right - --top - --bottom -"
    defaultoutparams="--colourful y --left - --right - --top - --bottom - --balloon n --fullcolour y"
    for x in '' 'extra'; do
	mkdir -p "${x}ttyponies"
	for pony in $(find "${x}ponies/" | grep -v '/\.' | grep '\.pony$' | sed -e "s_^${x}ponies/__"); do
	    echo "building ${x}ttypony: $pony"
	    if [ ! -L "${x}ponies/$pony" ]; then
		ponytool --import ponysay --file "${x}ponies/$pony" $defaultinparams \
		         --export ponysay --platform linux --file "${x}ttyponies/$pony" $defaultoutparams
		git add "${x}ttyponies/$pony"
	    else
		ln -sf "$(readlink "${x}ponies/$pony")" "${x}ttyponies/$pony"
		git add "${x}ttyponies/$pony"
	    fi
	done
    done
}


remaster()
{
    inparams="--left - --right - --top - --bottom -"
    xtermoutparams="--left - --right - --top - --bottom - --balloon n"
    linuxoutparams="--colourful y --left - --right - --top - --bottom - --balloon n --fullcolour y"
    for x in '' 'extra'; do
	mkdir -p "${x}ttyponies"
	for pony in $(find "${x}ponies/" | grep -v '/\.' | grep '\.pony$' | sed -e "s_^${x}ponies/__"); do
	    echo "remastering ${x}pony: $pony"
	    if [ ! -L "${x}ponies/$pony" ]; then
		ponytool --import ponysay --file "${x}ponies/$pony" $inparams \
		         --export ponysay --file "${x}ponies/$pony" $xtermoutparams \
		         --export ponysay --platform linux --file "${x}ttyponies/$pony" $linuxoutparams
		git add "${x}ponies/$pony" "${x}ttyponies/$pony"
	    else
		ln -sf "$(readlink "${x}ponies/$pony")" "${x}ttyponies/$pony"
		git add "${x}ttyponies/$pony"
	    fi
	done
    done
}


pdfmanual()
{
    texi2pdf "manuals/ponysay.texinfo"
    for ext in `echo aux cp cps fn ky log pg toc tp vr op ops pgs vrs bak`; do
	if [ -f "ponysay.$ext" ]; then
	    unlink "ponysay.$ext"
	fi
    done
    if [ -d "ponysay.t2d" ]; then
	rm -r "ponysay.t2d";
    fi
    git add "manuals/ponysay.texinfo" "ponysay.pdf"
}


beigepdf()
{
    pdfjam --pagecolor 249,246,240 -o "ponysay+beige.pdf" "ponysay.pdf"
}


pdf()
{
    pdfmanual "$@"
}


tag()
{
    echo 'Testing executability'
    ./src/__main__.py -l >/dev/null || exit 1
    ./src/__main__.py -L >/dev/null || exit 1
    ./src/__main__.py +l >/dev/null || exit 1
    ./src/__main__.py +L >/dev/null || exit 1
    ./src/__main__.py -A >/dev/null || exit 1
    ./src/__main__.py +A >/dev/null || exit 1
    ./src/__main__.py -B >/dev/null || exit 1
    ./src/__main__.py -of pinkie >/dev/null || exit 1
    ./src/__main__.py -o +f faust >/dev/null || exit 1
    ./src/__main__.py -o -F faust >/dev/null || exit 1
    echo test | ./src/__main__.py -f pinkie >/dev/null || exit 1
    echo 'No error was thrown'
    
    ./dev/tests/test-everything || exit $?
    
    version=`./setup.py version`
    if [ "$version" = 'Ponysay '"$1"' installer' ]; then
	git tag -s "$@" && git checkout "$1" && git push --tags -u origin "$1"
    else
	echo 'Setup script reports. '"$version"
	echo 'This is not consistent with desired tag version: '"$1"
	echo 'Make sure the version is correct in setup.py and that all change logs are up to date'
    fi
}


[ "$0" = './dist.sh' ] && cd ..
"$@"

