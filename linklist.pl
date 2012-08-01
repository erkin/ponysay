#!/usr/bin/perl

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

my %hash;

{
	local @ARGV = @ARGV;
	while ((my ($source, $target), @ARGV) = @ARGV) {
		unless ($source eq $target) {
			push @{$hash{$target}}, $source;
		}
	}
}

while ((my ($source, $target), @ARGV) = @ARGV) {
	if ($source eq $target) {
		my @list = @{$hash{$source} // []};
		print $source;
		print ' (', join(' ', @list), ')' if @list;
		print "\n";
	}
}
