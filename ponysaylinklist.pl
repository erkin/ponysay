#!/usr/bin/perl

# ponysaylist
# Prints a list of ponies in columns
# 
# Licensed under WTFPL
# See COPYING for details

# Author: Mattias Andrée, maandree@kth.se


%hash = ();
$argc = @ARGV;

$i = 0;
while ($i < $argc)
{
    $source = $ARGV[$i];
    $i += 1;
    $target = $ARGV[$i];
    $i += 1;
    if ($source eq $target)
    {
        $hash{$source} = [ () ];
    }
}

$i = 0;
while ($i < $argc)
{
    $source = $ARGV[$i];
    $i += 1;
    $target = $ARGV[$i];
    $i += 1;
    unless ($source eq $target)
    {
        push @{ $hash{$target} }, $source;
    }
}

$i = 0;
while ($i < $argc)
{
    $source = $ARGV[$i];
    $i += 1;
    $target = $ARGV[$i];
    $i += 1;
    if ($source eq $target)
    {
        @list = @{ $hash{$source} };
        $first = 1;
        print $source;
        foreach $link (@list)
        {
            if ($first eq 1)
            {
                print " (".$link;
                $first = 0;
            }
            else
            {
                print " ".$link;
            }
        }
        if ($first eq 0)
        {
            print ")";
        }
        print "\n";
    }
}

