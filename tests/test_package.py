"""Release gates must reject corrupted archives and wrong public-API assertions."""
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
import warnings
import shutil
import json

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import package_candidate as package
import check_consumer as consumer


class ReleaseGates(unittest.TestCase):
    def test_escaping_archive_rejected_before_extract(self):
        for name in ['../outside', '/absolute', 'nested/../../outside', 'dir\\escape']:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as d:
                path=Path(d)/'bad.zip'
                with zipfile.ZipFile(path,'w') as z:z.writestr(name,b'x')
                with self.assertRaises(ValueError):package.archive_members(path)

    def test_symlink_archive_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.zip'
            info=zipfile.ZipInfo('link');info.external_attr=(0o120777 << 16)
            with zipfile.ZipFile(path,'w') as z:z.writestr(info,b'outside')
            with self.assertRaises(ValueError):package.archive_members(path)

    def test_duplicate_archive_member_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.zip'
            with warnings.catch_warnings():
                warnings.simplefilter('ignore',UserWarning)
                with zipfile.ZipFile(path,'w') as z:
                    z.writestr('same',b'first');z.writestr('same',b'second')
            with self.assertRaises(ValueError):package.archive_members(path)

    def test_report_decoder_preserves_protocol_rejections(self):
        from release_support import machine_report
        for raw in [b'{"ok":true}',b'{"ok":true}\r\n',b'{"ok":true}\n\n',
                    b'{"ok":true,"ok":true}\n',b'{"x":NaN}\n',b'{"x":1e999}\n',
                    b'{"x":"\\ud800"}\n']:
            with self.subTest(raw=raw),self.assertRaises((ValueError,UnicodeError)):machine_report(raw)

    def test_package_requires_runtime_and_excludes_private_files(self):
        good=package.expected_files(ROOT)
        self.assertIn('cmd/mooneventeval/io_stub.c',good)
        self.assertIn('docs/API.md',good)
        self.assertNotIn('cmd/probe/main.mbt',good)
        for bad in ['.tools/secret','evidence/log','docs/PROJECT_STATE.md','spikes/T0/probe.mbt']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):package.validate_members(set(good)|{bad},good)
        with self.assertRaises(ValueError):package.validate_members(set(good)-{'cmd/mooneventeval/io_stub.c'},good)

    def test_failed_explanation_never_qualifies_package(self):
        # Compile an actual serializer mutation through the complete archive gate.
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'source';source.mkdir()
            for name in package.expected_files(ROOT)|{'.moonignore'}:
                target=source/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/name,target)
            path=source/'eventeval/report_json.mbt';original=path.read_text()
            before,body=original.split('pub fn explanation_json(',1)
            needle='("status", "\\\"completed\\\"")'
            replacement='("status", "\\\"failed\\\"")'
            self.assertEqual(body.count(needle),1)
            path.write_text(before+'pub fn explanation_json('+body.replace(needle,replacement,1))
            output=Path(directory)/'gate'
            report=package.package(source,output)
            self.assertEqual(report['cli_build']['exit_code'],0)
            actual=json.loads((output/'unpacked-examples/explain/stdout').read_bytes())
            self.assertEqual(actual['status'],'failed')
            self.assertTrue(report['consumer']['passed'])
            self.assertFalse(report['examples']['passed'])
            self.assertFalse(report['passed'])

    def test_public_consumer_wrong_expected_count_fails(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'run'
            template=(ROOT/'tests/consumer/main/main.mbt').read_text().replace('counts.tp == 1','counts.tp == 2')
            report=consumer.check(ROOT,out,main_text=template)
            self.assertFalse(report['passed'])
            self.assertNotEqual(report['run']['exit_code'],0)
            self.assertEqual(report['build']['exit_code'],0)
            self.assertTrue((out/'run/stdout').is_file())

    def test_consumer_source_must_be_module(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):consumer.check(Path(d),Path(d)/'out')


if __name__=='__main__':unittest.main()
