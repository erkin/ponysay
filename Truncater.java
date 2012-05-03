import java.io.*;

public class Truncater
{
    public static void main(final String... args) throws IOException
    {
	final int width;
	if ((width = getWidth()) > 15) //sanity
	{
	    final OutputStream stdout = new BufferedOutputStream(System.out);
	    OutputStream out = new OutputStream()
		    {
			/**
			 * The number of column on the current line
			 */
			private int x = 0;
			
			/**
			 * Escape sequence state
			 */
			private int esc = 0;
			
			/**
			 * Last bytes as written
			 */
			private boolean ok = true;
			
			
			/**
			 * {@inheritDoc}
			 */
			@Override
			public void write(final int b) throws IOException
			{
			    if (this.esc == 0)
			    {
				if (b == '\n')
				{
				    if (x >= width)
				    {
					write('\033');
					write('[');
					write('4');
					write('9');
					write('m');
				    }
				    this.x = -1;
				}
				else if (b == '\t')
				{
				    int nx = 8 - (x & 7);
				    for (int i = 0; i < nx; i++)
					write(' ');
				    return; //(!)
				}
				else if (b == '\033')
				    this.esc = 1;
			    }
			    else if (this.esc == 1)
			    {
				if      (b == '[')  this.esc = 2;
				else if (b == ']')  this.esc = 3;
				else                this.esc = 10;
			    }
			    else if (this.esc == 2)
			    {
				if ((('a' <= b) && (b <= 'z')) || (('A' <= b) && (b <= 'Z')))
				    this.esc = 10;
			    }
			    else if ((this.esc == 3) && (b == 'P'))
			    {
				this.esc = ~0;
			    }
			    else if (this.esc < 0)
			    {
				this.esc--;
				if (this.esc == ~7)
				    this.esc = 10;
			    }
			    else
				this.esc = 10;
			        
			    if ((x < width) || (this.esc != 0) || (ok && ((b & 0xC0) == 0x80)))
			    {
				stdout.write(b);
				if (this.esc == 0)
				    if ((b & 0xC0) != 0x80)
					x++;
				ok = true;
			    }
			    else
				ok = false;
			    if (this.esc == 10)
				this.esc = 0;
			}
			
			/**
			 * {@inheritDoc}
			 */
			@Override
			public void flush() throws IOException
			{
			    stdout.flush();
			}
		};
	    
	    System.setOut(new PrintStream(out));
	}
	
	
	InputStream in = System.in;
	OutputStream out = System.out;
	
	for (int d; (d = in.read()) != -1;)
	    out.write(d);
	out.flush();
    }

    /**
     * Gets the width of the terminal
     *
     * @return  The width of the terminal
     */
    public static int getWidth()
    {
	try
	{
	    Process process = (new ProcessBuilder("/bin/sh", "-c", "tput cols 2> " + (new File("/dev/stderr")).getCanonicalPath())).start();
	    String rcs = new String();
	    InputStream stream = process.getInputStream();
	    int c;
	    while (((c = stream.read()) != '\n') && (c != -1))
		rcs += (char)c;
	    try
	    {
		stream.close();
	    }
	    catch (final Throwable err)
	    {
		//Ignore
	    }
	    return Integer.parseInt(rcs);
	}
	catch (final Throwable err)
	{
	    return -1;
	}
    }
}

