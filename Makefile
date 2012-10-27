SHELL=bash

manual-update:
	(branch=$$(git branch | grep \\\* | sed -e s/\*\ //g)	;\
	 git checkout master					;\
	 makeinfo --html "./manuals/ponysay.texinfo"		;\
	 git add "./ponysay"					;\
	 git stash						;\
	 git checkout $$branch					;\
	)
	git rm "./pages/ponysay/*"
	git stash pop
	git mv "./ponysay" "./pages"

