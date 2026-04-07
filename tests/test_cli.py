from __future__ import annotations

import json

from xlodit.cli import main


def test_cli_json_exit_code_success(fixture_dir, capsys) -> None:
    code = main(
        [str(fixture_dir / "valid.xlsx"), "--backend", "none", "--format", "json"]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["audit_completed"] is True


def test_cli_json_exit_code_with_errors(fixture_dir, capsys) -> None:
    code = main(
        [
            str(fixture_dir / "formula_error_simple.xlsx"),
            "--backend",
            "none",
            "--format",
            "json",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 1
    assert payload["summary"]["errors"] > 0


def test_cli_exit_code_runtime_failure(tmp_path, capsys) -> None:
    bad = tmp_path / "file.csv"
    bad.write_text("x", encoding="utf-8")
    code = main([str(bad), "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["audit_completed"] is False
