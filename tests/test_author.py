import io
import os
import random
import re
import subprocess
import sys
from pathlib import Path

import author
import pytest

ROOT = Path(__file__).resolve().parent.parent
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

# Importing main.py's dependencies starts the file log and loads the LM Studio model.
HEAVY = {"config", "utils", "utils.logger", "utils.llm_manager", "loguru", "lmstudio", "openpyxl"}


def run_main(*args: str, cwd: Path) -> tuple[subprocess.CompletedProcess, set[str]]:
    """Run main.py as a script; also return every module the run imported."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1"}
    result = subprocess.run(
        [sys.executable, "-X", "importtime", str(ROOT / "main.py"), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,  # a regression would reach the model load, which can wait on LM Studio
    )
    imported = {
        line.rsplit("|", 1)[1].strip()
        for line in result.stderr.splitlines()
        if line.startswith("import time:") and "|" in line
    }
    return result, imported


def test_plain_card_when_not_a_console():
    out = io.StringIO()
    assert author.show(out) == 0
    text = out.getvalue()
    assert text.isascii()
    assert "\x1b" not in text
    for line in author.QUOTE:
        assert line in text
    assert author.NAME in text and author.BY in text


@pytest.mark.parametrize("render", [author.big, author.compact])
def test_finished_card_is_a_closed_box_with_the_exact_quote(render):
    card = author.Card(render, random.Random(1))
    lines = [ANSI.sub("", line) for line in card.lines(author.END + 1)]
    assert len(lines) == card.height
    assert {len(line) for line in lines} == {card.width}
    assert lines[0].startswith("╭") and lines[-1].endswith("╯")
    body = "\n".join(lines)
    for line in author.QUOTE:
        assert line in body
    assert f"— {author.BY}" in body
    assert author.NAME in body


def test_every_frame_keeps_the_box_width():
    card = author.Card(author.compact, random.Random(2))
    for step in range(0, 45):
        lines = [ANSI.sub("", line) for line in card.lines(step / 10)]
        assert {len(line) for line in lines} == {card.width}


def test_author_needs_no_config_and_writes_no_log(tmp_path):
    for args in (["--author"], ["--anything", "--author"]):
        result, imported = run_main(*args, cwd=tmp_path)
        assert result.returncode == 0, result.stderr[-2000:]
        assert author.NAME in result.stdout
        assert not imported & HEAVY  # no config, no logger, no model
    assert list(tmp_path.iterdir()) == []  # no log file, nothing


def test_help_hints_at_author_without_explaining_it(tmp_path):
    result, imported = run_main("--help", cwd=tmp_path)
    assert result.returncode == 0, result.stderr[-2000:]
    text = result.stdout
    assert "--author" in text and "who built this" in text
    assert author.NAME not in text  # only a hint: the name shows when you try it
    assert not imported & HEAVY  # --help never starts the run or loads the model
