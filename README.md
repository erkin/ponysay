`ponysay` - A cowsay wrapper for ponies.

![Derp](http://i.imgur.com/xOJbE.png)

Today your terminal, tomorrow the world!

Installation on GNU/Linux (or other Unix implementations)
---------------------------------------------------------

First of all, you need `cowsay` from your local repositories.
Obtain it from [here](http://www.nog.net/~tony/warez) if you wish to compile it yourself.
This is often sufficient, but if is not you may be missing one of the standard packages: [bash](ftp://ftp.gnu.org/gnu/bash/), [coreutils](ftp://ftp.gnu.org/gnu/coreutils/) or [sed](ftp://ftp.gnu.org/gnu/sed/).

[Download](https://github.com/erkin/ponysay/downloads) or clone the project.
In the terminal, `cd` into the ponysay directory and `make && make install`.

This will install ponysay into the $PREFIX (`/usr` by default, meaning you may need to `make install` as root, e.g. `sudo make install`.)

If either `make` or `make install` fails you be missing one of the standard packages:
[gcc](ftp://ftp.gnu.org/gnu/gcc/), [gzip](ftp://ftp.gnu.org/gnu/gzip/), [make](ftp://ftp.gnu.org/gnu/make/) or [coreutils](ftp://ftp.gnu.org/gnu/coreutils/).

In order to use ponysay, run:

    ponysay "I am just the cutest pony!"
    
Or if you have a specific pony in your mind:

    ponysay -f pinkie "Partay!~"

Run `info ponysay`, `man 6 ponysay` or `ponysay -h` for more information.
A Spanish manual is available: `man -L es 6 ponysay`.


### Pony fortune on terminal startup 

This requires that you have the `fortune` utility installed. You can install it from your repositories (may be named `fortune-mod`)
or just fetch the source code from [here](ftp://ftp.ibiblio.org/pub/linux/games/amusements/fortune/).

You can try [this](http://www.reddit.com/r/mylittlelinux/comments/srixi/using_ponysay_with_a_ponified_fortune_warning/) script or
[ponypipe](https://github.com/maandree/ponypipe) to ponify fortunes.

Edit your `~/.bashrc` and add this to the end of the file

    fortune | ponysay

Now every time you open a terminal a pony should give your fortune

### Pony quotes

Installing [ponyquotes4ponysay](https://github.com/maandree/ponyquotes4ponysay) will enable My Little Pony quotes with associated pony.

Run `ponysay -q` will give you a random pony saying one it its quote from MLP:FiM. Add one or more argument after `-q` to sepecify a
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

Installation on Microsoft™ Windows®
-----------------------------------
[¯\\\_(ツ)\_/¯](http://i.imgur.com/2nP5N.png)

Dependencies
------------

### Required runtime dependencies

`bash`: required for the main script [file: ponysay]

`cowsay`: this is a wrapper for cowsay

`coreutils`: the main script uses stty, cut, ls, cat, sort, readlink, pwd, head and tail

`sed`: used to remove .pony from pony names when running `ponysay -l` and `ponysay -l`

`perl`: required to run `ponysay -l` and `ponysay -L`

### Package building dependencies

`gcc`: used for compiling ponysaytruncater.c

`gzip`: used for compressing manpages

`make`: required to run the make script

`coreutils`: make script uses install, unlink, rm, ln, mkdir and cp

FAQ
---

__Q:__ The output looks like a mess in _(TTY/PuTTY/other)_!

__A:__ Unfortunately, there's nothing much we can do about it. See [issue 1](https://github.com/erkin/ponysay/issues/1).

__Q:__ You are missing _(my-favourite-pony)_!

__A:__ [Ask](https://github.com/erkin/ponysay/issues) and we'll add!

__Q:__ Which programs do you use to generate the pony files?

__A:__ The pony files are actually mostly a bunch of selected [browser ponies](http://web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html)
that are generated into cow files via [img2xterm](https://github.com/rossy2401/img2xterm) or [util-say](https://github.com/maandree/util-say).
