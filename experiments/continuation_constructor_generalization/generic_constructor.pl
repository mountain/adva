#!/usr/bin/env perl
use strict;
use warnings;
use Digest::SHA qw(sha256_hex);
use Encode qw(encode);
use File::Path qw(make_path);
use File::Spec;
use Fcntl qw(:DEFAULT);
use JSON::PP;

# Project-original generic constructor under Unknown v0.3. It consumes only
# the declared abstract TSV and contains no instance vocabulary.

my ($spec_path, $output);
while (@ARGV) {
    my $flag = shift @ARGV;
    my $value = shift @ARGV;
    die "Arguments\n" unless defined $value;
    if ($flag eq '--spec') {
        $spec_path = $value;
    } elsif ($flag eq '--output') {
        $output = $value;
    } else {
        die "Arguments\n";
    }
}
die "MissingArguments\n" unless defined $spec_path && defined $output;
die "ExistingOutput\n" if -e $output;

my $json = JSON::PP->new->ascii(1)->canonical(1);
my $work_units = 0;
my $files_written = 0;

sub canonical {
    my ($value) = @_;
    my $raw = encode('ASCII', $json->encode($value));
    $work_units += length($raw) + 1;
    return $raw;
}

sub digest {
    my ($raw) = @_;
    $work_units += length($raw) + 1;
    return sha256_hex($raw);
}

sub slurp_raw {
    my ($path) = @_;
    sysopen(my $fh, $path, O_RDONLY) or die "Read:$path:$!\n";
    binmode($fh);
    local $/;
    my $raw = <$fh>;
    close($fh) or die "Close:$path:$!\n";
    return $raw;
}

sub write_new {
    my ($path, $raw) = @_;
    my (undef, $directory) = File::Spec->splitpath($path);
    make_path($directory) unless -d $directory;
    sysopen(my $fh, $path, O_WRONLY | O_CREAT | O_EXCL) or die "Write:$path:$!\n";
    binmode($fh);
    print {$fh} $raw or die "Print:$path:$!\n";
    close($fh) or die "Close:$path:$!\n";
    $files_written += 1;
}

my $spec_raw = slurp_raw($spec_path);
die "NonAsciiSpec\n" if $spec_raw =~ /[^\x00-\x7f]/;
my @lines = split(/\n/, $spec_raw, -1);
pop @lines if @lines && $lines[-1] eq '';
die "AbstractSpecShape\n"
    unless @lines >= 3
        && $lines[0] eq 'adva.research.continuation-abstract-instances.v0'
        && $lines[1] eq join("\t", qw(case_id attempt_id state problem_id initial_units spent_units remaining_units));

my @specs;
my %seen;
for my $index (2 .. $#lines) {
    my @fields = split(/\t/, $lines[$index], -1);
    die "AbstractSpecRow\n"
        unless @fields == 7
            && $fields[0] =~ /\A[a-z][a-z0-9-]*\z/
            && $fields[1] =~ /\A[a-z0-9-]+\z/
            && ($fields[2] eq 'completed' || $fields[2] eq 'cancelled')
            && $fields[3] =~ /\A[a-z0-9-]+\z/
            && !$seen{$fields[0]}++;
    for my $position (4 .. 6) {
        die "AbstractBudget\n" unless $fields[$position] =~ /\A(?:0|[1-9][0-9]*)\z/;
    }
    my ($initial, $spent, $remaining) = @fields[4 .. 6];
    die "AbstractBudget\n" unless $initial == $spent + $remaining;
    push @specs, {
        case_id => $fields[0], attempt_id => $fields[1], state => $fields[2],
        problem_id => $fields[3], initial => 0 + $initial, spent => 0 + $spent,
        remaining => 0 + $remaining,
    };
}

make_path($output);
my @manifest_cases;
for my $spec (@specs) {
    my $case_id = $spec->{case_id};
    my $directory = File::Spec->catdir($output, $case_id);
    make_path($directory);
    my $pair_digest = digest(encode('ASCII', "pair-coordinate:$case_id:v0"));
    my $pending = canonical({
        profile => 'heldout-pending-anchor-v0', case_id => $case_id,
        attempt_id => $spec->{attempt_id},
    });
    my $recovery = canonical({
        profile => 'heldout-recovery-anchor-v0', case_id => $case_id, stage => 1,
    });
    my $terminal = canonical({
        profile => 'heldout-terminal-anchor-v0', case_id => $case_id,
        state => $spec->{state},
    });
    my $pending_sha = digest($pending);
    my $recovery_sha = digest($recovery);
    my $terminal_sha = digest($terminal);
    my $resolution_query = canonical({
        profile => 'terminal-resolution-query-v0',
        attempt_id => $spec->{attempt_id}, pair_digest => $pair_digest,
        source_pending_sha256 => $pending_sha,
        recovery_receipt_sha256 => $recovery_sha, terminal_sha256 => $terminal_sha,
    });
    my $resolution_query_sha = digest($resolution_query);
    my $resolution_receipt = canonical({
        profile => 'terminal-resolution-receipt-v0',
        outcome => 'ResolutionVerified', reason => 'HeldOutCanonicalAnchorsBound',
        state => $spec->{state}, attempt_id => $spec->{attempt_id},
        pair_digest => $pair_digest, source_pending_sha256 => $pending_sha,
        recovery_receipt_sha256 => $recovery_sha, terminal_sha256 => $terminal_sha,
        archive_mutated => JSON::PP::false, target_processes => 0,
        effect_authority => JSON::PP::false, retry_authority => JSON::PP::false,
        refund_authority => JSON::PP::false, mutation_authority => JSON::PP::false,
        native_authority => JSON::PP::false, free_authority => JSON::PP::false,
        work_units => 0,
    });
    my $resolution_receipt_sha = digest($resolution_receipt);
    my $continuation = canonical({
        profile => 'problem-history-budget-continuation-v0',
        problem => {
            profile => 'terminal-continuation-problem-v0',
            problem_id => $spec->{problem_id}, attempt_id => $spec->{attempt_id},
            pair_digest => $pair_digest,
            resolution_query_sha256 => $resolution_query_sha,
            allowed_terminal_states => [$spec->{state}],
        },
        history => {
            profile => 'continuation-history-v0',
            entries => [
                {index => 0, kind => 'terminal-resolution-query',
                 sha256 => $resolution_query_sha},
                {index => 1, kind => 'terminal-resolution-receipt',
                 sha256 => $resolution_receipt_sha},
            ],
        },
        budget => {
            profile => 'cumulative-natural-budget-v0',
            initial_units => $spec->{initial}, spent_units => $spec->{spent},
            remaining_units => $spec->{remaining},
        },
    });
    my $continuation_sha = digest($continuation);
    my $gate_query = canonical({
        profile => 'continuation-resolution-gate-query-v0',
        continuation_sha256 => $continuation_sha,
        resolution_receipt_sha256 => $resolution_receipt_sha,
    });
    my %payloads = (
        'source-pending.json' => $pending,
        'recovery-receipt.json' => $recovery,
        'terminal.json' => $terminal,
        'resolution-query.json' => $resolution_query,
        'resolution-receipt.json' => $resolution_receipt,
        'continuation.json' => $continuation,
        'gate-query.json' => $gate_query,
    );
    my %digests;
    for my $name (sort keys %payloads) {
        write_new(File::Spec->catfile($directory, $name), $payloads{$name});
        $digests{$name} = digest($payloads{$name});
    }
    push @manifest_cases, {case_id => $case_id, input_sha256 => \%digests};
}

my $manifest = canonical({
    profile => 'adva.research.generic-continuation-perl-constructor-manifest.v0',
    cases => \@manifest_cases, case_count => scalar(@specs),
    abstract_spec_sha256 => digest($spec_raw),
    receiver_classification_supplied => JSON::PP::false,
    receiver_source_imported => JSON::PP::false,
    peer_output_read => JSON::PP::false,
    files_written_before_manifest => $files_written,
    work_units_before_manifest => $work_units,
});
write_new(File::Spec->catfile($output, 'manifest.json'), $manifest);
my $result = canonical({
    profile => 'adva.research.generic-continuation-perl-constructor-result.v0',
    case_count => scalar(@specs), files_written => $files_written,
    work_units => $work_units, abstract_spec_sha256 => digest($spec_raw),
    receiver_classification_supplied => JSON::PP::false,
    receiver_source_imported => JSON::PP::false, peer_output_read => JSON::PP::false,
});
print $result, "\n";
