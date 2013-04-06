ponysay — cowsay with ponies
============================

![Derp](http://i.imgur.com/xOJbE.png)

```
<3 ./ponysay.py --help
usage: ponysay.py [-h] [-p PONY] [-q] [-c] [-C] [-w WIDTH] [-b BALLOON]
                  [text [text ...]]

Cowsay with ponies

positional arguments:
  text                  The text to be placed in the speech bubble

optional arguments:
  -h, --help            show this help message and exit
  -p PONY, --pony PONY  The name of the pony to be used. Use "-p list" to list
                        all ponies, "-p random" (default) to use a random
                        pony.
  -q, --quote           Use a random quote of the pony being displayed as text
  -c, --center          Use a random quote of the pony being displayed as text
  -C, --center-text     Center the text in the bubble
  -w WIDTH, --width WIDTH
                        Terminal width. Use 0 for unlimited width. Default:
                        autodetect
  -b BALLOON, --balloon BALLOON
                        Balloon style to use. Use "-b list" to list available
                        styles.
```

This is my fork of https://github.com/erkin/ponysay
I really liked the concept, but I sort-of WTF-ed at the 2458-line python script powering it. So I rewrote the thing from scratch in actual python (not that bad since most of the work is done by util-say). Also, I missed a "--center"-option, so I added one. This rewrite is 117 lines long, and that includes the 7 original bubble styles which now are embedded in the python script. This means 95.2% less bloat, which I consider a success. Also, the rewrite is about 50-85% faster.

Fork me on github: https://github.com/jaseg/ponysay

FAQ
---

__Q:__ The output looks like a mess in `TTY/PuTTY/other`

__A:__ Yeah, sorry. If you find a fix, send me a pull request.

__Q:__ Which programs do you use to generate the pony files?

__A:__ The pony files are actually mostly a bunch of selected [browser ponies](http://web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html), converted using [util-say](https://github.com/maandree/util-say).

Conversion
----------
Convert the old quote format with
```
for line in $(cat ponyquotes/ponies|grep +); do n=${line%%+*}; for a in $(sed s/+/\\n/g<<<${line#*+}); do ln -s quotes/${n}.quotes quotes/${a}.quotes; done; done
```
Afterwards, clean up the broken symlinks with ```find -L quotes -type l -delete```
