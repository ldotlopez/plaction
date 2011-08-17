#!/usr/bin/perl -w

use strict;
use warnings;
use utf8;
use Getopt::Long;
use LWP::UserAgent;
use URI::Escape ('uri_escape_utf8');
use Cwd;
use File::Basename;

package main;

$| = 1;
$ENV{'PATH'} = "/bin:/usr/bin:/sbin:/usr/sbin:";
my $verbose = 1;

#
# Download backends
#
sub fetch_wget ($) {
	my ($url) = @_;
	my $buffer = undef;

	$url =~ s,^http://,,i;
	$url = "http://$url";

	print STDERR "wget: '$url'\n" if $verbose;
	open FD, "wget -qq -O - '$url' |";
	while (read(FD, my $tmp, 1024)) {
		$buffer .= $tmp;
	}
	close FD;

	return $buffer;
}

sub fetch_lwp () {
	my ($url) = @_;

	my $ua = LWP::UserAgent->new;
	$ua->timeout(10);
	$ua->default_header('Accept-Language' => 'en',
		'Accept-Charset'  => 'utf-8;q=1, *;q=0.1');  
	$ua->env_proxy;

	$url =~ s,^http://,,i;
	$url = "http://$url";
	print STDERR "lwp: fetch URL '$url'\n" if $verbose;
	my $req = HTTP::Request->new(GET => $url);
	my $res = $ua->request($req);
  
	if (not $res->is_success) {
		print STDERR ('lwp: error fetching URL ' . $res->status_line . "\n") if $verbose;
		return undef;
	}
	return $res->content;
}

sub extract_cover_url ($) {
	my ($buffer) = @_;
	my ($idx, $idx2, $cover_idx1, $cover_idx2);

	if (($idx = index($buffer,"<span class=\"art\">")) == -1) {
		return undef;
	}

	if (($idx2 = index($buffer, "src=", $idx)) == -1 ) {
		return undef;
	}

	$cover_idx1 = $idx2 + 5;
	$cover_idx2 = index($buffer, '"', $cover_idx1);
	return substr($buffer, $cover_idx1, ($cover_idx2  - $cover_idx1));
}

sub usage ($) {
	my ($msg,$code) = @_;
	print "Error: $msg\n" if ($msg);
	print "Usage $0 [-a|--artist] artist [-b|--album] album (-o|--output output.jpg)\n";
	$code = 1 if (not $code);
	exit $code;
}

# Parse args
my ($artist, $album, $output, $fetch_url) = (undef, undef, undef, \&fetch_lwp);
while (@ARGV) {
	my $arg = shift @ARGV;
	if (($arg eq '-a') or ($arg eq '--artist')) {
		&usage('Missing artist', 1) if not @ARGV;
		$artist = shift @ARGV;
	}
	elsif (($arg eq '-b') or ($arg eq '--album')) {
		&usage('Missing album', 2) if not @ARGV;
		$album = shift @ARGV;
	}
	elsif (($arg eq '-o') or ($arg eq '--output')) {
		&usage('Missing output filename', 3) if not @ARGV;
		$output = shift @ARGV;
		($output = '/dev/stdout') if ($output eq '-');
	}
	elsif (($arg eq '-s') or ($arg eq '--special')) {
		&usage('Missing special pathname', 4) if not @ARGV;
		my $s = shift @ARGV;
		&usage("$s: No such directory", 5) if not (-d "$s");
		($artist, $album) = split(/ - /, basename(Cwd::abs_path($s)), 2);
		($output = "$s/cover.jpg") if not ($output);
	}
}

# Verify args and set defaults
&usage('Missing artist', 1) if not ($artist);
&usage('Missing album', 2)  if not ($album);
$output = 'cover.jpg'       if not ($output);
&usage(undef, 0) if ((not defined $album) or (not defined $artist));

# Fetch lastfm info page
my $lastfm_url = "www.last.fm/music/" . uri_escape_utf8($artist) . '/' . uri_escape_utf8($album);
my $lastfm_buffer = undef;
if (not ($lastfm_buffer = &$fetch_url("$lastfm_url"))) {
	print "Cannot get lastfm info page\n";
	exit 3;
}

# Extract cover URL
my $cover_url = undef;
if (not ($cover_url = &extract_cover_url($lastfm_buffer))) {
	print "Cannot find cover URL in lastfm info page\n";
	exit 4;
}

# Fetch cover data
my $cover_data = undef;
if (not ($cover_data = &$fetch_url($cover_url))) {
	print "Cannot fetch cover URL [$cover_url]\n";
	exit 5;
}

# Save to disk
open FD, "> $output" || die "$@";
syswrite FD, $cover_data;
close FD;

exit 0;

__END__

