`ponysay` — cowsay reimplemention for ponies.

![Derp](http://i.imgur.com/xOJbE.png)

Today your terminal, tomorrow the world!


Installation on GNU/Linux (or other Unix implementations)
---------------------------------------------------------

[Download](/erkin/ponysay/downloads) or clone the project.
In the terminal, `cd` into the ponysay directory and `./configure && make install`.
You make need to be super user to run `make install`, on most systems this
can be achieved by running `sudo make install`.
For more information we have provided you with an extensive [manual in PDF](https://github.com/erkin/ponysay/blob/master/ponysay.pdf?raw=true).

In order to use ponysay, run:

    ponysay "I am just the cutest pony!"
    
Or if you have a specific pony in your mind:

    ponysay -f pinkie "Partay!~"

Run `info ponysay`, `man 6 ponysay` or `ponysay -h` for more information.
A Spanish manual is available: `man -L es 6 ponysay`.

#### Arch Linux
The package is in the official repositories as `community/ponysay`.

#### Gentoo Linux
There is a package for Gentoo, to make installation and keeping it up to date easy. You can find it in [this overlay](/etu/aidstu-overlay). The package is named `games-misc/ponysay`.

#### Debian GNU/Linux and Ubuntu
The DEB file can be found [here](http://roryholland.co.uk/misc.html#ponysay) and the PPA can be found [here](https://launchpad.net/~blazemore/+archive/ponysay).

### Pony fortune on terminal startup 

This requires that you have the `fortune` utility installed. You can install it from your repositories (may be named `fortune-mod`)
or just fetch the source code from [here](ftp://ftp.ibiblio.org/pub/linux/games/amusements/fortune/).

You can try [this](http://www.reddit.com/r/mylittlelinux/comments/srixi/using_ponysay_with_a_ponified_fortune_warning/) script or
[ponypipe](/maandree/ponypipe) to ponify fortunes.

Edit your `~/.bashrc` and add this to the end of the file

    fortune | ponysay

Now every time you open a terminal a pony should give your fortune

### Pony quotes

Running `ponysay -q` will give you a random pony saying one it its quote from MLP:FiM. Add one or more argument after `-q` to sepecify a
set of ponies from which one will be selected randomly.

When running `ponysay -l` or `ponysay -L` the ponies which have quotes will be printed bold or bright (depending on terminal).

### Ponies in TTY (Linux VT)

If you have a custom colour palette edit your `~/.bashrc` and add

    if [ "$TERM" = "linux" ]; then
        function ponysay
        {
            exec ponysay "$@"
            #RESET PALETTE HERE
        }
    fi

Read the PDF or info manual for more information.


Installation on Microsoft™ Windows®
-----------------------------------
[¯\\\_(ツ)\_/¯](http://i.imgur.com/2nP5N.png)


Dependencies
------------

### Required runtime dependencies

`coreutils`: stty in coreutils used to determine size of the terminal

`python>=3`: written in python 3

### Package building dependencies

`gzip`: used for compressing manuals (suppressable with `./configure --without-info-compression --without-man-compression`)

`texinfo`: used for building info manual (suppressable with `./configure --without-info`)

`info`: used for installing info manual to info's dir file (suppressable with `./configure --without-info-install`)

`python>=3`: the installation process is written in python 3

Run `./dependency-test.sh` if things are not working for you.


FAQ
---

__Q:__ The output looks like a mess in _(TTY/PuTTY/other)_!

__A:__ Unfortunately we cannot make it perfect, see [issue 1](/erkin/ponysay/issues/1). But we have done a lot, read more about how to get the best the current state of the art has to offer in the [manual](/erkin/ponysay/blob/master/ponysay.pdf?raw=true).

__Q:__ You are missing _(my-favourite-pony)_!

__A:__ [Ask](/erkin/ponysay/issues) and we'll add!

__Q:__ Which programs do you use to generate the pony files?

__A:__ The pony files are actually mostly a bunch of selected [browser ponies](//web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html), converted using [util-say](/maandree/util-say).

The [PDF manual](/erkin/ponysay/blob/master/ponysay.pdf?raw=true) should answer most of your questions.
