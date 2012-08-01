#!/usr/bin/env perl

# ponysaylist
# Prints a list of ponies in columns
# 
# Licensed under WTFPL
# See COPYING for details

# Author: Mattias Andrée, maandree@kth.se
#         spider-mario


use strict;
use warnings;
use utf8;
use feature qw(say);
use integer;
use List::Util qw(max);

my $scrw = shift @ARGV // 1;

#for (@ARGV) {
#	# Format names from pony names
#	s/(?<=[a-z])(?=[A-Z])/ /;
#	s/_(.*)/\t($1)/;
#}

my $maxw = max 1, map {length} @ARGV;

my $cols = max 1, (($scrw + 2) / ($maxw + 2));

my @list = map {sprintf "%-${maxw}s", $_} @ARGV;

my $rows = (@list + $cols - 1) / $cols;

my @rowlist;
for my $i (0 .. $#list) {
	push @{$rowlist[$i % $rows]}, $list[$i];
}

say join '  ', @$_ for @rowlist;
