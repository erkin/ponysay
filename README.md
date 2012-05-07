`ponysay` - A cowsay wrapper with ponies.

The pony files are [desktop/browser ponies](http://web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html) converted using [img2xterm](https://github.com/rossy2401/img2xterm).

![Derp](http://i.imgur.com/xOJbE.png)
Today your terminal, tomorrow the world!

Installation on Linux (or other Unix)
-------------------------------------

If you do not already have `cowsay` you will need to install it

    apt-get install cowsay # assuming dpkg

[Download](https://github.com/erkin/ponysay/downloads) the latest project. In the terminal, `cd` into the ponysay directory and run
  
    sudo make

This will install ponysay into the $PREFIX (`/usr` by default). In order to use ponysay, run

    ponysay "I am just the cutest pony"
    
Or if you have a specific pony in your mind:

    ponysay -f pinkie "Partay!~"

### Pony fortune on terminal startup 

This requires that you have the `fortune` utility installed

    apt-get install fortune
    
You can try [this](http://www.reddit.com/r/mylittlelinux/comments/srixi/using_ponysay_with_a_ponified_fortune_warning/) script to ponify fortunes.
  
Edit your `~/.bashrc` and add this to the end of the file

    fortune | ponysay

Now every time you open a terminal a pony should give your fortune

### Ponies in TTY (Linux VT)

If you have a custom colour palette edit your `~/.bashrc` and add

    if [ "$TERM" = "linux" ]; then
        function ponysay
        {
            exec ponysay $@
            #RESET PALETTE HERE
        }
    fi

Installation on Microsoft™ Windows®
-----------------------------------
[¯\\\_(ツ)\_/¯](http://i.imgur.com/2nP5N.png)

FAQ
---

__Q:__ The output looks like a mess in _(TTY/PuTTY/other)_!

__A:__ Unfortunately, there's nothing much we can do about it. See [issue 1](https://github.com/erkin/ponysay/issues/1).

__Q:__ You are missing _(my-favourite-pony)_!

__A:__ Ask and we'll add!

__Q:__ Which programs do you use to generate the pony files?

__A:__ The pony files are actually a bunch of selected [browser ponies](http://web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html) that are generated into cow files via [img2xterm](https://github.com/rossy2401/img2xterm).
