/* ponysaytruncater
 * Output truncater used by ponysay to stop
 * large ponies from being printed badly.
 * 
 * Licensed under WTFPL
 * See COPYING for details
 */
#include <stdio.h>
#define  String   char*
#define  boolean  char
#define  true     1
#define  false    0

/* Stdin file descriptor ID */
#define  STDIN  0

/* The number of columns on the current line */
static int col =  0;

/* Escape sequence state */
static int esc = 0;

/* Last bytes as written */
static boolean ok = true;

void write(char b, int width);
int toInt(String string);


/* Mane method!
 *   The only argument, in addition to the executed file,
 *   should be the width of the terminal which you get by
 *   adding <code>`tput cols || echo 0`</code> as an argument.
 *   
 * @param  argc  The number of startup arguments
 * @param  argv  The startup arguments, the first is the file itself
 * 
 * @author  Mattias Andrée, maandree@kth.se
 */
void main(int argc, String* argv)
{
  int width = 0;
  if (argc > 1)
    width = toInt(*(argv + 1));
  
  char b = 0;
  
  if (width > 15) /* sanity */
    while (read(STDIN, &b, 1))
      write(b, width);
  else
    while (read(STDIN, &b, 1))
      printf("%c", b);
}

/* Writes a character to stdout, iff it fits within the terminal
 * 
 * @param  b      The character (byte) to write
 * @param  width  The width of the terminal
 */
void write(char b, int width)
{
  int i;
  char tabstop;
  
  if (esc == 0)
    {
      if (b == '\n')
	{
	  if (col >= width)
	    {
	      /* Reset background colour */
	      write('\e', width);
	      write('[', width);
	      write('4', width);
	      write('9', width);
	      write('m', width);
	    }
	  col = -1;
	}
      else if (b == '\t')
	{
	  /* Tab to next pos ≡₈ 0 */
	  tabstop = 8 - (col & 7);
	  for (i = 0; i < tabstop; i++)
	    write(' ', width);
	  return; /* (!) */
	}
      else if (b == '\e')
	esc = 1;
    }
  else if (esc == 1)
    {
      if      (b == '[')  esc = 2;  /* CSI: CSI ends with a letter, m is for colour */
      else if (b == ']')  esc = 3;  /* OSI: OSI P is for palette editing in Linux VT */
      else                esc = 10; /* Nothing to see here, move along */
    }
  else if (esc == 2)
    {
      if ((('a' <= b) && (b <= 'z')) || (('A' <= b) && (b <= 'Z')))
	esc = 10;
    }
  else if ((esc == 3) && (b == 'P'))
    {
      esc = ~0;
    }
  else if (esc < 0)
    {
      esc--;
      if (esc == ~7)
	esc = 10;
    }
  else
    esc = 10;
  
  if (
      /* Can be printed:
	 within bounds  ∨
	 ∨ escape sequence  ∨
	 ∨ last with printed ∧ not first byte in character */
      (col < width) ||
      (esc != 0) ||
      (ok && ((b & 0xC0) == 0x80)))
    {
      printf("%c", b);
      if ((esc == 0) && ((b & 0xC0) != 0x80))
	/* Count up columns of not in escape sequnce and */
	col++; /* the byte is not the first byte in the character */
      ok = true;
    }
  else
    ok = false;
  
  if (esc == 10)
    esc = 0;
}

/* Converts a string to an integer
 * 
 * @param   string  The string to convert
 * @return          The integer represented by the string
 */
int toInt(String string)
{
  int rc = 0;
  String str = string;
  char c = 0;
  
  while ((c = *str++) != 0)
    rc = (rc << 1) + (rc << 3) - (c & 15);
  
  return -rc;
}
