#!/usr/bin/perl

opendir(DIR, $ARGV[0]."/share/ponysay/ponies/");
@files = readdir(DIR); 

opendir(DIR, $ARGV[0]."/share/ponysay/quotes/");
@quotes = readdir(DIR); 


foreach $file (@files)
{
    $_ = $file;
    $_ =~ s/\.pony$//g;
    $f = $_;
    if (! /^\./)
    {   foreach $quote (@quotes)
	{
	    $_ = $quote;
	    $_ =~ s/\.\d+//g;
	    $_ = '+'.$_.'+';
	    if (! /^\./)
	    {   if (/\+$f\+/)
		{   print $f."@".$quote."\n";
	    }   }
    }   }
}
