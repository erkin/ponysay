SHELL=bash

BRANCH="$(git branch | grep \\\* | sed -e s/\*\ //g)"


manual-update:
	git checkout master
	makeinfo --html "./manuals/ponysay.texinfo"
	git add "./manuals/ponysay"
	git stash
	git checkout $(BRANCH)
	git rm "./pages/ponysay/*"
	git stash pop

