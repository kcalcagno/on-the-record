#!/usr/bin/perl

open INFILE, shift or die "Can't open input file";
open OUTFILE, ">import.txt" or die "Can't open import.txt";

while ($line = <INFILE>) {
    if ($line =~ /.*?(\d{2,3}).*?(\d{2,3}).* - \b(.+)\b  \d{4}-\d\d-\d\d/) {
	$nd = $1;
	$opp = $2;
	$handle = $3;
	if ($handles{$handle}) {
	    print STDERR "Duplicate handle: $handle\n";
	} else {
	    $handles{$handle} = 1;
	}
	print OUTFILE "$handle,$nd,$opp\n";
    }
}

close INFILE;
close OUTFILE;
