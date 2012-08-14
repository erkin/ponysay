all: truncater manpages infomanual ponythinkcompletion

truncater:
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) -o "truncater" "truncater.c"

manpages:
	gzip -9 < "manuals/manpage.6"    > "manuals/manpage.6.gz"
	gzip -9 < "manuals/manpage.es.6" > "manuals/manpage.es.6.gz"

infomanual:
	makeinfo "manuals/ponysay.texinfo"
	gzip -9  "ponysay.info"

ponythinkcompletion:
	sed -e 's/ponysay/ponythink/g' <"completion/bash-completion.sh"   | sed -e 's/\/ponythink\//\/ponysay\//g' -e 's/\\\/ponythink\\\//\\\/ponysay\\\//g' >"completion/bash-completion-think.sh"
	sed -e 's/ponysay/ponythink/g' <"completion/fish-completion.fish" | sed -e 's/\/ponythink\//\/ponysay\//g' -e 's/\\\/ponythink\\\//\\\/ponysay\\\//g' >"completion/fish-completion-think.fish"
	sed -e 's/ponysay/ponythink/g' <"completion/zsh-completion.zsh"   | sed -e 's/\/ponythink\//\/ponysay\//g' -e 's/\\\/ponythink\\\//\\\/ponysay\\\//g' >"completion/zsh-completion-think.zsh"

install-min: truncater
	mkdir -p "$(DESTDIR)/usr/share/ponysay/"
	mkdir -p "$(DESTDIR)/usr/share/ponysay/ponies"
	mkdir -p "$(DESTDIR)/usr/share/ponysay/ttyponies"
	mkdir -p "$(DESTDIR)/usr/share/ponysay/quotes"
	cp -P    ponies/*.pony "$(DESTDIR)/usr/share/ponysay/ponies/"
	cp -P ttyponies/*.pony "$(DESTDIR)/usr/share/ponysay/ttyponies/"
	cp -P    quotes/*.*    "$(DESTDIR)/usr/share/ponysay/quotes/"

	mkdir -p          "$(DESTDIR)/usr/bin/"
	install "ponysay" "$(DESTDIR)/usr/bin/ponysay"
	ln -sf  "ponysay" "$(DESTDIR)/usr/bin/ponythink"

	mkdir   -p                 "$(DESTDIR)/usr/lib/ponysay/"
	install -s "truncater"     "$(DESTDIR)/usr/lib/ponysay/truncater"
	install    "list.pl"       "$(DESTDIR)/usr/lib/ponysay/list.pl"
	install    "linklist.pl"   "$(DESTDIR)/usr/lib/ponysay/linklist.pl"
	install    "pq4ps"         "$(DESTDIR)/usr/lib/ponysay/pq4ps"
	install    "pq4ps.pl"      "$(DESTDIR)/usr/lib/ponysay/pq4ps.pl"
	install    "pq4ps-list"    "$(DESTDIR)/usr/lib/ponysay/pq4ps-list"
	install    "pq4ps-list.pl" "$(DESTDIR)/usr/lib/ponysay/pq4ps-list.pl"

	mkdir -p          "$(DESTDIR)/usr/share/licenses/ponysay/"
	install "COPYING" "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"

install-bash: ponythinkcompletion
	mkdir -p                                      "$(DESTDIR)/usr/share/bash-completion/completions/"
	install "completion/bash-completion.sh"       "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"
	install "completion/bash-completion-think.sh" "$(DESTDIR)/usr/share/bash-completion/completions/ponythink"

install-zsh: ponythinkcompletion
	mkdir -p                                      "$(DESTDIR)/usr/share/zsh/site-functions/"
	install "completion/zsh-completion.zsh"       "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay"
	install "completion/zsh-completion-think.zsh" "$(DESTDIR)/usr/share/zsh/site-functions/_ponythink"

install-fish: ponythinkcompletion
	mkdir -p                                        "$(DESTDIR)/usr/share/fish/completions/"
	install "completion/fish-completion.fish"       "$(DESTDIR)/usr/share/fish/completions/ponysay.fish"
	install "completion/fish-completion-think.fish" "$(DESTDIR)/usr/share/fish/completions/ponythink.fish"

install-man: manpages
	mkdir -p                       "$(DESTDIR)/usr/share/man/man6"
	install "manuals/manpage.6.gz" "$(DESTDIR)/usr/share/man/man6/ponysay.6.gz"
	ln -sf  "ponysay.6.gz"         "$(DESTDIR)/usr/share/man/man6/ponythink.6.gz"

install-man-es: manpages
	mkdir -p                          "$(DESTDIR)/usr/share/man/es/man6"
	install "manuals/manpage.es.6.gz" "$(DESTDIR)/usr/share/man/es/man6/ponysay.6.gz"
	ln -sf  "ponysay.6.gz"            "$(DESTDIR)/usr/share/man/es/man6/ponythink.6.gz"

install-info: infomanual
	mkdir -p                  "$(DESTDIR)/usr/share/info"
	install "ponysay.info.gz" "$(DESTDIR)/usr/share/info/ponysay.info.gz"
	install "ponysay.info.gz" "$(DESTDIR)/usr/share/info/ponythink.info.gz"
	install-info --dir-file="$(DESTDIR)/usr/share/info/dir" --entry="Miscellaneous" --description="My Little Ponies for your terminal" "$(DESTDIR)/usr/share/info/ponysay.info.gz"
	install-info --dir-file="$(DESTDIR)/usr/share/info/dir" --entry="Miscellaneous" --description="My Little Ponies for your terminal" "$(DESTDIR)/usr/share/info/ponythink.info.gz"

install-no-info: install-min install-bash install-zsh install-fish install-man install-man-es

install: install-no-info install-info
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
	if [ -d "$(DESTDIR)/usr/share/ponysay" ]; then                                rm -fr "$(DESTDIR)/usr/share/ponysay"                              ; fi
	if [ -d "$(DESTDIR)/usr/lib/ponysay"  ]; then                                 rm -fr "$(DESTDIR)/usr/lib/ponysay"                                ; fi
	if [ -f "$(DESTDIR)/usr/bin/ponysay" ]; then                                  unlink "$(DESTDIR)/usr/bin/ponysay"                                ; fi
	if [ -f "$(DESTDIR)/usr/bin/ponythink" ]; then                                unlink "$(DESTDIR)/usr/bin/ponythink"                              ; fi
	if [ -f "$(DESTDIR)/usr/share/licenses/ponysay/COPYING" ]; then               unlink "$(DESTDIR)/usr/share/licenses/ponysay/COPYING"             ; fi
	if [ -f "$(DESTDIR)/usr/share/bash-completion/completions/ponysay" ]; then    unlink "$(DESTDIR)/usr/share/bash-completion/completions/ponysay"  ; fi
	if [ -f "$(DESTDIR)/usr/share/bash-completion/completions/ponythink" ]; then  unlink "$(DESTDIR)/usr/share/bash-completion/completions/ponythink"; fi
	if [ -f "$(DESTDIR)/usr/share/fish/completions/ponysay.fish" ]; then          unlink "$(DESTDIR)/usr/share/fish/completions/ponysay.fish"        ; fi
	if [ -f "$(DESTDIR)/usr/share/fish/completions/ponythink.fish" ]; then        unlink "$(DESTDIR)/usr/share/fish/completions/ponythink.fish"      ; fi
	if [ -f "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay"; ]; then           unlink "$(DESTDIR)/usr/share/zsh/site-functions/_ponysay"          ; fi
	if [ -f "$(DESTDIR)/usr/share/zsh/site-functions/_ponythink"; ]; then         unlink "$(DESTDIR)/usr/share/zsh/site-functions/_ponythink"        ; fi
	if [ -f "$(DESTDIR)/usr/share/man/man6/ponysay.6.gz" ]; then                  unlink "$(DESTDIR)/usr/share/man/man6/ponysay.6.gz"                ; fi
	if [ -f "$(DESTDIR)/usr/share/man/man6/ponythink.6.gz" ]; then                unlink "$(DESTDIR)/usr/share/man/man6/ponythink.6.gz"              ; fi
	if [ -f "$(DESTDIR)/usr/share/man/es/man6/ponysay.6.gz" ]; then               unlink "$(DESTDIR)/usr/share/man/es/man6/ponysay.6.gz"             ; fi
	if [ -f "$(DESTDIR)/usr/share/man/es/man6/ponythink.6.gz" ]; then             unlink "$(DESTDIR)/usr/share/man/es/man6/ponythink.6.gz"           ; fi
	if [ -f "$(DESTDIR)/usr/share/info/ponysay.info.gz" ]; then                   unlink "$(DESTDIR)/usr/share/info/ponysay.info.gz"                 ; fi
	if [ -f unlink "$(DESTDIR)/usr/share/info/ponythink.info.gz" ]; then          unlink "$(DESTDIR)/usr/share/info/ponythink.info.gz"               ; fi

clean:
	if [ -f "truncater" ]; then                              rm -f "truncater"                            ; fi
	if [ -f "completion/bash-completion-think.sh" ]; then    rm -f "completion/bash-completion-think.sh"  ; fi
	if [ -f "completion/fish-completion-think.fish" ]; then  rm -f "completion/fish-completion-think.fish"; fi
	if [ -f "completion/zsh-completion-think.zsh" ]; then    rm -f "completion/zsh-completion-think.zsh"  ; fi
	if [ -f "manuals/manpage.6.gz" ]; then                   rm -f "manuals/manpage.6.gz"                 ; fi
	if [ -f "manuals/manpage.es.6.gz" ]; then                rm -f "manuals/manpage.es.6.gz"              ; fi
	if [ -f "ponysay.info.gz"  ]; then                       rm -f "ponysay.info.gz"                      ; fi

## Scripts for maintainers

ttyponies:
	mkdir -p "ttyponies"
	for pony in $$(ls --color=no "ponies/"); do                                                    \
	    echo "building ttypony: $$pony"                                                           ;\
	    if [[ `readlink "ponies/$$pony"` = "" ]]; then                                             \
	        ponysay2ttyponysay < "ponies/$$pony" | tty2colourfultty -c 1 -e > "ttyponies/$$pony"  ;\
		git add "ttyponies/$$pony"                                                            ;\
	    elif [[ ! -f "ttyponies/$$pony" ]]; then                                                   \
	        ln -s `readlink "ponies/$$pony"` "ttyponies/$$pony"                                   ;\
		git add "ttyponies/$$pony"                                                            ;\
	    fi                                                                                         \
	done

pdfmanual:
	texi2pdf "manuals/ponysay.texinfo"
	git add  "manuals/ponysay.texinfo" "ponysay.pdf"
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

submodules: clean
	(cd "ponyquotes4ponysay/"; make clean)
	git submodule init
	git submodule update

quotes: submodules
	(cd "ponyquotes4ponysay/"; make -B)
	if [[ -d quotes ]]; then git rm "quotes/"*.*; fi
	mkdir -p "quotes"
	cp "ponyquotes4ponysay/ponyquotes/"*.* "quotes"
	git add "quotes/"*.*

