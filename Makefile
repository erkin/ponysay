install:
	gcc -o "ponysaytruncater" "ponysaytruncater.c"
	mkdir -p "$(DESTDIR)/usr/share/ponies"
	mkdir -p "$(DESTDIR)/usr/share/ttyponies"
	cp -r "ponies/*.pony" "$(DESTDIR)/usr/share/ponies/"
	cp -r "ttyponies/*.pony" "$(DESTDIR)/usr/share/ttyponies/"
	install "ponysay" "$(DESTDIR)/usr/bin/ponysay"
	install -s "ponysaytruncater" "$(DESTDIR)/usr/bin/ponysaytruncater"
	ln -sf "ponysay" "$(DESTDIR)/usr/bin/ponythink"

uninstall:
	rm -fr "$(DESTDIR)/usr/share/ponies"
	rm -fr "$(DESTDIR)/usr/share/ttyponies"
	unlink "$(DESTDIR)/usr/bin/ponysay"
	unlink "$(DESTDIR)/usr/bin/ponysaytruncater"
	unlink "$(DESTDIR)/usr/bin/ponythink"
