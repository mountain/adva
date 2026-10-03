#!/usr/bin/env node
// Independent Node receiver for the frozen continuation-resolution gate bytes.
// Project-original contribution under Unknown v0.3. ChatGPT (OpenAI), through
// Mingli Yuan's authorized account proxy; not his review or correctness claim.

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

const MAX_BYTES = 16384;
const MAX_WORK = 4000;
let work = 0;

class InvalidEvidence extends Error {}

function tick(n = 1) {
  work += n;
  if (work > MAX_WORK) throw new InvalidEvidence("WorkLimit");
}

function asciiString(value) {
  return JSON.stringify(value).replace(/[\u0080-\uffff]/g, (character) =>
    `\\u${character.charCodeAt(0).toString(16).padStart(4, "0")}`);
}

function canonical(value) {
  tick();
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value)) throw new InvalidEvidence("UnsafeNumber");
    return String(value);
  }
  if (typeof value === "string") return asciiString(value);
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) =>
      `${asciiString(key)}:${canonical(value[key])}`).join(",")}}`;
  }
  throw new InvalidEvidence("UnsupportedJsonValue");
}

function sha(raw) {
  tick();
  return createHash("sha256").update(raw).digest("hex");
}

function exactFields(value, wanted, label) {
  tick();
  if (value === null || Array.isArray(value) || typeof value !== "object") {
    throw new InvalidEvidence(`${label}:Object`);
  }
  const actual = Object.keys(value).sort();
  const expected = [...wanted].sort();
  if (canonical(actual) !== canonical(expected)) {
    throw new InvalidEvidence(`${label}:Fields`);
  }
}

function hex64(value, label) {
  tick();
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) {
    throw new InvalidEvidence(`${label}:Digest`);
  }
}

function natural(value, label) {
  tick();
  if (!Number.isSafeInteger(value) || value < 0) {
    throw new InvalidEvidence(`${label}:Natural`);
  }
}

function readCanonical(path, label) {
  const raw = readFileSync(path);
  tick(raw.length + 1);
  if (raw.length > MAX_BYTES) throw new InvalidEvidence(`${label}:InputTooLarge`);
  let value;
  try {
    value = JSON.parse(raw.toString("utf8"));
  } catch {
    throw new InvalidEvidence(`${label}:Json`);
  }
  if (Buffer.from(canonical(value), "utf8").compare(raw) !== 0) {
    throw new InvalidEvidence(`${label}:NonCanonicalJson`);
  }
  return { value, raw };
}

function validateQuery(value) {
  exactFields(value, ["profile", "continuation_sha256", "resolution_receipt_sha256"], "Query");
  if (value.profile !== "continuation-resolution-gate-query-v0") {
    throw new InvalidEvidence("Query:Profile");
  }
  hex64(value.continuation_sha256, "Query:Continuation");
  hex64(value.resolution_receipt_sha256, "Query:Resolution");
}

function validateContinuation(value) {
  exactFields(value, ["profile", "problem", "history", "budget"], "Tuple");
  if (value.profile !== "problem-history-budget-continuation-v0") {
    throw new InvalidEvidence("Tuple:Profile");
  }
  const problem = value.problem;
  exactFields(problem, ["profile", "problem_id", "attempt_id", "pair_digest",
    "resolution_query_sha256", "allowed_terminal_states"], "Problem");
  if (problem.profile !== "terminal-continuation-problem-v0") {
    throw new InvalidEvidence("Problem:Profile");
  }
  for (const key of ["problem_id", "attempt_id"]) {
    tick();
    if (typeof problem[key] !== "string" || problem[key].length === 0) {
      throw new InvalidEvidence(`Problem:${key}`);
    }
  }
  hex64(problem.pair_digest, "Problem:Pair");
  hex64(problem.resolution_query_sha256, "Problem:ResolutionQuery");
  const states = problem.allowed_terminal_states;
  tick();
  if (!Array.isArray(states) || states.length === 0 || new Set(states).size !== states.length ||
      states.some((state) => state !== "completed" && state !== "cancelled")) {
    throw new InvalidEvidence("Problem:States");
  }

  const history = value.history;
  exactFields(history, ["profile", "entries"], "History");
  if (history.profile !== "continuation-history-v0" || !Array.isArray(history.entries) ||
      history.entries.length !== 2) throw new InvalidEvidence("History:Shape");
  const kinds = ["terminal-resolution-query", "terminal-resolution-receipt"];
  history.entries.forEach((entry, index) => {
    exactFields(entry, ["index", "kind", "sha256"], `History:${index}`);
    if (entry.index !== index || entry.kind !== kinds[index]) {
      throw new InvalidEvidence(`History:${index}:Coordinate`);
    }
    hex64(entry.sha256, `History:${index}`);
  });
  if (history.entries[0].sha256 !== problem.resolution_query_sha256) {
    throw new InvalidEvidence("History:ProblemDivergence");
  }

  const budget = value.budget;
  exactFields(budget, ["profile", "initial_units", "spent_units", "remaining_units"], "Budget");
  if (budget.profile !== "cumulative-natural-budget-v0") {
    throw new InvalidEvidence("Budget:Profile");
  }
  for (const key of ["initial_units", "spent_units", "remaining_units"]) {
    natural(budget[key], `Budget:${key}`);
  }
  if (budget.initial_units !== budget.spent_units + budget.remaining_units) {
    throw new InvalidEvidence("Budget:Equation");
  }
}

function validateResolution(value) {
  const fields = ["profile", "outcome", "reason", "state", "attempt_id", "pair_digest",
    "source_pending_sha256", "recovery_receipt_sha256", "terminal_sha256",
    "archive_mutated", "target_processes", "effect_authority", "retry_authority",
    "refund_authority", "mutation_authority", "native_authority", "free_authority",
    "work_units"];
  exactFields(value, fields, "Resolution");
  if (value.profile !== "terminal-resolution-receipt-v0" ||
      !["ResolutionVerified", "UnknownResolutionState", "InvalidEvidence"].includes(value.outcome)) {
    throw new InvalidEvidence("Resolution:ProfileOrOutcome");
  }
  if (typeof value.reason !== "string" || value.reason.length === 0 ||
      value.archive_mutated !== false || value.target_processes !== 0) {
    throw new InvalidEvidence("Resolution:Boundary");
  }
  for (const key of ["effect_authority", "retry_authority", "refund_authority",
    "mutation_authority", "native_authority", "free_authority"]) {
    if (value[key] !== false) throw new InvalidEvidence(`Resolution:${key}`);
  }
  natural(value.work_units, "Resolution:Work");
  const digests = ["pair_digest", "source_pending_sha256", "recovery_receipt_sha256", "terminal_sha256"];
  for (const key of digests) if (value[key] !== null) hex64(value[key], `Resolution:${key}`);
  if (value.attempt_id !== null && (typeof value.attempt_id !== "string" || value.attempt_id.length === 0)) {
    throw new InvalidEvidence("Resolution:Attempt");
  }
  if (value.state !== null && value.state !== "completed" && value.state !== "cancelled") {
    throw new InvalidEvidence("Resolution:State");
  }
  if (value.outcome === "ResolutionVerified") {
    if (!value.attempt_id || !["completed", "cancelled"].includes(value.state)) {
      throw new InvalidEvidence("Resolution:VerifiedCoordinate");
    }
    for (const key of digests) hex64(value[key], `Resolution:Verified:${key}`);
  }
}

function response(outcome, reason, continuation = null, continuationSha = null,
                  resolutionSha = null, state = null) {
  return {
    profile: "continuation-resolution-gate-receipt-v0", outcome, reason, state,
    continuation_sha256: continuationSha,
    resolution_receipt_sha256: resolutionSha,
    preserved_continuation: continuation,
    continuation_ready: outcome === "ContinuationReady",
    fuel_delta: 0, input_mutated: false, target_processes: 0,
    effect_authority: false, retry_authority: false, refund_authority: false,
    mutation_authority: false, native_authority: false, free_authority: false,
    work_units: work,
  };
}

function receive(queryPath, continuationPath, resolutionPath) {
  const queryRead = readCanonical(queryPath, "Query");
  validateQuery(queryRead.value);
  const continuationRead = readCanonical(continuationPath, "Continuation");
  validateContinuation(continuationRead.value);
  const continuationSha = sha(continuationRead.raw);

  let resolutionRead;
  try {
    resolutionRead = readCanonical(resolutionPath, "Resolution");
    validateResolution(resolutionRead.value);
  } catch (error) {
    if (!(error instanceof InvalidEvidence) && error?.code === undefined) throw error;
    return response("InvalidEvidence", `InvalidEvidence:${error.message}`,
      continuationRead.value, continuationSha);
  }
  const resolutionSha = sha(resolutionRead.raw);
  const query = queryRead.value;
  const continuation = continuationRead.value;
  const resolution = resolutionRead.value;
  if (continuationSha !== query.continuation_sha256 ||
      resolutionSha !== query.resolution_receipt_sha256) {
    return response("UnknownContinuationState", "GateQueryDigestDivergence",
      continuation, continuationSha, resolutionSha);
  }
  if (continuation.history.entries[1].sha256 !== resolutionSha) {
    return response("UnknownContinuationState", "HistoryReceiptDivergence",
      continuation, continuationSha, resolutionSha);
  }
  if (resolution.outcome === "InvalidEvidence") {
    return response("InvalidEvidence", "ParentResolutionInvalid",
      continuation, continuationSha, resolutionSha);
  }
  if (resolution.outcome === "UnknownResolutionState") {
    return response("UnknownContinuationState", "ParentResolutionUnknown",
      continuation, continuationSha, resolutionSha);
  }
  const problem = continuation.problem;
  if (problem.attempt_id !== resolution.attempt_id ||
      problem.pair_digest !== resolution.pair_digest ||
      !problem.allowed_terminal_states.includes(resolution.state)) {
    return response("UnknownContinuationState", "ProblemResolutionDivergence",
      continuation, continuationSha, resolutionSha, resolution.state);
  }
  return response("ContinuationReady", "ExactTupleAndResolutionBound",
    continuation, continuationSha, resolutionSha, resolution.state);
}

function argumentsByName(argv) {
  const result = Object.create(null);
  for (let index = 2; index < argv.length; index += 2) {
    if (!argv[index]?.startsWith("--") || argv[index + 1] === undefined) {
      throw new Error("Arguments");
    }
    result[argv[index].slice(2)] = argv[index + 1];
  }
  return result;
}

const args = argumentsByName(process.argv);
let continuationSha = null;
let result;
try {
  try { continuationSha = sha(readFileSync(args.continuation)); } catch {}
  result = receive(args.query, args.continuation, args["resolution-receipt"]);
} catch (error) {
  result = response("InvalidEvidence", `${error.constructor.name}:${error.message}`,
    null, continuationSha);
}
process.stdout.write(`${canonical(result)}\n`);
