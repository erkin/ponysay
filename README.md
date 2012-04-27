ponysay - A cowsay wrapper with ponies.

The pony files are [desktop/browser ponies](http://web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html) converted using [img2xterm](https://github.com/rossy2401/img2xterm).

![Derp](http://i.imgur.com/xOJbE.png)

[](/derp "Today your terminal, tomorrow the world!")

Installation on Linux
---------------------

If you do not already have cowsay you will need to install it

    apt-get install cowsay

[Download](https://github.com/erkin/ponysay/zipball/master) this project. In the terminal navagate to the ponysay folder and run
  
    sudo make

This will install ponysay into the `/usr` directory to use ponysay run

    ponysay "I am just the cutest pony"

### Pony fortune on terminal startup 

This requires that you have the `fortune` command installed

    apt-get install fortune
  
Edit your `~/.bashrc` and add this to the end of the file

    fortune | ponysay

Now every time you open a terminal a pony should give your fortune

### FAQ

__Q:__ The output looks like a mess in _(TTY/PuTTY/other)_!

__A:__ Unfortunately, there's nothing much we can do about it. See [issue 1](https://github.com/erkin/ponysay/issues/1).

__Q:__ You are missing _(my-favourite-pony)_!

__A:__ Ask and we'll add!

__Q:__ Which programs do you use to generate the pony files?

__A:__ The pony files are actually [browser ponies](http://web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html) that are generated into cow files via [img2xterm](https://github.com/rossy2401/img2xterm).
