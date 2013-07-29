
all: genponies

genpngs: ponies/*
	mkdir genpngs
	unpixelterm -d genpngs ponies/*.pony

genponies: pngs/*
	mkdir genponies
	pixelterm -d genponies pngs/*.png

