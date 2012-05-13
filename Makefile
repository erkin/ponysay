install:
	gcc -o "ponysaytruncater" "ponysaytruncater.c"
	mkdir -p "$(DESTDIR)/usr/share/ponies"
	mkdir -p "$(DESTDIR)/usr/share/ttyponies"
	cp -r ponies/*.pony "$(DESTDIR)/usr/share/ponies/"
	cp -r ttyponies/*.pony "$(DESTDIR)/usr/share/ttyponies/"
	install -D "ponysay" "$(DESTDIR)/usr/bin/ponysay"
	install -s "ponysaytruncater" "$(DESTDIR)/usr/bin/ponysaytruncater"
	ln -sf "ponysay" "$(DESTDIR)/usr/bin/ponythink"
	if [ -d "$(DESTDIR)/usr/share/zsh/site-functions/" ]; then install "completion/zsh-completion.zsh" "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay"; fi
	mkdir -p "$(DESTDIR)/usr/share/bash-completion/completions/"
	install -D "COPYING" "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"
	mkdir -p "$(DESTDIR)/usr/share/bash-completion/completions/"
	install "completion/bash-completion.sh" "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"

uninstall:
	rm -fr "$(DESTDIR)/usr/share/ponies"
	rm -fr "$(DESTDIR)/usr/share/ttyponies"
	unlink "$(DESTDIR)/usr/bin/ponysay"
	unlink "$(DESTDIR)/usr/bin/ponysaytruncater"
	unlink "$(DESTDIR)/usr/bin/ponythink"
	if [ -e "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay" ]; then unlink "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay"; fi
	unlink "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"
	unlink "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"

clean:
	rm -r ponysaytruncater
