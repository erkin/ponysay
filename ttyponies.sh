#!/bin/bash

for pony in $(ls ponies/); do
    echo "building ttypony: $pony"
    if [[ `readlink "ponies/$pony"` = '' ]]; then
	ponysay2ttyponysay < "ponies/$pony" | unzebra -e | tty2colourfultty -c 1 -e > "ttyponies/$pony"
    elif [[ ! -f "ttyponies/$pony" ]]; then
	ln -s `readlink "ponies/$pony"` "ttyponies/$pony"
    fi
done

