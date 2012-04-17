ponysay - A cowsay wrapper with ponies.

The pony files are [desktop/browser ponies](http://web.student.tuwien.ac.at/~e0427417/browser-ponies/ponies.html) converted using [img2xterm](https://github.com/rossy2401/img2xterm).

![Derp](http://i.imgur.com/xOJbE.png)

[](/derp "Today your terminal, tomorrow the world!")

Install Linux
-------------

[Download](https://github.com/erkin/ponysay/zipball/master) this project. In the terminal navagate to the ponysay folder and run
  
    sudo make

This will install ponysay into the `/usr` directory to use ponysay run

    ponysay "I am just the cutest pony"

### Pony fortune on terminal startup 

This requires that you have the `fortune` command installed

    apt-get install fortune
  
Edit your `~/.bashrc` and add this to the end of the file

    fotune | ponysay

Now every time you open a terminal a pony should give your fortune
