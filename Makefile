all: ponysaytruncater

ponysaytruncater:
	gcc -o "ponysaytruncater" "ponysaytruncater.c"

ttyponies:
	mkdir -p ttyponies
	./ttyponies.sh

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

	mkdir -p "$(DESTDIR)/usr/share/man/man6"
	install "manuals/manpage.6" "$(DESTDIR)/usr/share/man/man6/ponysay.6"
	ln -sf "ponysay.6" "$(DESTDIR)/usr/share/man/man6/ponythink.6"

	mkdir -p "$(DESTDIR)/usr/share/man/es/man6"
	install "manuals/manpage.es.6" "$(DESTDIR)/usr/share/man/es/man6/ponysay.6"
	ln -sf "ponysay.6" "$(DESTDIR)/usr/share/man/es/man6/ponythink.6"

uninstall:
	rm -fr "$(DESTDIR)/usr/share/ponysay/ponies"
	rm -fr "$(DESTDIR)/usr/share/ponysay/ttyponies"
	unlink "$(DESTDIR)/usr/bin/ponysay"
	unlink "$(DESTDIR)/usr/bin/ponysaytruncater"
	unlink "$(DESTDIR)/usr/bin/ponythink"
	unlink "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay";
	unlink "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"
	unlink "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"
	unlink "$(DESTDIR)/usr/share/man/man6/ponysay.6"
	unlink "$(DESTDIR)/usr/share/man/man6/ponythink.6"
	unlink "$(DESTDIR)/usr/share/man/es/man6/ponysay.6"
	unlink "$(DESTDIR)/usr/share/man/es/man6/ponythink.6"
clean:
	rm -f "ponysaytruncater"
