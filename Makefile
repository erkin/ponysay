all: ponysaytruncater

ponysaytruncater:
	gcc -o "ponysaytruncater" "ponysaytruncater.c"

install: all
	mkdir -p "$(DESTDIR)/usr/share/ponies"
	mkdir -p "$(DESTDIR)/usr/share/ttyponies"
	cp ponies/*.pony "$(DESTDIR)/usr/share/ponies/"
	cp ttyponies/*.pony "$(DESTDIR)/usr/share/ttyponies/"

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

uninstall:
	rm -fr "$(DESTDIR)/usr/share/ponies"
	rm -fr "$(DESTDIR)/usr/share/ttyponies"
	unlink "$(DESTDIR)/usr/bin/ponysay"
	unlink "$(DESTDIR)/usr/bin/ponysaytruncater"
	unlink "$(DESTDIR)/usr/bin/ponythink"
	unlink "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay";
	unlink "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"
	unlink "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"

clean:
	rm -r "ponysaytruncater"
