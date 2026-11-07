"""Synthetic reference-verifier controls; no machine semantic authority."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from verify import Invalid, digest, load_bundle, validate


class ReferenceControls(unittest.TestCase):
    def setUp(self):
        self.raw = b'first\nsecond\n'
        self.revision = 'a'*40
        self.contract = {'machine_revision':self.revision,'source_paths':['src/a.rs'],
                         'reference_ids':['R01'], 'limits':{'source_files':1,
                         'single_source_bytes':100,'total_source_bytes':100,'references':1}}
        self.manifest = [{'path':'src/a.rs','mode':'100644','bytes':len(self.raw),'lines':2,
                         'sha256':digest(self.raw),'git_blob':hashlib.sha1(
                             b'blob '+str(len(self.raw)).encode()+b'\0'+self.raw).hexdigest()}]
        self.refs = [{'id':'R01','path':'src/a.rs','first_line':1,'last_line':1,
                     'range_sha256':digest(b'first\n'),
                     'url':f'https://github.com/mountain/adva-machine/blob/{self.revision}/src/a.rs#L1-L1'}]

    def check(self):
        return validate(self.contract,self.manifest,self.refs,lambda _:self.raw,self.revision)

    def test_valid_reference(self):
        self.assertEqual(self.check()['references'],1)

    def test_changed_source_same_size(self):
        self.raw = b'FIRST\nsecond\n'
        with self.assertRaisesRegex(Invalid,'source hash'): self.check()

    def test_truncated_source(self):
        self.raw = self.raw[:-1]
        with self.assertRaisesRegex(Invalid,'source size'): self.check()

    def test_missing_source_row(self):
        self.manifest.clear()
        with self.assertRaisesRegex(Invalid,'source roster'): self.check()

    def test_missing_reference(self):
        self.refs.clear()
        with self.assertRaisesRegex(Invalid,'reference roster'): self.check()

    def test_duplicate_reference(self):
        self.refs.append(copy.deepcopy(self.refs[0]))
        with self.assertRaisesRegex(Invalid,'reference roster'): self.check()

    def test_shifted_coordinate(self):
        self.refs[0]['first_line'] = self.refs[0]['last_line'] = 2
        with self.assertRaisesRegex(Invalid,'range hash'): self.check()

    def test_outside_scope(self):
        self.refs[0]['path'] = 'src/elsewhere.rs'
        with self.assertRaisesRegex(Invalid,'outside selected'): self.check()

    def test_wrong_revision(self):
        self.revision = 'b'*40
        with self.assertRaisesRegex(Invalid,'wrong machine'): self.check()

    def test_symlink_mode(self):
        self.manifest[0]['mode'] = '120000'
        with self.assertRaisesRegex(Invalid,'regular tracked'): self.check()

    def test_budget(self):
        self.contract['limits']['total_source_bytes'] = 1
        with self.assertRaisesRegex(Invalid,'source byte cap'): self.check()

    def test_reference_url_substitution(self):
        self.refs[0]['url'] = self.refs[0]['url'].replace(self.revision,'main')
        with self.assertRaisesRegex(Invalid,'reference URL'): self.check()

    def test_changed_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = b'{"artifact_pins":{}}\n'
            (root/'contract.json').write_bytes(raw+b' ')
            with self.assertRaisesRegex(Invalid,'contract pin'):
                load_bundle(root,digest(raw))

    def test_changed_bound_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = json.dumps({'artifact_pins':{'item.json':{'bytes':2,
                             'sha256':digest(b'{}')}}}).encode()
            (root/'contract.json').write_bytes(raw)
            (root/'item.json').write_bytes(b'[]')
            with self.assertRaisesRegex(Invalid,'bound artifact'):
                load_bundle(root,digest(raw))


if __name__ == '__main__':
    unittest.main()
