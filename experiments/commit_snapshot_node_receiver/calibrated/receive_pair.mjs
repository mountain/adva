#!/usr/bin/env node
// Read two pinned commit snapshots without Python, SQLite, or external packages.
// Project-original contribution under Unknown v0.3. ChatGPT (OpenAI), through
// Mingli Yuan's authorized account proxy; not his review or correctness claim.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { performance } from "node:perf_hooks";

const PROFILE = "adva.research.commit-snapshot-pair-receive-node.v1";
const REQUEST_PROFILE = "adva.research.commit-snapshot-pair-receive.v0";
const SNAPSHOT_PROFILE = "adva.research.commit-snapshot.v0";
const SOURCE_PROFILE = "adva.research.decision-ledger-contention.v0";
const MAX_WIRE = 262144;
const MAX_DEPTH = 128;
const MAX_WORK = 15360;
const DELTA = [
  "complete saved two-step prefix independently rechecked",
  "pending third step checked at the same complete endpoint",
  "all four history entries retained without capacity increase",
  "one abstract attempt debit checked without external consumption",
];
let work = 0;
const meter = {value_nodes: 0, checks: 0, decoded: Object.create(null)};

function tick(count = 1, category = "checks") {
  meter[category] += count;
  work += count;
  if (work > MAX_WORK) throw new Error("receiver:work-limit");
}

class StrictJsonParser {
  constructor(text, label) {
    this.text = text;
    this.label = label;
    this.index = 0;
    this.nodes = 0;
    this.keys = 0;
    this.containers = 0;
    this.commas = 0;
  }

  fail(reason) {
    throw new Error(`${this.label}:${reason}@${this.index}`);
  }

  whitespace() {
    while (this.index < this.text.length && " \n\r\t".includes(this.text[this.index])) {
      this.index += 1;
    }
  }

  parse() {
    this.whitespace();
    const value = this.value(0);
    this.whitespace();
    if (this.index !== this.text.length) this.fail("trailing-data");
    return value;
  }

  value(depth) {
    tick(1, "value_nodes");
    this.nodes += 1;
    if (depth > MAX_DEPTH) this.fail("depth-limit");
    this.whitespace();
    const c = this.text[this.index];
    if (c === "{") return this.object(depth + 1);
    if (c === "[") return this.array(depth + 1);
    if (c === "\"") return this.string();
    if (c === "-" || (c >= "0" && c <= "9")) return this.integer();
    for (const [word, value] of [["true", true], ["false", false], ["null", null]]) {
      if (this.text.startsWith(word, this.index)) {
        this.index += word.length;
        return value;
      }
    }
    this.fail("value");
  }

  string() {
    const start = this.index;
    this.index += 1;
    let escaped = false;
    while (this.index < this.text.length) {
      const code = this.text.charCodeAt(this.index);
      const c = this.text[this.index];
      if (!escaped && c === "\"") {
        this.index += 1;
        let value;
        try {
          value = JSON.parse(this.text.slice(start, this.index));
        } catch {
          this.fail("string");
        }
        for (const character of value) {
          if (character.codePointAt(0) > 0x7f) this.fail("non-ascii-string");
        }
        return value;
      }
      if (!escaped && code < 0x20) this.fail("string-control");
      if (!escaped && c === "\\") escaped = true;
      else escaped = false;
      this.index += 1;
    }
    this.fail("unterminated-string");
  }

  integer() {
    const start = this.index;
    if (this.text[this.index] === "-") this.index += 1;
    if (this.text[this.index] === "0") {
      this.index += 1;
      if (/[0-9]/.test(this.text[this.index] ?? "")) this.fail("leading-zero");
    } else {
      if (!/[1-9]/.test(this.text[this.index] ?? "")) this.fail("integer");
      while (/[0-9]/.test(this.text[this.index] ?? "")) this.index += 1;
    }
    if (".eE".includes(this.text[this.index] ?? "")) this.fail("non-integer-number");
    const raw = this.text.slice(start, this.index);
    const value = Number(raw);
    if (!Number.isSafeInteger(value)) this.fail("unsafe-integer");
    return value;
  }

  array(depth) {
    this.containers += 1;
    const result = [];
    this.index += 1;
    this.whitespace();
    if (this.text[this.index] === "]") {
      this.index += 1;
      return result;
    }
    while (true) {
      result.push(this.value(depth));
      this.whitespace();
      if (this.text[this.index] === "]") {
        this.index += 1;
        return result;
      }
      if (this.text[this.index] !== ",") this.fail("array-separator");
      this.commas += 1;
      this.index += 1;
    }
  }

  object(depth) {
    this.containers += 1;
    const result = Object.create(null);
    const seen = new Set();
    this.index += 1;
    this.whitespace();
    if (this.text[this.index] === "}") {
      this.index += 1;
      return result;
    }
    while (true) {
      this.whitespace();
      if (this.text[this.index] !== "\"") this.fail("object-key");
      const key = this.string();
      this.keys += 1;
      if (seen.has(key)) this.fail("duplicate-key");
      seen.add(key);
      this.whitespace();
      if (this.text[this.index] !== ":") this.fail("object-colon");
      this.index += 1;
      result[key] = this.value(depth);
      this.whitespace();
      if (this.text[this.index] === "}") {
        this.index += 1;
        return result;
      }
      if (this.text[this.index] !== ",") this.fail("object-separator");
      this.commas += 1;
      this.index += 1;
    }
  }
}

function decode(buffer, label) {
  if (buffer.length > MAX_WIRE) throw new Error(`${label}:wire-byte-limit`);
  let text;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(buffer);
  } catch {
    throw new Error(`${label}:invalid-utf8`);
  }
  const parser = new StrictJsonParser(text, label);
  const value = parser.parse();
  if (Object.hasOwn(meter.decoded, label)) throw new Error("meter:duplicate-role");
  meter.decoded[label] = {
    bytes: buffer.length, blocks64: Math.ceil(buffer.length / 64),
    value_nodes: parser.nodes, keys: parser.keys,
    lexical_tokens: parser.nodes + 2 * parser.keys + parser.containers + parser.commas,
  };
  return value;
}

function canonical(value) {
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value)) throw new Error("canonical:unsafe-integer");
    return String(value);
  }
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  }
  throw new Error("canonical:unsupported-value");
}

function sha(buffer) {
  tick();
  return createHash("sha256").update(buffer).digest("hex");
}

function equal(left, right) {
  return canonical(left) === canonical(right);
}

function exactFields(value, fields, label) {
  tick();
  if (value === null || Array.isArray(value) || typeof value !== "object") {
    throw new Error(`${label}:fields`);
  }
  const actual = Object.keys(value).sort();
  const wanted = [...fields].sort();
  if (!equal(actual, wanted)) throw new Error(`${label}:fields`);
}

function hexDigest(value, label) {
  tick();
  if (typeof value !== "string" || !/^[0-9a-f]{64}$/.test(value)) {
    throw new Error(`${label}:sha256`);
  }
}

function balance(value, label) {
  exactFields(value, ["grant", "spent", "remaining"], label);
  tick(3);
  if (![value.grant, value.spent, value.remaining].every(Number.isSafeInteger)) {
    throw new Error(`${label}:integer`);
  }
  if (!(value.grant >= 1 && value.grant <= 4 && value.spent >= 0 && value.spent <= value.grant)) {
    throw new Error(`${label}:range`);
  }
  if (value.remaining !== value.grant - value.spent) throw new Error(`${label}:balance`);
}

function readSnapshot(path, pin, label) {
  hexDigest(pin, `${label}:pin`);
  const raw = readFileSync(path);
  if (sha(raw) !== pin) throw new Error(`${label}:file-pin`);
  const snapshot = decode(raw, label);
  const expectedRaw = Buffer.from(`${canonical(snapshot)}\n`, "utf8");
  if (!raw.equals(expectedRaw)) throw new Error(`${label}:noncanonical-file`);
  exactFields(snapshot, ["profile", "version", "body", "body_sha256"], label);
  if (snapshot.profile !== SNAPSHOT_PROFILE || snapshot.version !== 0) {
    throw new Error(`${label}:profile-or-version`);
  }
  hexDigest(snapshot.body_sha256, `${label}:body`);
  const body = snapshot.body;
  if (sha(Buffer.from(canonical(body), "utf8")) !== snapshot.body_sha256) {
    throw new Error(`${label}:body-digest`);
  }
  exactFields(body, ["source_profile", "source_ledger_sha256", "expected_request", "candidate",
    "checker_fingerprint", "allowance", "snapshot_state", "transition",
    "builder_source_sha256"], `${label}:body`);
  if (body.source_profile !== SOURCE_PROFILE) throw new Error(`${label}:source-profile`);
  hexDigest(body.source_ledger_sha256, `${label}:source-ledger`);
  for (const name of ["checker_fingerprint", "builder_source_sha256"]) {
    const mapping = body[name];
    if (mapping === null || Array.isArray(mapping) || typeof mapping !== "object" || Object.keys(mapping).length === 0) {
      throw new Error(`${label}:${name}`);
    }
    for (const [key, digest] of Object.entries(mapping)) {
      if (!key) throw new Error(`${label}:${name}:key`);
      hexDigest(digest, `${label}:${name}`);
    }
  }
  return body;
}

function projection(body) {
  const result = Object.create(null);
  for (const key of Object.keys(body)) {
    if (key !== "builder_source_sha256") result[key] = body[key];
  }
  return result;
}

function validateProjection(body, expected, candidate) {
  if (body.source_profile !== SOURCE_PROFILE) throw new Error("projection:source-profile");
  if (!equal(body.expected_request, expected)) throw new Error("projection:expected-binding");
  if (!equal(body.candidate, candidate)) throw new Error("projection:candidate-binding");
  exactFields(candidate, ["profile", "transition_key", "checkpoint_receipt"], "candidate");
  if (candidate.profile !== SOURCE_PROFILE || typeof candidate.transition_key !== "string") {
    throw new Error("candidate:profile-or-key");
  }
  const allowance = body.allowance;
  balance(allowance, "allowance");
  const initial = expected !== null && typeof expected === "object" && !Array.isArray(expected)
    ? expected.allowance : null;
  balance(initial, "initial-allowance");
  if (body.snapshot_state === "empty") {
    if (body.transition !== null || !equal(allowance, initial)) {
      throw new Error("empty:transition-or-allowance");
    }
    return { outcome: "ProvenUncommittedLedger", state: "empty", allowance, storedResult: null };
  }
  if (body.snapshot_state !== "committed") throw new Error("projection:snapshot-state");
  const transition = body.transition;
  exactFields(transition, ["transition_key", "payload", "stored_result"], "transition");
  if (transition.transition_key !== candidate.transition_key || !equal(transition.payload, candidate)) {
    throw new Error("transition:binding");
  }
  const result = transition.stored_result;
  exactFields(result, ["outcome", "reason", "checkpoint_retained", "allowance_after", "semantic_delta"], "result");
  if (initial.remaining <= 0) throw new Error("committed:initial-allowance");
  const after = Object.assign(Object.create(null), {
    grant: initial.grant,
    spent: initial.spent + 1,
    remaining: initial.remaining - 1,
  });
  if (!equal(after, allowance) || !equal(result.allowance_after, after)) {
    throw new Error("committed:allowance");
  }
  if (result.outcome !== "AcceptedCheckpointContinuation" || result.reason !== "prefix-and-declared-next-step-checked") {
    throw new Error("result:scope");
  }
  if (!equal(result.semantic_delta, DELTA)) throw new Error("result:delta");
  const receipt = candidate.checkpoint_receipt;
  if (receipt === null || typeof receipt !== "object" || Array.isArray(receipt)
      || !equal(result.checkpoint_retained, receipt.checkpoint)) {
    throw new Error("result:checkpoint-binding");
  }
  if (!equal(receipt.allowance_after, after)) throw new Error("candidate:allowance-binding");
  return { outcome: "StoredCommitted", state: "committed", allowance, storedResult: result };
}

function argumentsOf(argv) {
  const result = Object.create(null);
  for (let i = 0; i < argv.length; i += 2) {
    if (!argv[i]?.startsWith("--") || argv[i + 1] === undefined) throw new Error("arguments:shape");
    result[argv[i].slice(2)] = argv[i + 1];
  }
  for (const key of ["request", "left", "right"]) if (!result[key]) throw new Error(`arguments:${key}`);
  return result;
}

const started = performance.now();
let outcome = "UnknownCommitState";
let reason = "unstarted";
let state = null;
let allowance = null;
let storedResult = null;
let projectionSha256 = null;
let leftSources = null;
let rightSources = null;
let expected = null;
let candidate = null;
try {
  const args = argumentsOf(process.argv.slice(2));
  const request = decode(readFileSync(args.request), "request");
  exactFields(request, ["profile", "expected_request", "candidate", "left_snapshot_sha256",
    "right_snapshot_sha256"], "request");
  if (request.profile !== REQUEST_PROFILE) throw new Error("request:profile");
  expected = request.expected_request;
  candidate = request.candidate;
  const left = readSnapshot(args.left, request.left_snapshot_sha256, "left");
  const right = readSnapshot(args.right, request.right_snapshot_sha256, "right");
  leftSources = left.builder_source_sha256;
  rightSources = right.builder_source_sha256;
  if (equal(leftSources, rightSources)) throw new Error("builders:provenance-not-distinct");
  const leftProjection = projection(left);
  const rightProjection = projection(right);
  const leftBytes = Buffer.from(canonical(leftProjection), "utf8");
  const rightBytes = Buffer.from(canonical(rightProjection), "utf8");
  if (!leftBytes.equals(rightBytes)) throw new Error("builders:projection-disagreement");
  projectionSha256 = sha(leftBytes);
  const checked = validateProjection(leftProjection, expected, candidate);
  outcome = checked.outcome;
  state = checked.state;
  allowance = checked.allowance;
  storedResult = checked.storedResult;
  reason = "distinct-builders-agree-on-pinned-ledger-projection";
} catch (error) {
  reason = `${error?.name ?? "Error"}: ${error?.message ?? String(error)}`;
}

const report = Object.assign(Object.create(null), {
  profile: PROFILE,
  outcome,
  reason,
  expected_request: expected,
  candidate,
  stored_result: storedResult,
  allowance,
  snapshot_state: state,
  projection_sha256: projectionSha256,
  left_builder_source_sha256: leftSources,
  right_builder_source_sha256: rightSources,
  parent_checked: false,
  debit_delta: 0,
  retry_authorized: false,
  sqlite_opened: false,
  ledger_path_accepted: false,
  work_units: work,
  meter,
  wall_nanoseconds: Math.round((performance.now() - started) * 1000000),
  process_peak_rss_kib: process.resourceUsage().maxRSS,
  runtime: `Node.js ${process.version}`,
  native_authority: false,
  close_authorized: false,
  free_authorized: false,
});
process.stdout.write(`${canonical(report)}\n`);
