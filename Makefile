
PREFIX?=/usr/local

install: genponies
	install -m 0755 ponysay.py $(PREFIX)/bin
	ln -s $(PREFIX)/bin/ponysay.py $(PREFIX)/bin/ponysay
	ln -s $(PREFIX)/bin/ponysay.py $(PREFIX)/bin/ponythink
	install -m 0755 -d $(PREFIX)/share/ponysay
	install -m 0755 -t $(PREFIX)/share/ponysay quotes/*
	install -m 0755 -t $(PREFIX)/share/ponysay genponies/*
	install -m 0755 -d $(PREFIX)/share/doc/ponysay
	install -m 0755 -t $(PREFIX)/share/doc/ponysay COPYING
	install -m 0755 -t $(PREFIX)/share/doc/ponysay README.md
	install -m 0644 completion/zsh-completion.sh /usr/share/zsh/site-functions/_ponysay
	install -m 0755 completion/bash-completion.sh /etc/bash_completion.d/ponysay.sh

uninstall:
	rm $(PREFIX)/bin/ponysay
	rm $(PREFIX)/bin/ponythink
	rm $(PREFIX)/bin/ponysay.py
	rm $(PREFIX)/share/ponysay/*
	rmdir $(PREFIX)/share/ponysay
	rm $(PREFIX)/share/doc/ponysay/*
	rmdir $(PREFIX)/share/doc/ponysay
	rm /usr/share/zsh/site-functions/_ponysay
	rm /etc/bash_completion.d/ponysay.sh

reinstall: uninstall install

genpngs:
	mkdir genpngs
	unpixelterm -d genpngs ponies/*.pony

genponies:
	mkdir genponies
	pixelterm -d genponies pngs/*.png

