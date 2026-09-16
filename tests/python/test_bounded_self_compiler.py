"""Independent receiving of frozen compiler evidence, without a new campaign."""
from pathlib import Path
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]

@pytest.mark.parametrize('check',['sources','stages','fixtures','lineage','fresh'])
def test_frozen_self_compiler_receiving(check):
    result=subprocess.run([sys.executable,'-B',str(ROOT/'experiments/bounded_self_compiler/regression.py'),check],
                          cwd=ROOT,capture_output=True,text=True,timeout=90)
    assert result.returncode==0,result.stdout+result.stderr
