#!/usr/bin/env bash

# USAGE:  dev/dist.sh ttyponies
#     or  dev/dist.sh pdfmanual
#     or  dev/dist.sh tag VERSION [OTHER OPTIONS FOR `git tag`]
#     or  dev/dist.sh beigepdf
#     or  dev/dist.sh remaster


ttyponies()
{
    defaultoutparams=--colourful y --left - --right - --top - --bottom - --balloon n --fullcolour y
    for x in '' 'extra'; do
	mkdir -p "${x}ttyponies"
	for pony in $(find "${x}ponies/" | grep -v '/\.' | grep '\.pony$' | sed -e "s_^${x}ponies/__"); do
	    echo "building ${x}ttypony: $pony"
	    if [ ! -L "${x}ponies/$pony" ]; then
		ponytool --import ponysay --file "${x}ponies/$pony" \
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
    defaultoutparams=--colourful y --left - --right - --top - --bottom - --balloon n --fullcolour y
    for x in '' 'extra'; do
	mkdir -p "${x}ttyponies"
	for pony in $(find "${x}ponies/" | grep -v '/\.' | grep '\.pony$' | sed -e "s_^${x}ponies/__"); do
	    echo "remastering ${x}pony: $pony"
	    if [ ! -L "${x}ponies/$pony" ]; then
		ponytool --import ponysay --file "${x}ponies/$pony" \
		         --export ponysay --file "${x}ponies/$pony" $defaultoutparams \
		         --export ponysay --platform linux --file "${x}ttyponies/$pony" $defaultoutparams
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
    version=`./setup.py version`
    if [ "$version" = 'Ponysay '"$1"' installer' ]; then
	git tag -a "$@" && git checkout "$1" && git push -u origin "$1"
    else
	echo 'Setup script reports. '"$version"
	echo 'This is not consistent with desired tag version: '"$1"
	echo 'Make sure the version is correct in setup.py and that all change logs are up to date'
    fi
}


[ "$1" = './dist.sh' ] && cd ..
"$@"

