`ponysay` — cowsay reimplemention for ponies.

![Derp](http://i.imgur.com/xOJbE.png)

Today your terminal, tomorrow the world!


Installation on GNU/Linux (or other Unix implementations)
---------------------------------------------------------

[Download](/erkin/ponysay/downloads) or clone the project.
In the terminal, `cd` into the ponysay directory and `./setup.py --freedom=partial install` or `python3 setup.py --freedom=partial install`.
Superuser permissions might be required in order to run `./setup.py --freedom=partial install` without `--private`, on most systems this
can be achieved by running `sudo ./setup.py --freedom=partial install`.
If installing only the completely free ponies is desired, `--freedom=strict` should be used instead of `--freedom=partial`.
For additional information, an extensive [manual in PDF](https://github.com/erkin/ponysay/blob/master/ponysay.pdf?raw=true) is provided.

In order to use ponysay, run:

    ponysay "I am just the cutest pony!"

Or if you have a specific pony in your mind:

    ponysay -f pinkie "Partay!~"

Consult `info ponysay`, `man 6 ponysay` or `ponysay -h` for additional information.
Spanish and Turkish manuals are also available: `man -L es 6 ponysay` and 'man -L tr 6 ponysay` respectively.

#### Arch Linux
The package is in the official repositories as `community/ponysay`. A Git version is also present, named `ponysay-git` in AUR.

#### Chakra
A git version of the package is available as `ponysay-git` in CCR, alongside a stable package called `ponysay`.

#### Gentoo Linux
There is a package for Gentoo, to make installation and updating simple. You can find it in [this overlay](https://github.com/etu/aidstu-overlay). The package is named `games-misc/ponysay`.

#### Debian GNU/Linux and Ubuntu
The DEB file can be found on this PPA [here](https://launchpad.net/~vincent-c/+archive/ppa).

#### Mac OS X

A `ponysay` [Homebrew](https://github.com/mxcl/homebrew) formula is available.

### Print a pony fortune upon terminal startup

This requires the `fortune` utility to be installed. It can install be from the distribution's repositories (might be named `fortune-mod`).
Alternatively, one can just fetch the source code from [here](http://ftp.ibiblio.org/pub/linux/games/amusements/fortune/).

You can try [this](http://www.reddit.com/r/mylittlelinux/comments/srixi/using_ponysay_with_a_ponified_fortune_warning/) script or
[ponypipe](/maandree/ponypipe) to ponify fortunes.

Edit your `~/.bashrc` and add this to the end of the file

    fortune | ponysay

Afterwards, every time you open a terminal a pony should give you a fortune.

### Pony quotes

Running `ponysay -q` will print a random pony saying one of its quotes from My Little Pony: Friendship is Magic. The pony can be specified: `ponysay -q pinkie`.
Just as with `-f`, `-q` can be used multiple times to specify a set of ponies from which a single one will be selected randomly.

When running `ponysay -l` or `ponysay -L` the ponies with quotes will be printed in bold or bright (depending on the used terminal).

### Ponies in TTY (Unix VT)

If you have a custom colour palette edit your `~/.bashrc` and add

```
if [ "$TERM" = "linux" ]; then
    function ponysay
    {
        exec ponysay "$@"
        #RESET PALETTE HERE
    }
fi
```

Read the PDF or info manual for more information.


Installation on Microsoft™ Windows®
-----------------------------------
[¯\\\_(ツ)\_/¯](http://fc05.deviantart.net/fs71/i/2011/266/d/e/shrugpony_firefly_by_imaplode-d4aqtvx.png)


Dependencies
------------

### Runtime dependencies

`coreutils`: `stty` in coreutils used to determine size of the terminal.

`python>=3`: `ponysay` is written in Python 3.

### Package building dependencies

`gzip`: Used for compressing manuals (suppressable with `./configure --without-info-compression --without-man-compression`).

`texinfo`: Used for building the info manual (suppressable with `./configure --without-info`).

`python>=3`: The installation process is written in Python 3.

Run `./dependency-test.sh` if things are not working for you.


FAQ
---

__Q:__ The output looks like a mess in _(TTY/PuTTY/other)_!

__A:__ Unfortunately we cannot make it perfect, see [issue 1](//github.com/erkin/ponysay/issues/1). But we have done a lot, read more about how to get the best of the current state of the art has to offer in the [manual](//github.com/erkin/ponysay/blob/master/ponysay.pdf?raw=true).

__Q:__ The output looks like a mess in _(xfce4-terminal/mate-terminal/xterm/[...])_ with _(this)_ font!

__A:__ We use blocks for printing the ponies, if the blocks are misaligned, or if you do not use a truly monospaced font with aligned blocks try another monospaced font, such as 'Fixed [...]' or 'Liberation Mono.'

__Q:__ You are missing _(my-favourite-pony)_!

__A:__ [Ask](//github.com/erkin/ponysay/issues) and we'll add!

__Q:__ Which programs do you use to generate the pony files?

__A:__ The pony files are in fact mostly a bunch of selected [browser ponies](//web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html), converted using [util-say](//github.com/maandree/util-say),
Other are taken from desktop ponies, and the others are created specifically for ponysay.

The [PDF manual](//github.com/erkin/ponysay/blob/master/ponysay.pdf?raw=true) should answer most of your questions.
