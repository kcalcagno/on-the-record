#!/usr/bin/perl

open INFILE, shift or die "Can't open input file";
open OUTFILE, ">import.txt" or die "Can't open import.txt";

while ($line = <INFILE>) {
    if ($line =~ /\D+(\d+)\D+(\d+).* - \b(.+)\b  \d+\/\d+\/\d{4}/) {
	$nd = $1;
	$opp = $2;
	$handle = $3;
	print OUTFILE "$handle,$nd,$opp\n";
    }
}

close INFILE;
close OUTFILE;
