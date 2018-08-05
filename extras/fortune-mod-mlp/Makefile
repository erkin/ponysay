PKGNAME=fortune-mod-mlp
PREFIX=/usr
DATA=/share
DATADIR=$(PREFIX)$(DATA)
FORTUNEDIR=$(DATADIR)/fortune
LICENSEDIR=$(DATADIR)/licenses/$(PKGNAME)

SRC = ../../ponyquotes
PSRC = ../../ponies

PONIES = $(shell find "$(SRC)" | grep '$(SRC).*\..' | sed -e "s:^$(SRC)::" | sed -e "s:^/::g" | cut -d . -f 1 | sort | uniq)


# Tab symbol for use with `echo`. echo -e is not POSIX
empty = 
tab = $(empty)	$(empty)


.PHONY: all
all: pony pony.dat


pony.dat: pony
	strfile pony


pony: $(foreach P, $(PONIES), obj/$(P))
	cat $^ > $@


obj/%: $(SRC)/%.*
	@mkdir -p obj
	test -f $@ && rm $@ || true
	pony="$$(./name-pony.sh "$(PSRC)" $*)" && \
	for file in $^; do                        \
	    cat $$file >> $@ &&                   \
	    echo "$(tab)-- $$pony" >> $@ &&       \
	    echo % >> $@                          \
	    || exit 1;                            \
	done


.PHONY: install
install: pony pony.dat
	install -d -- "$(DESTDIR)$(FORTUNEDIR)"
	install -m644 pony pony.dat -- "$(DESTDIR)$(FORTUNEDIR)"


.PHONY: install-license
install-license:
	install -Dm644 -- COPYING "$(DESTDIR)$(LICENSEDIR)/COPYING"
	install -Dm644 -- "$(shell realpath LICENSE)" "$(DESTDIR)$(LICENSEDIR)/LICENSE"


.PHONY: uninstall
uninstall:
	-rm -- "$(DESTDIR)$(FORTUNEDIR)/pony"
	-rm -- "$(DESTDIR)$(FORTUNEDIR)/pony.dat"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/COPYING"
	-rm -- "$(DESTDIR)$(LICENSEDIR)/LICENSE"
	-rmdir -- "$(DESTDIR)$(LICENSEDIR)"


.PHONY: list-ponies
list-ponies:
	@for p in $(PONIES); do echo "$$p"; done


.PHONY: clean
clean:
	-rm -r obj
	-rm pony pony.dat

