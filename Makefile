ponydir=/usr/share/ponies/
scripts=ponysay ponythink
bindir=/usr/bin/
install:
	mkdir $(ponydir)
	cp -r ponies $(ponydir)
	cp $(scripts) $(bindir)
