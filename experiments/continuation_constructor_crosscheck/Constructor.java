import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

// Project-original constructor under Unknown v0.3. It reads only the declared
// abstract TSV and never reads the Perl constructor or its output directory.
public final class Constructor {
    private static long workUnits = 0;
    private static int filesWritten = 0;

    private record Spec(String caseId, String attemptId, String state,
                        String problemId, long initial, long spent, long remaining) {}

    private static String quote(String value) {
        StringBuilder output = new StringBuilder("\"");
        for (int index = 0; index < value.length(); index++) {
            char character = value.charAt(index);
            switch (character) {
                case '\"' -> output.append("\\\"");
                case '\\' -> output.append("\\\\");
                case '\b' -> output.append("\\b");
                case '\f' -> output.append("\\f");
                case '\n' -> output.append("\\n");
                case '\r' -> output.append("\\r");
                case '\t' -> output.append("\\t");
                default -> {
                    if (character < 0x20 || character > 0x7e) {
                        output.append(String.format("\\u%04x", (int) character));
                    } else {
                        output.append(character);
                    }
                }
            }
        }
        return output.append('\"').toString();
    }

    private static String encode(Object value) {
        if (value instanceof String string) {
            return quote(string);
        }
        if (value instanceof Boolean || value instanceof Integer || value instanceof Long) {
            return value.toString();
        }
        if (value instanceof List<?> list) {
            List<String> encoded = new ArrayList<>();
            for (Object item : list) {
                encoded.add(encode(item));
            }
            return "[" + String.join(",", encoded) + "]";
        }
        if (value instanceof Map<?, ?> map) {
            TreeMap<String, Object> sorted = new TreeMap<>();
            for (Map.Entry<?, ?> entry : map.entrySet()) {
                if (!(entry.getKey() instanceof String key)) {
                    throw new IllegalArgumentException("NonStringKey");
                }
                sorted.put(key, entry.getValue());
            }
            List<String> encoded = new ArrayList<>();
            for (Map.Entry<String, Object> entry : sorted.entrySet()) {
                encoded.add(quote(entry.getKey()) + ":" + encode(entry.getValue()));
            }
            return "{" + String.join(",", encoded) + "}";
        }
        throw new IllegalArgumentException("UnsupportedJsonValue");
    }

    private static byte[] canonical(Object value) {
        byte[] raw = encode(value).getBytes(StandardCharsets.US_ASCII);
        workUnits += raw.length + 1L;
        return raw;
    }

    private static String sha256(byte[] raw) throws NoSuchAlgorithmException {
        workUnits += raw.length + 1L;
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(raw);
        StringBuilder output = new StringBuilder();
        for (byte value : digest) {
            output.append(String.format("%02x", value & 0xff));
        }
        return output.toString();
    }

    private static void writeNew(Path path, byte[] raw) throws IOException {
        Files.createDirectories(path.getParent());
        try (FileChannel channel = FileChannel.open(path, StandardOpenOption.CREATE_NEW,
                                                     StandardOpenOption.WRITE)) {
            ByteBuffer buffer = ByteBuffer.wrap(raw);
            while (buffer.hasRemaining()) {
                channel.write(buffer);
            }
            channel.force(true);
        }
        filesWritten += 1;
    }

    private static Map<String, Object> object(Object... entries) {
        if (entries.length % 2 != 0) {
            throw new IllegalArgumentException("OddObjectEntries");
        }
        Map<String, Object> output = new HashMap<>();
        for (int index = 0; index < entries.length; index += 2) {
            output.put((String) entries[index], entries[index + 1]);
        }
        return output;
    }

    private static List<Spec> readSpecs(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path, StandardCharsets.US_ASCII);
        if (lines.size() != 4 ||
            !lines.get(0).equals("adva.research.continuation-abstract-instances.v0") ||
            !lines.get(1).equals("case_id\tattempt_id\tstate\tproblem_id\tinitial_units\tspent_units\tremaining_units")) {
            throw new IllegalArgumentException("AbstractSpecShape");
        }
        List<Spec> specs = new ArrayList<>();
        Set<String> caseIds = new HashSet<>();
        for (int lineIndex = 2; lineIndex < lines.size(); lineIndex++) {
            String[] fields = lines.get(lineIndex).split("\\t", -1);
            if (fields.length != 7 || !fields[0].matches("[a-z][a-z0-9-]*") ||
                !fields[1].matches("[a-z0-9-]+") ||
                !(fields[2].equals("completed") || fields[2].equals("cancelled")) ||
                !fields[3].matches("[a-z0-9-]+") || !caseIds.add(fields[0])) {
                throw new IllegalArgumentException("AbstractSpecRow");
            }
            long initial = Long.parseLong(fields[4]);
            long spent = Long.parseLong(fields[5]);
            long remaining = Long.parseLong(fields[6]);
            if (initial < 0 || spent < 0 || remaining < 0 || initial != spent + remaining) {
                throw new IllegalArgumentException("AbstractBudget");
            }
            specs.add(new Spec(fields[0], fields[1], fields[2], fields[3],
                               initial, spent, remaining));
        }
        return specs;
    }

    public static void main(String[] arguments) throws Exception {
        Path specPath = null;
        Path output = null;
        for (int index = 0; index < arguments.length; index += 2) {
            if (index + 1 >= arguments.length) {
                throw new IllegalArgumentException("Arguments");
            }
            if (arguments[index].equals("--spec")) {
                specPath = Path.of(arguments[index + 1]).toAbsolutePath();
            } else if (arguments[index].equals("--output")) {
                output = Path.of(arguments[index + 1]).toAbsolutePath();
            } else {
                throw new IllegalArgumentException("Arguments");
            }
        }
        if (specPath == null || output == null || Files.exists(output)) {
            throw new IllegalArgumentException("MissingOrExistingOutput");
        }
        List<Spec> specs = readSpecs(specPath);
        Files.createDirectories(output);
        List<Object> manifestCases = new ArrayList<>();

        for (Spec spec : specs) {
            Path directory = output.resolve(spec.caseId());
            Files.createDirectories(directory);
            String pairDigest = sha256(("pair-coordinate:" + spec.caseId() + ":v0")
                                       .getBytes(StandardCharsets.US_ASCII));
            byte[] pending = canonical(object(
                "profile", "heldout-pending-anchor-v0", "case_id", spec.caseId(),
                "attempt_id", spec.attemptId()));
            byte[] recovery = canonical(object(
                "profile", "heldout-recovery-anchor-v0", "case_id", spec.caseId(),
                "stage", 1L));
            byte[] terminal = canonical(object(
                "profile", "heldout-terminal-anchor-v0", "case_id", spec.caseId(),
                "state", spec.state()));
            String pendingSha = sha256(pending);
            String recoverySha = sha256(recovery);
            String terminalSha = sha256(terminal);

            byte[] resolutionQuery = canonical(object(
                "profile", "terminal-resolution-query-v0",
                "attempt_id", spec.attemptId(), "pair_digest", pairDigest,
                "source_pending_sha256", pendingSha,
                "recovery_receipt_sha256", recoverySha, "terminal_sha256", terminalSha));
            String resolutionQuerySha = sha256(resolutionQuery);
            byte[] resolutionReceipt = canonical(object(
                "profile", "terminal-resolution-receipt-v0",
                "outcome", "ResolutionVerified", "reason", "HeldOutCanonicalAnchorsBound",
                "state", spec.state(), "attempt_id", spec.attemptId(),
                "pair_digest", pairDigest, "source_pending_sha256", pendingSha,
                "recovery_receipt_sha256", recoverySha, "terminal_sha256", terminalSha,
                "archive_mutated", false, "target_processes", 0L,
                "effect_authority", false, "retry_authority", false,
                "refund_authority", false, "mutation_authority", false,
                "native_authority", false, "free_authority", false, "work_units", 0L));
            String resolutionReceiptSha = sha256(resolutionReceipt);

            byte[] continuation = canonical(object(
                "profile", "problem-history-budget-continuation-v0",
                "problem", object(
                    "profile", "terminal-continuation-problem-v0",
                    "problem_id", spec.problemId(), "attempt_id", spec.attemptId(),
                    "pair_digest", pairDigest,
                    "resolution_query_sha256", resolutionQuerySha,
                    "allowed_terminal_states", List.of(spec.state())),
                "history", object(
                    "profile", "continuation-history-v0",
                    "entries", List.of(
                        object("index", 0L, "kind", "terminal-resolution-query",
                               "sha256", resolutionQuerySha),
                        object("index", 1L, "kind", "terminal-resolution-receipt",
                               "sha256", resolutionReceiptSha))),
                "budget", object(
                    "profile", "cumulative-natural-budget-v0",
                    "initial_units", spec.initial(), "spent_units", spec.spent(),
                    "remaining_units", spec.remaining())));
            String continuationSha = sha256(continuation);
            byte[] gateQuery = canonical(object(
                "profile", "continuation-resolution-gate-query-v0",
                "continuation_sha256", continuationSha,
                "resolution_receipt_sha256", resolutionReceiptSha));

            TreeMap<String, byte[]> payloads = new TreeMap<>();
            payloads.put("source-pending.json", pending);
            payloads.put("recovery-receipt.json", recovery);
            payloads.put("terminal.json", terminal);
            payloads.put("resolution-query.json", resolutionQuery);
            payloads.put("resolution-receipt.json", resolutionReceipt);
            payloads.put("continuation.json", continuation);
            payloads.put("gate-query.json", gateQuery);
            Map<String, Object> digests = new TreeMap<>();
            for (Map.Entry<String, byte[]> entry : payloads.entrySet()) {
                writeNew(directory.resolve(entry.getKey()), entry.getValue());
                digests.put(entry.getKey(), sha256(entry.getValue()));
            }
            manifestCases.add(object("case_id", spec.caseId(), "input_sha256", digests));
        }

        Map<String, Object> manifest = object(
            "profile", "adva.research.continuation-java-constructor-manifest.v0",
            "cases", manifestCases, "case_count", (long) specs.size(),
            "abstract_spec_sha256", sha256(Files.readAllBytes(specPath)),
            "receiver_classification_supplied", false,
            "receiver_source_imported", false,
            "perl_output_read", false,
            "files_written_before_manifest", (long) filesWritten,
            "work_units_before_manifest", workUnits);
        writeNew(output.resolve("manifest.json"), canonical(manifest));
        byte[] result = canonical(object(
            "profile", "adva.research.continuation-java-constructor-result.v0",
            "case_count", (long) specs.size(), "files_written", (long) filesWritten,
            "work_units", workUnits, "abstract_spec_sha256", sha256(Files.readAllBytes(specPath)),
            "receiver_classification_supplied", false,
            "receiver_source_imported", false, "perl_output_read", false));
        System.out.write(result);
        System.out.write('\n');
    }
}
