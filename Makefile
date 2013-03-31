
prefix=/usr

install:
	install -m 0755 ponysay.py $(prefix)/bin
	ln -s $(prefix)/bin/ponysay.py $(prefix)/bin/ponysay
	ln -s $(prefix)/bin/ponysay.py $(prefix)/bin/ponythink
	install -m 0755 -d $(prefix)/share/ponysay
	install -m 0755 -t $(prefix)/share/ponysay ponies/*
	install -m 0755 -d $(prefix)/share/doc/ponysay
	install -m 0755 -t $(prefix)/share/doc/ponysay COPYING
	install -m 0755 -t $(prefix)/share/doc/ponysay README.md

uninstall:
	rm $(prefix)/bin/ponysay
	rm $(prefix)/bin/ponythink
	rm $(prefix)/bin/ponysay.py
	rm $(prefix)/share/ponysay/*
	rmdir $(prefix)/share/ponysay
	rm $(prefix)/share/doc/ponysay/*
	rmdir $(prefix)/share/doc/ponysay

