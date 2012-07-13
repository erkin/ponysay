all: ponysaytruncater

ponysaytruncater:
	gcc -o "ponysaytruncater" "ponysaytruncater.c"

install: all
	mkdir -p "$(DESTDIR)/usr/share/ponysay/"
	mkdir -p "$(DESTDIR)/usr/share/ponysay/ponies"
	mkdir -p "$(DESTDIR)/usr/share/ponysay/ttyponies"
	cp ponies/*.pony "$(DESTDIR)/usr/share/ponysay/ponies/"
	cp ttyponies/*.pony "$(DESTDIR)/usr/share/ponysay/ttyponies/"

	mkdir -p "$(DESTDIR)/usr/bin/"
	install "ponysay" "$(DESTDIR)/usr/bin/ponysay"
	install -s "ponysaytruncater" "$(DESTDIR)/usr/bin/ponysaytruncater"
	ln -sf "ponysay" "$(DESTDIR)/usr/bin/ponythink"

	mkdir -p "$(DESTDIR)/usr/share/zsh/site-functions/"
	install "completion/zsh-completion.zsh" "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay"

	mkdir -p "$(DESTDIR)/usr/share/bash-completion/completions/"
	install "completion/bash-completion.sh" "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"

	mkdir -p "$(DESTDIR)/usr/share/licenses/ponysay/"
	install "COPYING" "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"

	mkdir -p "$(DESTDIR)/usr/share/man/man1"
	install "manpage.1" "$(DESTDIR)/usr/share/man/man1/ponysay.1"
	ln -sf "ponysay.1" "$(DESTDIR)/usr/share/man/man1/ponythink.1"

	mkdir -p "$(DESTDIR)/usr/share/man/es/man1"
	install "manpage.es.1" "$(DESTDIR)/usr/share/man/es/man1/ponysay.6"
	ln -sf "ponysay.6" "$(DESTDIR)/usr/share/man/es/man1/ponythink.6"

uninstall:
	rm -fr "$(DESTDIR)/usr/share/ponysay/ponies"
	rm -fr "$(DESTDIR)/usr/share/ponysay/ttyponies"
	unlink "$(DESTDIR)/usr/bin/ponysay"
	unlink "$(DESTDIR)/usr/bin/ponysaytruncater"
	unlink "$(DESTDIR)/usr/bin/ponythink"
	unlink "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay";
	unlink "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"
	unlink "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"
	unlink "$(DESTDIR)/usr/share/man/man1/ponysay.1"
	unlink "$(DESTDIR)/usr/share/man/man1/ponythink.1"
	unlink "$(DESTDIR)/usr/share/man/es/man1/ponysay.6"
	unlink "$(DESTDIR)/usr/share/man/es/man1/ponythink.6"
clean:
	rm -r "ponysaytruncater"
