
PREFIX?=/usr

install:
	install -m 0755 ponysay.py $(PREFIX)/bin
	ln -s $(PREFIX)/bin/ponysay.py $(PREFIX)/bin/ponysay
	ln -s $(PREFIX)/bin/ponysay.py $(PREFIX)/bin/ponythink
	install -m 0755 -d $(PREFIX)/share/ponysay
	install -m 0755 -t $(PREFIX)/share/ponysay ponies/*
	install -m 0755 -d $(PREFIX)/share/doc/ponysay
	install -m 0755 -t $(PREFIX)/share/doc/ponysay COPYING
	install -m 0755 -t $(PREFIX)/share/doc/ponysay README.md

uninstall:
	rm $(PREFIX)/bin/ponysay
	rm $(PREFIX)/bin/ponythink
	rm $(PREFIX)/bin/ponysay.py
	rm $(PREFIX)/share/ponysay/*
	rmdir $(PREFIX)/share/ponysay
	rm $(PREFIX)/share/doc/ponysay/*
	rmdir $(PREFIX)/share/doc/ponysay

