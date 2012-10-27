SHELL=bash

BRANCH="$(git branch | grep \\\* | sed -e s/\*\ //g)"


manual-update:
	git checkout master
	makeinfo --html "./manual/ponysay.texinfo"
	git add "./manual/ponysay"
	git stash
	git checkout $(BRANCH)
	git rm "./manual/ponysay/*"
	git stash pop

