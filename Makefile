install:
	mkdir -p $(DESTDIR)/usr/share/ponies
	cp -r ponies/*.pony $(DESTDIR)/usr/share/ponies/
	install -Dm755 ponysay $(DESTDIR)/usr/bin/ponysay
	ln -s ponysay $(DESTDIR)/usr/bin/ponythink
