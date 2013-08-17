!#/usr/bin/env bash

en="en_GB-ise-w_accents"

info()
{
    if [ -f "./manuals/ponysay.texinfo" ]; then
	aspell --lang="$en" check "./manuals/ponysay.texinfo"
        git add "./manuals/ponysay.texinfo"
    elif [ -f "../manuals/ponysay.texinfo" ]; then
	aspell --lang="$en" check "../manuals/ponysay.texinfo"
        git add "../manuals/ponysay.texinfo"
    else
	echo "spell.sh: unable to find document: ponysay.texinfo" >&2
	exit -1
    fi
}


man()
{
    lang="$1"
    langarg="$1"
    if [ ! "$lang" = "" ]; then
	lang=".$lang"
    else
	langarg="$en"
    fi
    
    if [ -f "./manuals/manpage${lang}.0" ]; then
	aspell --lang="${langarg}" check "./manuals/manpage${lang}.0"
	git add "./manuals/manpage${lang}.0"
    elif [ -f "../manuals/manpage${lang}.0" ]; then
	aspell --lang="${langarg}" check "../manuals/manpage${lang}.0"
	git add "../manuals/manpage${lang}.0"
    else
	echo "spell.sh: unable to find document: manpage${lang}.0" >&2
	exit -1
    fi
}


"$@"
