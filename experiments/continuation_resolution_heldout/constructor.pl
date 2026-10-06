#!/usr/bin/env perl
use strict;
use warnings;

use Digest::SHA qw(sha256_hex);
use Fcntl qw(:DEFAULT);
use File::Path qw(make_path);
use IO::Handle;
use JSON::PP;

# Project-original held-out byte constructor under Unknown v0.3.
# It does not import either receiver and emits no expected gate classification.

my $output;
for (my $index = 0; $index < @ARGV; $index += 2) {
    die "Arguments\n" if !defined($ARGV[$index + 1]) || $ARGV[$index] ne '--output';
    $output = $ARGV[$index + 1];
}
die "MissingOutput\n" if !defined($output) || $output eq '';
die "OutputExists\n" if -e $output;
make_path($output) or die "MakeOutput:$!\n";

my $json = JSON::PP->new->canonical(1)->ascii(1)->allow_nonref(1);
my $work = 0;
my $files = 0;

sub canonical {
    my ($value) = @_;
    my $raw = $json->encode($value);
    $work += length($raw) + 1;
    return $raw;
}

sub digest_bytes {
    my ($raw) = @_;
    $work += length($raw) + 1;
    return sha256_hex($raw);
}

sub write_new {
    my ($path, $raw) = @_;
    sysopen(my $stream, $path, O_WRONLY | O_CREAT | O_EXCL, 0644)
        or die "WriteNew:$path:$!\n";
    print {$stream} $raw or die "Write:$path:$!\n";
    $stream->flush() or die "Flush:$path:$!\n";
    $stream->sync() or die "Sync:$path:$!\n";
    close($stream) or die "Close:$path:$!\n";
    $files += 1;
}

my @specifications = (
    {
        case_id => 'rho', attempt_id => 'heldout-rho-01', state => 'completed',
        problem_id => 'heldout-continuation-rho', initial => 31, spent => 19,
        remaining => 12,
    },
    {
        case_id => 'tau', attempt_id => 'heldout-tau-02', state => 'cancelled',
        problem_id => 'heldout-continuation-tau', initial => 37, spent => 21,
        remaining => 16,
    },
);

my @manifest_cases;
for my $spec (@specifications) {
    my $directory = "$output/$spec->{case_id}";
    make_path($directory) or die "MakeCase:$!\n";

    my $pair_digest = digest_bytes("pair-coordinate:$spec->{case_id}:v0");
    my $pending_raw = canonical({
        profile => 'heldout-pending-anchor-v0',
        case_id => $spec->{case_id},
        attempt_id => $spec->{attempt_id},
    });
    my $recovery_raw = canonical({
        profile => 'heldout-recovery-anchor-v0',
        case_id => $spec->{case_id},
        stage => 1,
    });
    my $terminal_raw = canonical({
        profile => 'heldout-terminal-anchor-v0',
        case_id => $spec->{case_id},
        state => $spec->{state},
    });
    my $pending_sha = digest_bytes($pending_raw);
    my $recovery_sha = digest_bytes($recovery_raw);
    my $terminal_sha = digest_bytes($terminal_raw);

    my $resolution_query_raw = canonical({
        profile => 'terminal-resolution-query-v0',
        attempt_id => $spec->{attempt_id},
        pair_digest => $pair_digest,
        source_pending_sha256 => $pending_sha,
        recovery_receipt_sha256 => $recovery_sha,
        terminal_sha256 => $terminal_sha,
    });
    my $resolution_query_sha = digest_bytes($resolution_query_raw);
    my $resolution_receipt_raw = canonical({
        profile => 'terminal-resolution-receipt-v0',
        outcome => 'ResolutionVerified',
        reason => 'HeldOutCanonicalAnchorsBound',
        state => $spec->{state},
        attempt_id => $spec->{attempt_id},
        pair_digest => $pair_digest,
        source_pending_sha256 => $pending_sha,
        recovery_receipt_sha256 => $recovery_sha,
        terminal_sha256 => $terminal_sha,
        archive_mutated => JSON::PP::false,
        target_processes => 0,
        effect_authority => JSON::PP::false,
        retry_authority => JSON::PP::false,
        refund_authority => JSON::PP::false,
        mutation_authority => JSON::PP::false,
        native_authority => JSON::PP::false,
        free_authority => JSON::PP::false,
        work_units => 0,
    });
    my $resolution_receipt_sha = digest_bytes($resolution_receipt_raw);

    my $continuation_raw = canonical({
        profile => 'problem-history-budget-continuation-v0',
        problem => {
            profile => 'terminal-continuation-problem-v0',
            problem_id => $spec->{problem_id},
            attempt_id => $spec->{attempt_id},
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
            initial_units => $spec->{initial},
            spent_units => $spec->{spent},
            remaining_units => $spec->{remaining},
        },
    });
    my $continuation_sha = digest_bytes($continuation_raw);
    my $gate_query_raw = canonical({
        profile => 'continuation-resolution-gate-query-v0',
        continuation_sha256 => $continuation_sha,
        resolution_receipt_sha256 => $resolution_receipt_sha,
    });

    my %payloads = (
        'source-pending.json' => $pending_raw,
        'recovery-receipt.json' => $recovery_raw,
        'terminal.json' => $terminal_raw,
        'resolution-query.json' => $resolution_query_raw,
        'resolution-receipt.json' => $resolution_receipt_raw,
        'continuation.json' => $continuation_raw,
        'gate-query.json' => $gate_query_raw,
    );
    my %digests;
    for my $name (sort keys %payloads) {
        write_new("$directory/$name", $payloads{$name});
        $digests{$name} = digest_bytes($payloads{$name});
    }
    push @manifest_cases, {
        case_id => $spec->{case_id},
        input_sha256 => \%digests,
    };
}

my $manifest = {
    profile => 'adva.research.continuation-heldout.constructor-manifest.v0',
    cases => \@manifest_cases,
    case_count => scalar(@manifest_cases),
    receiver_classification_supplied => JSON::PP::false,
    receiver_source_imported => JSON::PP::false,
    files_written_before_manifest => $files,
    work_units_before_manifest => $work,
};
write_new("$output/manifest.json", canonical($manifest));
print canonical({
    profile => 'adva.research.continuation-heldout.constructor-result.v0',
    case_count => scalar(@manifest_cases),
    files_written => $files,
    work_units => $work,
    receiver_classification_supplied => JSON::PP::false,
    receiver_source_imported => JSON::PP::false,
}), "\n";
