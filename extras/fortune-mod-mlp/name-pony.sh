#!/bin/sh

file="$1/$2.pony"
pony="$2"
name=""

case "${pony}" in # Exceptions not supported by the name extraction below
    (carrot)        name="Carrot";;
    (chrysalis)     name="Chrysalis";;
    (lemonhearts)   name="Lemon Hearts";;
    (lily)          name="Lily Valley";;
    (snowflake)     name="Snowflake";;
    (twinkleshine)  name="Twinkleshine";;
    (rumble)        name="Rumble";;
esac

if [ -n "${name}" ]; then
    echo "${name}"
    exit 0
fi

name="$(cat "$file" | grep '^NAME: ' | sed -e 's/^NAME: //g')"
name="$(echo $(echo "$name" | grep -o '[^,(]*' | head -n 1))"

full_name="$(cat "$file" | grep '^OTHER NAMES: ' | sed -e 's/^OTHER NAMES: /, /g')"
full_name="$(echo $(echo "$full_name" | grep -o ', [^,(]* (official, full name[a-z]*)' | grep -o ' [^,(]*' | head -n 1))"

if test -n "${full_name}"; then
    echo "${full_name}"
else
    echo "${name}"
fi

