install:
	mkdir -p $(DESTDIR)/usr/share/ponies
	cp -r ponies/*.pony $(DESTDIR)/usr/share/ponies/
	cp -r ttyponies/*.pony $(DESTDIR)/usr/share/ttyponies/
	install -Dm755 ponysay $(DESTDIR)/usr/bin/ponysay
	ln -sf ponysay $(DESTDIR)/usr/bin/ponythink

uninstall:
	rm -fr $(DESTDIR)/usr/share/ponies
#	cp -r ponies/*.pony $(DESTDIR)/usr/share/ponies/
	rm -fr $(DESTDIR)/usr/share/ttyponies
#	cp -r ttyponies/*.pony $(DESTDIR)/usr/share/ttyponies/
	rm -f $(DESTDIR)/usr/bin/ponysay
	unlink $(DESTDIR)/usr/bin/ponythink
