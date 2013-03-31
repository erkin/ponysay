`ponysay` — cowsay reimplemention for ponies.
You may find the code on github: https://github.com/jaseg/ponysay

![Derp](http://i.imgur.com/xOJbE.png)

```
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

FAQ
---

*Q:* The output looks like a mess in `TTY/PuTTY/other`!
*A:* Yeah, sorry. If you find a fix, send me a pull request.

*Q:* Which programs do you use to generate the pony files?
*A:* The pony files are actually mostly a bunch of selected [browser ponies](http://web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html), converted using [util-say](https://github.com/maandree/util-say).
