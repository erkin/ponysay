all: ponysaytruncater manpages infomanual ponythinkcompletion


ponysaytruncater:
	gcc -o "ponysaytruncater" "ponysaytruncater.c"


manpages:
	gzip -9 < "manuals/manpage.6" > "manuals/manpage.6.gz"
	gzip -9 < "manuals/manpage.es.6" > "manuals/manpage.es.6.gz"


infomanual:
	makeinfo "manuals/ponysay.texinfo"
	gzip -9 "ponysay.info"


ponythinkcompletion:
	sed -e 's/ponysay/ponythink/g' <"completion/bash-completion.sh"   | sed -e 's/\/ponythink\//\/ponysay\//g' -e 's/\\\/ponythink\\\//\\\/ponysay\\\//g' >"completion/bash-completion-think.sh"
	sed -e 's/ponysay/ponythink/g' <"completion/fish-completion.fish" | sed -e 's/\/ponythink\//\/ponysay\//g' -e 's/\\\/ponythink\\\//\\\/ponysay\\\//g' >"completion/fish-completion-think.fish"
	sed -e 's/ponysay/ponythink/g' <"completion/zsh-completion.zsh"   | sed -e 's/\/ponythink\//\/ponysay\//g' -e 's/\\\/ponythink\\\//\\\/ponysay\\\//g' >"completion/zsh-completion-think.zsh"


ttyponies:
	mkdir -p ttyponies
	for pony in $$(ls --color=no ponies/); do                                                      \
	    echo "building ttypony: $$pony"                                                           ;\
	    if [[ `readlink "ponies/$$pony"` = "" ]]; then                                             \
	        ponysay2ttyponysay < "ponies/$$pony" | tty2colourfultty -c 1 -e > "ttyponies/$$pony"  ;\
	    elif [[ ! -f "ttyponies/$$pony" ]]; then                                                   \
	        ln -s `readlink "ponies/$$pony"` "ttyponies/$$pony"                                   ;\
	    fi                                                                                         \
	done


pdfmanual:
	texi2pdf "manuals/ponysay.texinfo"
	if [[ -f "ponysay.aux" ]]; then unlink "ponysay.aux"; fi
	if [[ -f "ponysay.cp"  ]]; then unlink "ponysay.cp" ; fi
	if [[ -f "ponysay.cps" ]]; then unlink "ponysay.cps"; fi
	if [[ -f "ponysay.fn"  ]]; then unlink "ponysay.fn" ; fi
	if [[ -f "ponysay.ky"  ]]; then unlink "ponysay.ky" ; fi
	if [[ -f "ponysay.log" ]]; then unlink "ponysay.log"; fi
	if [[ -f "ponysay.pg"  ]]; then unlink "ponysay.pg" ; fi
	if [[ -f "ponysay.toc" ]]; then unlink "ponysay.toc"; fi
	if [[ -f "ponysay.tp"  ]]; then unlink "ponysay.tp" ; fi
	if [[ -f "ponysay.vr"  ]]; then unlink "ponysay.vr" ; fi


install:
	mkdir -p "$(DESTDIR)/usr/share/ponysay/"
	mkdir -p "$(DESTDIR)/usr/share/ponysay/ponies"
	mkdir -p "$(DESTDIR)/usr/share/ponysay/ttyponies"
	cp -P ponies/*.pony "$(DESTDIR)/usr/share/ponysay/ponies/"
	cp -P ttyponies/*.pony "$(DESTDIR)/usr/share/ponysay/ttyponies/"

	mkdir -p "$(DESTDIR)/usr/bin/"
	install "ponysay" "$(DESTDIR)/usr/bin/ponysay"
	ln -sf "ponysay" "$(DESTDIR)/usr/bin/ponythink"

	mkdir -p "$(DESTDIR)/usr/lib/ponysay/"
	install -s "ponysaytruncater" "$(DESTDIR)/usr/lib/ponysay/truncater"
	install "ponysaylist.pl" "$(DESTDIR)/usr/lib/ponysay/list.pl"

	mkdir -p "$(DESTDIR)/usr/share/bash-completion/completions/"
	install "completion/bash-completion.sh" "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"
	install "completion/bash-completion-think.sh" "$(DESTDIR)/usr/share/bash-completion/completions/ponythink"

	mkdir -p "$(DESTDIR)/usr/share/fish/completions/"
	install "completion/fish-completion.fish" "$(DESTDIR)/usr/share/fish/completions/ponysay.fish"
	install "completion/fish-completion-think.fish" "$(DESTDIR)/usr/share/fish/completions/ponythink.fish"

	mkdir -p "$(DESTDIR)/usr/share/zsh/site-functions/"
	install "completion/zsh-completion.zsh" "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay"
	install "completion/zsh-completion-think.zsh" "$(DESTDIR)/usr/share/zsh/site-functions/_ponythink"

	mkdir -p "$(DESTDIR)/usr/share/licenses/ponysay/"
	install "COPYING" "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"

	mkdir -p "$(DESTDIR)/usr/share/man/man6"
	install "manuals/manpage.6.gz" "$(DESTDIR)/usr/share/man/man6/ponysay.6.gz"
	ln -sf "ponysay.6.gz" "$(DESTDIR)/usr/share/man/man6/ponythink.6.gz"

	mkdir -p "$(DESTDIR)/usr/share/man/es/man6"
	install "manuals/manpage.es.6.gz" "$(DESTDIR)/usr/share/man/es/man6/ponysay.6.gz"
	ln -sf "ponysay.6.gz" "$(DESTDIR)/usr/share/man/es/man6/ponythink.6.gz"

	mkdir -p "$(DESTDIR)/usr/share/info"
	install "ponysay.info.gz" "$(DESTDIR)/usr/share/info/ponysay.info.gz"
	install "ponysay.info.gz" "$(DESTDIR)/usr/share/info/ponythink.info.gz"
	install-info --dir-file="$(DESTDIR)/usr/share/info/dir" --entry="Miscellaneous" --description="My Little Ponies for your terminal" "$(DESTDIR)/usr/share/info/ponysay.info.gz"
	install-info --dir-file="$(DESTDIR)/usr/share/info/dir" --entry="Miscellaneous" --description="My Little Ponies for your terminal" "$(DESTDIR)/usr/share/info/ponythink.info.gz"

	@echo -e '\n\n'\
'/--------------------------------------------------\\\n'\
'|   ___                                            |\n'\
'|  / (_)        o                                  |\n'\
'|  \__   _  _      __                              |\n'\
'|  /    / |/ |  | /  \_|   |                       |\n'\
'|  \___/  |  |_/|/\__/  \_/|/                      |\n'\
'|              /|         /|                       |\n'\
'|              \|         \|                       |\n'\
'|   ____                                           |\n'\
'|  |  _ \  ___   _ __   _   _  ___   __ _  _   _   |\n'\
'|  | |_) |/ _ \ | '\''_ \ | | | |/ __| / _` || | | |  |\n'\
'|  |  __/| (_) || | | || |_| |\__ \| (_| || |_| |  |\n'\
'|  |_|    \___/ |_| |_| \__, ||___/ \__,_| \__, |  |\n'\
'|                       |___/              |___/   |\n'\
'\\--------------------------------------------------/'
	@echo '' | ./ponysay -f ./`if [[ "$$TERM" = "linux" ]]; then echo ttyponies; else echo ponies; fi`/pinkiecannon.pony | tail --lines=30 ; echo -e '\n'


uninstall:
	rm -fr "$(DESTDIR)/usr/share/ponysay/ponies"
	rm -fr "$(DESTDIR)/usr/share/ponysay/ttyponies"
	unlink "$(DESTDIR)/usr/bin/ponysay"
	unlink "$(DESTDIR)/usr/bin/ponythink"
	unlink "$(DESTDIR)/usr/lib/ponysay/list.pl"
	unlink "$(DESTDIR)/usr/lib/ponysay/truncater"
	unlink "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"
	unlink "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"
	unlink "$(DESTDIR)/usr/share/bash-completion/completions/ponythink"
	unlink "$(DESTDIR)/usr/share/fish/completions/ponysay.fish"
	unlink "$(DESTDIR)/usr/share/fish/completions/ponythink.fish"
	unlink "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay";
	unlink "$(DESTDIR)/usr/share/zsh/site-functions/_ponythink";
	unlink "$(DESTDIR)/usr/share/man/man6/ponysay.6.gz"
	unlink "$(DESTDIR)/usr/share/man/man6/ponythink.6.gz"
	unlink "$(DESTDIR)/usr/share/man/es/man6/ponysay.6.gz"
	unlink "$(DESTDIR)/usr/share/man/es/man6/ponythink.6.gz"
	unlink "$(DESTDIR)/usr/share/info/ponysay.info.gz"
	unlink "$(DESTDIR)/usr/share/info/ponythink.info.gz"


clean:
	rm -f "ponysaytruncater"
	rm "completion/bash-completion-think.sh"
	rm "completion/fish-completion-think.fish"
	rm "completion/zsh-completion-think.zsh"
	rm "manuals/manpage.6.gz"
	rm "manuals/manpage.es.6.gz"
	rm "ponysay.info.gz"
