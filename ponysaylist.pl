#!/usr/bin/perl

# ponysaylist
# Prints a list of ponies in columns
# 
# Licensed under WTFPL
# See COPYING for details

# Author: Mattias Andrée, maandree@kth.se


$first = 1;
$scrw = 1;
$maxw = 1;

foreach $arg (@ARGV)
{
	# Format names from ponyies names
	$arg =~ s/([a-z])([A-Z])/\1 \2/;
	$arg =~ s/_(.*)/\t(\1)/;
	
    if ($first == 1)
    {   $first = 0;
	$scrw = $arg;
    }
    else
    {   $w = length $arg;
	$maxw = $w if ($w > $maxw);
    }
}

$cols = int (($scrw + 2) / ($maxw + 2));
$cols = 1 if ($cols < 1);


@list = ();

$first = 1;
$items = 0;
foreach $arg (@ARGV)
{
    if ($first == 1)
    {   $first = 0;
    }
    else
    {   $ws = $maxw - (length $arg);
	push @list, $arg.(" "x$ws);
	$items += 1;
    }
}


$rows = int (($items + $cols - 1) / $cols);
$i = 0;
@rowlist = ();

while ($i < $items)
{   $row = 0;
    while (($row < $rows) and ($i < $items))
    {
	$rowlist[$row] .= "  " unless ($i < $rows);
	$rowlist[$row] .= $list[$i];
	$row += 1;
	$i += 1;
}   }

foreach $row (@rowlist)
{
    print $row."\n";
}

