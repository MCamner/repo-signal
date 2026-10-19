"""Doctor consumes mq-agent validation, never infers a pass from structure."""
import json
import subprocess
from pathlib import Path

import pytest

from repo_signal.doctor import doctor_repo
from repo_signal.verification import verification_evidence


def receipt(status='PASS'):
    return {'schema': 'mq.verification-receipt.v1', 'status': status,
            'code_status': status, 'receipt_id': 'a' * 64,
            'fingerprint': 'b' * 64, 'head': 'c' * 40, 'base': 'c' * 40,
            'checks': [{'id': 'unit', 'status': 'PASS'}],
            'uncovered_files': [], 'runtime_data': []}


def provider(monkeypatch, payload, code=0):
    calls = []
    monkeypatch.setattr('repo_signal.verification.shutil.which', lambda _: '/tools/mq-agent')
    def run(args, **kwargs):
        calls.append(args)
        kwargs['stdout'].write(json.dumps(payload).encode())
        return subprocess.CompletedProcess(args, code)
    monkeypatch.setattr('repo_signal.verification.subprocess.run', run)
    return calls


def test_default_is_unverified_without_subprocess(monkeypatch, tmp_path):
    monkeypatch.setattr('subprocess.run', lambda *a, **k: pytest.fail('unexpected execution'))
    assert verification_evidence(tmp_path)['status'] == 'NOT_VERIFIED'


@pytest.mark.parametrize(('status', 'code', 'expected'), [
    ('PASS', 0, 'PASS'), ('FAIL', 1, 'FAIL'), ('STALE', 1, 'STALE'),
    ('MISSING', 1, 'NOT_VERIFIED'), ('NO_CHANGES', 0, 'NOT_VERIFIED'),
    ('INCOMPLETE', 1, 'NOT_VERIFIED'), ('PLAN', 0, 'NOT_VERIFIED'),
    ('ERROR', 2, 'NOT_VERIFIED')])
def test_provider_status(monkeypatch, tmp_path, status, code, expected):
    calls = provider(monkeypatch, receipt(status), code)
    result = verification_evidence(tmp_path, enabled=True)
    assert result['status'] == expected
    assert calls == [['/tools/mq-agent', 'verify-changes', str(tmp_path.resolve()),
                      '--check-receipt', '--json']]
    assert 'checks' not in result  # no raw provider body exported


@pytest.mark.parametrize('mutate', [
    lambda p: p.update(schema='unknown'), lambda p: p.update(checks=[]),
    lambda p: p.update(uncovered_files=['uncovered.py']),
    lambda p: p.update(runtime_data=[{'path': 'history.json'}]),
    lambda p: p.update(code_status='FAIL'), lambda p: p.pop('fingerprint'),
    lambda p: p.update(checks=[{'status': 'FAIL'}]),
])
def test_inconsistent_pass_is_not_trusted(monkeypatch, tmp_path, mutate):
    payload = receipt(); mutate(payload)
    provider(monkeypatch, payload)
    assert verification_evidence(tmp_path, enabled=True)['status'] == 'NOT_VERIFIED'


def test_wrong_exit_code_is_not_pass(monkeypatch, tmp_path):
    provider(monkeypatch, receipt(), 2)
    assert verification_evidence(tmp_path, enabled=True)['status'] == 'NOT_VERIFIED'


def test_absent_provider(monkeypatch, tmp_path):
    monkeypatch.setattr('repo_signal.verification.shutil.which', lambda _: None)
    assert verification_evidence(tmp_path, enabled=True)['reason'] == 'provider_unavailable'


def test_timeout_does_not_expose_output(monkeypatch, tmp_path):
    monkeypatch.setattr('repo_signal.verification.shutil.which', lambda _: '/tools/mq-agent')
    def timeout(*a, **k):
        raise subprocess.TimeoutExpired('private-command', 30, output='secret')
    monkeypatch.setattr('repo_signal.verification.subprocess.run', timeout)
    result = verification_evidence(tmp_path, enabled=True)
    assert result['status'] == 'NOT_VERIFIED'
    assert 'secret' not in json.dumps(result)


def test_doctor_scores_stay_static_and_formats_separate_verification(tmp_path):
    default = json.loads(doctor_repo(tmp_path, output_format='json'))
    assert default['schema'] == 'doctor.v1'
    assert default['verification']['status'] == 'NOT_VERIFIED'
    markdown = doctor_repo(tmp_path)
    assert 'Structural scores' in markdown
    assert 'NOT_VERIFIED' in markdown


def test_cli_flag_accepts_json(tmp_path):
    import sys
    result = subprocess.run([sys.executable, '-m', 'repo_signal.cli', 'doctor',
                             str(tmp_path), '--verification', '--json'],
                            capture_output=True, text=True, env={**__import__('os').environ, 'PATH': ''})
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['verification']['status'] == 'NOT_VERIFIED'


@pytest.mark.parametrize('raw', [b'not-json', b'[]', b'x' * 65537])
def test_invalid_or_oversized_json(monkeypatch, tmp_path, raw):
    monkeypatch.setattr('repo_signal.verification.shutil.which', lambda _: '/tools/mq-agent')
    def run(args, **kwargs):
        kwargs['stdout'].write(raw)
        return subprocess.CompletedProcess(args, 0)
    monkeypatch.setattr('repo_signal.verification.subprocess.run', run)
    assert verification_evidence(tmp_path, enabled=True)['status'] == 'NOT_VERIFIED'


def test_opt_in_does_not_change_structure_scores(monkeypatch, tmp_path):
    baseline = json.loads(doctor_repo(tmp_path, output_format='json'))
    monkeypatch.setattr('repo_signal.doctor.verification_evidence',
                        lambda *a, **kw: {'status': 'FAIL', 'reason': 'fail'})
    verified = json.loads(doctor_repo(tmp_path, output_format='json', verification=True))
    assert verified['scores'] == baseline['scores']
    assert verified['verification']['status'] == 'FAIL'
