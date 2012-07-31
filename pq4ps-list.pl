#!/usr/bin/perl

print "(sed";

foreach $arg (@ARGV)
{
    print " -e 's/ $arg / \e[1m$arg\e[21m /g'";
    print " -e 's/ $arg)/ \e[1m$arg\e[21m)/g'";
    print " -e 's/($arg /(\e[1m$arg\e[21m /g'";
    print " -e 's/($arg)/(\e[1m$arg\e[21m)/g'";
    print " -e 's/ $arg\$/ \e[1m$arg\e[21m/g'";
    print " -e 's/^$arg /\e[1m$arg\e[21m /g'";
    print " -e 's/^$arg\$/\e[1m$arg\e[21m/g'";
}

print " | sed";

foreach $arg (@ARGV)
{
    print " -e 's/ $arg)/ \e[1m$arg\e[21m)/g'";
    print " -e 's/ $arg\$/ \e[1m$arg\e[21m/g'"
}

print ")";
