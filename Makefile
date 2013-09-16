
all: genponies

genpngs:
	mkdir genpngs
	unpixelterm -d genpngs ponies/*.pony

genponies:
	mkdir ponysay/ponies
	pixelterm -d ponysay/ponies pngs/*.png

