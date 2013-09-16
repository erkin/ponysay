
all: genponies

genpngs: ponies/*
	mkdir genpngs
	unpixelterm -d genpngs ponies/*.pony

genponies: pngs/*
	pixelterm -d ponysay/ponies pngs/*.png

