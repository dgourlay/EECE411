# -----------------------------------------------------------------
# $Id: PLDeploy.pm,v 1.5 2004/03/29 23:30:55 mbowman Exp $
#
# Copyright (c) 2004 Intel Corporation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.

#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.

#     * Neither the name of the Intel Corporation nor the names of its
#       contributors may be used to endorse or promote products derived
#       from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# EXPORT LAWS: THIS LICENSE ADDS NO RESTRICTIONS TO THE EXPORT LAWS OF
# YOUR JURISDICTION. It is licensee's responsibility to comply with any
# export regulations applicable in licensee's jurisdiction. Under
# CURRENT (May 2000) U.S. export regulations this software is eligible
# for export from the U.S. and can be downloaded by or otherwise
# exported or reexported worldwide EXCEPT to U.S. embargoed destinations
# which include Cuba, Iraq, Libya, North Korea, Iran, Syria, Sudan,
# Afghanistan and any other country to which the U.S. has embargoed
# goods and services.
# -----------------------------------------------------------------

=head1 NAME

PlanetLab::PLDeploy - Perl extension for PlanetLab Slice Deploy toolkit

=head1 SYNOPSIS

  use PlanetLab::PLDeploy

=head1 DESCRIPTION

The PlanetLab::PLDeploy class is used to manage configuration
information within PLDeploy control scripts that run on PlanetLab
nodes. Information is provided for various deployment parameters (name
of slice, cog directory, etc) and for values stored in a "config"
file. If it exists, the configuration file stored in the PL directory on
the node is read first, then the configuraiton file stored in the
current cog's directory.

The following values are always defined: Verbose, Debug, Version,
SliceName, SliceRoot, SliceEmail, SliceCntl, SliceInit, NodeName,
CogName, CogRoot, CogOutbound, CogArchive, and CogTmp. 

Values stored in the configuration file are accessible through the
hash; for example, $gCogCntl->{'Version'}.

=head2 new

=head2 UpdateCrontab($cmd,$key)

Sets the script associated with the key in the crontab for the current
slice. The key is typically the name of the cog, but can be any
string. If $cmd is the empty string, the command will be removed from
crontab.

=head2 DoSystem($cmd)

Execute the command line and return the exit status.

=head1 EXAMPLE

BEGIN {
    my $home = $ENV{'HOME'};
    my $arch = $Config{archname};
    push(@INC,"$home/PL/lib/perl5");
    push(@INC,"$home/PL/lib/perl5/$arch/auto");
}

use PlanetLab::PLDeploy;
my $gCogCntl = PlanetLab::PLDeploy->new;

if ($gCogCntl->Verbose) {
    print "COG=" . $gCogCntl->CogName . "\n";
    print "IDENT=" .$gCogCntl->{'IDENT'} . "\n";
}

=head1 SEE ALSO

See http://www.planet-lab.org/ for more information.

=head1 AUTHOR

Mic Bowman, E<lt>mic.bowman@intel.comE<gt>

=cut

package PlanetLab::PLDeploy;

use 5.008;
use strict;
use warnings;

our $AUTOLOAD;

use Cwd qw(abs_path);
use FindBin;
use File::Basename;
use Sys::Hostname;
use File::Temp qw/ :mktemp /;

# Set up for method autoload on a few known fields
my %gAutoFields = (Verbose => undef,
		   Debug => undef,
		   Version => undef,
		   SliceName => undef,
		   SliceRoot => undef,
		   SliceEmail => undef,
		   SliceCntl => undef,
		   SliceInit => undef,
		   NodeName => undef,
		   CogName => undef,
		   CogRoot => undef,
		   CogOutbound => undef,
		   CogArchive => undef,
		   CogTmp => undef);
    
# -----------------------------------------------------------------
# Assumes:
#     * binary is somewhere in a cog
#     * some parent directory contains a .cog file with configuration info
#     * parent of the parent of the cog directory contains a .slice file
# -----------------------------------------------------------------
sub new {
    my $class = shift;
    my $self = ($#_ == 0) ? { %{ (shift) } } : { @_ };

    bless $self, $class;

    # Save for autoload and set all the defaults
    $self->{'_permitted'} = \%gAutoFields;
    foreach my $key (keys %gAutoFields) {
	$self->{$key} = $gAutoFields{$key} unless defined $self->{$key};
    }

    # Some defaults
    $self->{'Verbose'} = 0;
    $self->{'Debug'} = 0;
    $self->{'Version'} = 0;

    # Some slice information
    $self->{'SliceName'} = basename($ENV{'HOME'});
    $self->{'SliceEmail'} = $self->{'SliceName'} . '@slice.planet-lab.org';
    $self->{'SliceRoot'} = $ENV{'HOME'} . "/PL";
    $self->{'SliceCntl'} = $self->{'SliceRoot'} . "/PLServiceCntl";
    $self->{'SliceInit'} = $self->{'SliceRoot'} . "/PLServiceInit";
    $self->{'NodeName'} = hostname;

    # Read slice configuration file in $SliceRoot/config
    my $sconfig = $self->{'SliceRoot'} . "/config";
    $self->ReadConfig($sconfig) if -f $sconfig;
	
    # Absolute path to the directory where the binary resides
    # Used to find out which cog we are in, if we aren't in a
    # cog, then all is ignored
    my $dir = abs_path($FindBin::Bin);
    if ($dir =~ m@$self->{'SliceRoot'}/Cogs/([^/]+)@ ) {
	# Information about the cog
	$self->{'CogName'} = $1;
	$self->{'CogRoot'} = $self->{'SliceRoot'} . "/Cogs/$1";
	$self->{'CogOutbound'} = $self->{'CogRoot'} . "/OUTBOUND";
	$self->{'CogArchive'} = $self->{'CogRoot'} . "/OUTBOUND/ARCHIVE";
	$self->{'CogTmp'} = $self->{'CogRoot'} . "/TMP";

	# Read cog configuration file in $CogRoot/config
	my $cconfig = $self->{'CogRoot'} . "/config";
	$self->ReadConfig($cconfig) if -f $cconfig;

	# Check for a version file for the cog and read the contents
	my $vfile = $self->{'CogRoot'} . "/.version";
	if (-f $vfile) {
	    if (open(VFILE,"<$vfile")) {
		while (<VFILE>) {
		    chomp;
		    next if (/^\s*$/); # all whitespace
		    next if (/^\s*\#/); # comment

		    $self->{'Version'} = $_;
		}
		close(VFILE);
	    }
	}	    
    }

    return $self;
}

# -----------------------------------------------------------------
# NAME: ReadConfig
# DESC: Invocation: ReadConfig("Configfile");
# -----------------------------------------------------------------
sub ReadConfig {
    my $self = shift;
    my $config = shift;

    print "Read config file $config\n"
	if $self->Verbose;

    if (open(CONFIG, "< $config")) {
        my $key;
        my $val;
        while(<CONFIG>) {
            chomp;
	    next if (/^\s*$/); # all whitespace
	    next if (/^\s*\#/); # comment
		 
            ($key, $val) = split(":",$_,2); # just the first :
	    $key =~ s/ //g; # clean up the space around the key
	    $val =~ s/^ *//; # clean up leading white space in the value
	    $self->{$key} = $val;
	}		 
        close CONFIG;
    }
}

# -----------------------------------------------------------------
# Call the system to execute the passed parameter.
# The command is echoed if 'gVerbose' is non-zero.
# Called:
#    &DoSystem($command);
# -----------------------------------------------------------------
sub DoSystem {
    my $self = shift;
    my $cmd = shift;

    print "$cmd\n"
	if $self->Verbose;

    return system($cmd) == 0
	unless $self->Debug;
}

# -----------------------------------------------------------------
# NAME: UpdateCrontab
# DESC: This command updates the crontab entry for a cog without
# destroying other crontab entries. The crontab file is expected
# to be in the following form:
#     # PlanetLab Modifications Start Here
#     # Cog: <key>
#     <cmd>
# -----------------------------------------------------------------
sub UpdateCrontab {
    my $self = shift;
    my ($cmd,$key) = @_;

    # Key defaults to cog name
    $key = $self->{'CogName'} unless defined $key;

    # Always put the separator at the top of the file
    my @lines = ();
    push(@lines,"\# PlanetLab Modifications Start Here\n");
    push(@lines,"MAILTO=" . $self->SliceEmail . "\n");

    # Check the crontab current status
    my $tempfile = mktemp("./LLXXXXXX");
    my $croncmd = "/usr/bin/crontab -l > $tempfile 2> /dev/null";

    if ($self->DoSystem($croncmd)) {
	open(CTOUT,"< $tempfile") ||
	    die "Unable to open crontab output; $!\n";

	# Skip the stuff that is automatically generated
	while (<CTOUT>) {
	    last if /^\# PlanetLab Modifications Start Here/;
	}

	# Now start with the PlanetLab specific stuff, if the crontab
	# was empty, this will just fail and move on (ie it does the
	# right thing)
	while (<CTOUT>) {
	    # Skip the Mailto line if it exists, already added
	    next if /^MAILTO/;

	    # Transfer lines to the new list
	    push(@lines,$_), next unless (/^\# Cog: $key/);

	    # Read the next line and blow it away, then continue copying
	    <CTOUT>;
	}
	
	close(CTOUT);
    }

    # Clean up the temporary file
    $self->DoSystem("/bin/rm -f $tempfile");

    # Add the new command at the end of the file
    if (defined $cmd && ! $cmd eq "") {
	push(@lines,"\# Cog: $key\n");
	push(@lines,"$cmd\n");
    }

    # Write the new crontab entry
    open(NEWCT,"| /usr/bin/crontab -") ||
	die "Unable to open pipe to crontab; $!\n";

    # Copy each line from the old file
    foreach my $line (@lines) {
	print NEWCT $line;
    }

    # Done
    close(NEWCT);
}

# -----------------------------------------------------------------
# 
# -----------------------------------------------------------------
sub AUTOLOAD {
    my $self = shift;

    my $name = $AUTOLOAD;
    $name =~ s/.*://;   # strip fully-qualified portion

    die "Unknown key $name\n" unless exists $self->{_permitted}->{$name};

    if (@_) {
	return $self->{$name} = shift;
    } else {
	return $self->{$name};
    }
}  

# -----------------------------------------------------------------
# 
# -----------------------------------------------------------------
sub DESTROY {
    my $self = shift;

    return;
}

1;
__END__

