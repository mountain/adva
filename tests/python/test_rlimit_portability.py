"""Engineering checks: mock Darwin API rejection, never claim Darwin execution."""
import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'experiments/rlimit_portability'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


replay = load('portable_replay', HERE / 'replay.py')
audit = load('rlimit_audit', HERE / 'audit.py')


class Resource:
    RLIMIT_AS, RLIMIT_CPU, RLIMIT_FSIZE, RLIMIT_CORE = 'AS', 'CPU', 'FSIZE', 'CORE'
    RLIM_INFINITY = -1

    def __init__(self, fail=None, existing=(-1, -1)):
        self.calls, self.fail, self.existing = [], fail, existing

    def getrlimit(self, kind):
        return self.existing

    def setrlimit(self, kind, value):
        self.calls.append((kind, value))
        if kind == self.fail:
            raise ValueError('current limit exceeds maximum limit')


class PortabilityTests(unittest.TestCase):
    def test_darwin_skips_as_but_keeps_other_limits(self):
        api = Resource(fail='AS')
        result = replay.install_limits('darwin', api)
        self.assertEqual([x[0] for x in api.calls], ['CPU', 'FSIZE', 'CORE'])
        self.assertEqual(result['RLIMIT_AS']['status'], 'not-installed')

    def test_linux_failure_is_not_swallowed(self):
        api = Resource(fail='AS')
        with self.assertRaises(ValueError):
            replay.install_limits('linux', api)
        self.assertEqual(api.calls[-1], ('AS', (256*1024**2,)*2))

    def test_mandatory_limits_and_inherited_caps(self):
        for host in ('linux', 'darwin'):
            for kind in ('CPU', 'FSIZE', 'CORE'):
                with self.subTest(host=host, kind=kind), self.assertRaises(ValueError):
                    replay.install_limits(host, Resource(fail=kind))
        api = Resource(existing=(2, 4))
        replay.install_limits('linux', api)
        self.assertTrue(all(max(pair) <= 2 for _, pair in api.calls))
        with self.assertRaises(ValueError):
            replay.install_limits('freebsd', Resource())

    def test_inventory_and_pins(self):
        self.assertEqual(audit.inventory(), json.loads((HERE/'inventory.json').read_bytes()))
        replay.checked_inputs()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in json.loads((HERE/'contract.json').read_bytes())['inputs']:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT/name).read_bytes())
            path.write_bytes(path.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                replay.checked_inputs(root)

    def test_legacy_failure_at_exact_limit_functions(self):
        # Execute only the original function AST, no research trial or real setrlimit.
        for path, name, extra in [
            ('experiments/decision_scale/run.py', 'limits', {}),
            ('python/adva/verifier_search.py', 'child_limits', {'FILE_LIMIT': 1048576}),
            ('python/adva/adva.py', '_limits', {'OUTPUT_LIMIT': 262144}),
        ]:
            with self.subTest(path=path):
                tree = ast.parse((ROOT/path).read_bytes())
                fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
                namespace = {'resource': Resource(fail='AS'), **extra}
                exec(compile(ast.Module(body=[fn], type_ignores=[]), path, 'exec'), namespace)
                with self.assertRaisesRegex(ValueError, 'current limit'):
                    namespace[name]()
        # adva._limits fails in isolation, but its production prime_check gate prevents it.

    def test_existing_entry_guards_do_not_spawn_on_darwin(self):
        operator = load('operator_for_portability', ROOT/'python/adva/operator_receipt.py')
        with patch.object(operator.sys, 'platform', 'darwin'), patch.object(operator.subprocess, 'Popen') as spawn:
            result = operator.run('missing-question', 'missing-receipt')
            self.assertEqual(result['status'], 'BackendUnavailable')
            spawn.assert_not_called()
        adapter = load('adapter_for_portability', ROOT/'python/adva/adva.py')
        with patch.object(adapter.sys, 'platform', 'darwin'), patch.object(adapter, '_read', return_value=b'{}'), patch.object(adapter, '_request', return_value={}), patch.object(adapter.shutil, 'which', return_value='/unused/backend'), patch.object(adapter.subprocess, 'Popen') as spawn:
            self.assertEqual(adapter.prime_check('unused', 'unused')['status'], 'BackendUnavailable')
            spawn.assert_not_called()

    def test_verifier_supervisor_has_reachable_preexec_failure(self):
        verifier = load('verifier_for_portability', ROOT/'python/adva/verifier_search.py')
        def popen(*args, **kwargs):
            try:
                kwargs['preexec_fn']()
            except ValueError as error:
                raise subprocess.SubprocessError('Exception occurred in preexec_fn.') from error
            self.fail('limit refusal was swallowed')
        with tempfile.TemporaryDirectory() as directory:
            supervisor = verifier.Supervisor(Path(directory)/'fresh')
            with patch.object(verifier, 'resource', Resource(fail='AS')):
                # call also measures rusage; supply only the inert observation needed here.
                verifier.resource.RUSAGE_CHILDREN = 0
                verifier.resource.getrusage = lambda _: SimpleNamespace()
                with patch.object(verifier.subprocess, 'Popen', side_effect=popen), self.assertRaises(subprocess.SubprocessError):
                    supervisor.call('probe', ['/unused/backend'])

    def test_payload_mutation_detected(self):
        frozen = json.loads((ROOT/'experiments/frame_covariance/evidence.json').read_bytes())
        altered = json.loads(json.dumps(frozen))
        altered['rows'][0]['frame'] = 'wrong'
        self.assertNotEqual(replay.payload(frozen), replay.payload(altered))
        altered = dict(frozen, costs={'changed': True}, python='other')
        self.assertEqual(replay.payload(frozen), replay.payload(altered))

    def test_retained_linux_replay_is_bound_to_current_sources(self):
        directory = HERE / 'linux-run-01'
        report = json.loads((directory/'replay.json').read_bytes())
        execution = json.loads((directory/'execution.json').read_bytes())
        self.assertEqual(report['runner_sha256'], replay.digest((HERE/'replay.py').read_bytes()))
        self.assertEqual(report['profile_sha256'], replay.digest((HERE/'contract.json').read_bytes()))
        self.assertEqual(report['input_sha256'], json.loads((HERE/'contract.json').read_bytes())['inputs'])
        for name in ('replay.json', 'stderr.txt'):
            self.assertEqual(execution[name+'_sha256'], replay.digest((directory/name).read_bytes()))
        frozen = json.loads((ROOT/'experiments/frame_covariance/evidence.json').read_bytes())
        self.assertEqual(report['payload_sha256'], replay.digest(json.dumps(replay.payload(frozen), sort_keys=True).encode()))
        self.assertEqual((report['rows'], report['controls'], report['logical_checks']), (84, 7, 1615))
        self.assertFalse(report['original_resource_contract_claim'])
        self.assertFalse(execution['darwin_execution'])
        self.assertEqual(execution['status'], 'Completed')

    def test_fresh_output_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            sentinel = Path(directory)/'sentinel'
            sentinel.write_text('keep')
            result = subprocess.run([sys.executable, str(HERE/'replay.py'), '--output', directory], capture_output=True, timeout=5)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(Path(directory).iterdir()), [sentinel])
            self.assertEqual(sentinel.read_text(), 'keep')
