#!/usr/bin/perl

# ponysaylist
# Prints a list of ponies in columns
# 
# Licensed under WTFPL
# See COPYING for details

# Author: Mattias Andrée, maandree@kth.se


use strict;
use warnings;
use utf8;
use List::MoreUtils qw(natatime);

my %hash;
my $argc = @ARGV;

my $it = natatime 2, @ARGV;
while (my ($source, $target) = &$it) {
	unless ($source eq $target) {
		push @{$hash{$target}}, $source;
	}
}

$it = natatime 2, @ARGV;
while (my ($source, $target) = &$it) {
	if ($source eq $target) {
		my @list = @{$hash{$source} // []};
		print $source;
		print ' (', join(' ', @list), ')' if @list;
		print "\n";
	}
}

