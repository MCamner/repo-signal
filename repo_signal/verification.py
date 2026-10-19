"""Read-only adapter: mq-agent owns verification and validates its own receipts."""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any

SCHEMA = 'mq.verification-receipt.v1'
MAX_BYTES = 65536


def verification_evidence(repo_path: Path, *, enabled: bool = False) -> dict[str, Any]:
    """Consume a validated HEAD-based receipt; never run checks or trust file presence."""
    result: dict[str, Any] = {
        'status': 'NOT_VERIFIED', 'source': 'mq-agent', 'reason': 'not_requested',
        'scope': 'changed_files_against_HEAD', 'code_status': None,
        'receipt_id': None, 'fingerprint': None, 'head': None, 'base': None,
        'next_action': 'Run doctor --verification to validate existing local evidence.',
    }
    if not enabled:
        return result
    executable = shutil.which('mq-agent')
    if not executable:
        return {**result, 'reason': 'provider_unavailable',
                'next_action': 'Install mq-agent with verify-changes support, then retry.'}
    try:
        # Bound captured output and discard stderr: neither raw errors nor receipt
        # bodies (which may include private paths) belong in an exported report.
        with tempfile.TemporaryFile() as output:
            proc = subprocess.run(
                [executable, 'verify-changes', str(repo_path.resolve()), '--check-receipt', '--json'],
                stdout=output, stderr=subprocess.DEVNULL, timeout=30, check=False,
            )
            output.seek(0)
            raw = output.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('oversized response')
        payload = json.loads(raw)
    except (OSError, subprocess.TimeoutExpired, ValueError, UnicodeError):
        return {**result, 'reason': 'provider_error',
                'next_action': 'Check mq-agent availability and receipt validity locally.'}
    if not isinstance(payload, dict) or payload.get('schema') != SCHEMA:
        return {**result, 'reason': 'invalid_provider_response'}
    status = payload.get('status')
    if status not in {'PASS', 'FAIL', 'STALE', 'MISSING', 'NO_CHANGES', 'INCOMPLETE', 'PLAN', 'ERROR'}:
        return {**result, 'reason': 'invalid_provider_response'}
    expected_code = 0 if status in {'PASS', 'NO_CHANGES', 'PLAN'} else 2 if status == 'ERROR' else 1
    if proc.returncode != expected_code:
        return {**result, 'reason': 'invalid_provider_response'}
    if status in {'MISSING', 'ERROR', 'PLAN'}:
        return {**result, 'reason': status.lower(),
                'next_action': 'Review the verification plan in mq-agent before running checks.'}
    # The producer validates freshness/checksum. Validate the summary shape here,
    # without reimplementing fingerprint calculation or echoing untrusted strings.
    for field, pattern in [('receipt_id', r'[0-9a-f]{64}'), ('fingerprint', r'[0-9a-f]{64}'),
                           ('head', r'[0-9a-f]{40,64}'), ('base', r'[0-9a-f]{40,64}')]:
        value = payload.get(field)
        if not isinstance(value, str) or not re.fullmatch(pattern, value):
            return {**result, 'reason': 'invalid_provider_response'}
    checks = payload.get('checks')
    uncovered = payload.get('uncovered_files')
    runtime = payload.get('runtime_data', [])
    code_status = payload.get('code_status')
    if (not isinstance(checks, list) or not all(isinstance(c, dict) for c in checks)
            or not isinstance(uncovered, list) or not isinstance(runtime, list)
            or code_status not in {'PASS', 'FAIL', 'STALE', 'INCOMPLETE', 'NO_CHANGES'}):
        return {**result, 'reason': 'invalid_provider_response'}
    if status == 'PASS' and (code_status != 'PASS' or not checks or uncovered or runtime
                             or any(c.get('status') != 'PASS' for c in checks)):
        return {**result, 'reason': 'invalid_provider_response'}
    result.update({key: payload[key] for key in ('receipt_id', 'fingerprint', 'head', 'base')})
    result.update(code_status=code_status, reason=status.lower(),
                  status=status if status in {'PASS', 'FAIL', 'STALE'} else 'NOT_VERIFIED',
                  next_action='Review uncovered scope and evidence in mq-agent before release.')
    if status == 'PASS':
        result['next_action'] = 'Review remaining release requirements; this is changed-file evidence only.'
    return result
